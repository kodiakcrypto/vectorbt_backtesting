import streamlit as st
import pandas_ta as ta
import inspect
from pandas_ta_utils import list_ind
from strategy import calc_ind, backtest
from candle_fetcher import get_candles
import xlsxwriter
from io import BytesIO
import numpy as np

# >, <, etc... string to operation on datasets
def operator_to_operation(data1, data2, comparison_operator):
    if comparison_operator == '>':
        data = data1.gt(data2)
    elif comparison_operator == '<':
        data = data1.lt(data2)
    elif comparison_operator == '>=':
        data = data1.ge(data2)
    elif comparison_operator == '<=':
        data = data1.le(data2)
    elif comparison_operator == '-':
        data = data1.subtract(data2)
    elif comparison_operator == '+':
        data = data1.add(data2)
    elif comparison_operator == '*':
        data = data1.multiply(data2)
    elif comparison_operator == '/':
        data = data1.divide(data2)
    return data

# Entry input boxes
def add_entry_boxes(clean_columns, i):
    entry_column1 = st.selectbox('Column #1', clean_columns, key='entry_column1_'+str(i))
    entry_comparison = st.selectbox('Comparison', ['>', '<', '>=', '<=', '-', '+','*','/'], key='entry_comparison_'+str(i))
    entry_column2 = st.selectbox('Column #2', clean_columns, key='entry_column2_'+str(i))
    if i > 1:
        entry_combiner = st.radio('Combine with', ['AND', 'OR'], key='entry_combiner_'+str(i))
        return entry_column1, entry_comparison, entry_column2, entry_combiner
    else:
        return entry_column1, entry_comparison, entry_column2, None
def increment_entries():
    st.session_state.entries += 1
def remove_entry_box():
    st.session_state['entries'] -= 1

# Exit input boxes
def add_exit_boxes(clean_columns, i):
    exit_column1 = st.selectbox('Column #1', clean_columns, key='exit_column1_'+str(i))
    exit_comparison = st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'], key='exit_comparison_'+str(i))
    exit_column2 = st.selectbox('Column #2', clean_columns, key='exit_column2_'+str(i))
    if i > 1:
        exit_combiner = st.radio('Combine with', ['AND', 'OR'], key='exit_combiner_'+str(i))
        return exit_column1, exit_comparison, exit_column2, exit_combiner
    else:
        return exit_column1, exit_comparison, exit_column2, None
def increment_exits():
    st.session_state.exits += 1
def remove_exit_box():
    st.session_state['exits'] -= 1

def main():
    st.header("Data Downloader")
    col1, col2 = st.columns([2, 3])


    ##########################
    # Default variable inits #
    ##########################
    if 'expanded' not in st.session_state:
        st.session_state['expanded'] = False
    if 'entries' not in st.session_state:
        st.session_state['entries'] = 0
        st.session_state['all_entries'] = []
    if 'exits' not in st.session_state:
        st.session_state['exits'] = 0
        st.session_state['all_exits'] = []
    if 'separate_panel_indicators' not in st.session_state:
        st.session_state['separate_panel_indicators'] = []
    

    ###############################
    # Plot Chart if Backtest Done #
    ###############################
    if 'portfolio' in st.session_state:
        try:
            st.plotly_chart(st.session_state.portfolio.plot())
            st.write(st.session_state.portfolio.stats())
        except:
            st.write("# Try Again, Backtest Data Missing")


    #################
    # Data Fetching #
    #################
    with col1:
        ticker = st.text_input("Ticker", "BTC-USD")
        amount_of_candles = st.number_input("Amount of candles", 100, 100000, 1000)
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"], index=3)

        # List of all indicators
        indicators = list_ind()
        select_ind = st.multiselect("Choose indicators to apply to data", indicators)
        
        args_dicts = {} #multi indicator
        ind_functions = [getattr(ta, ind) for ind in select_ind]
        if len(ind_functions) > 0: 
            st.write("### Indicator Params")
            st.write("ignore 0 and blank boxes to use a default value:")

        #list indicator parameter boxes
        for ind_function in ind_functions:
            st.sidebar.write(f"# {ind_function.__name__.title()} Info")
            st.sidebar.write(ind_function.__doc__)
            #add separator
            st.sidebar.write("\n# ===========\n")

            st.write(f"\n## {ind_function.__name__.title()}")
            args = inspect.getfullargspec(ind_function).args #get all params needed
            args_dict = {}
            for argument in args:
                param_box = f"{argument}input" #name the input box
                # toggle type of input according to variable. Data will be automatically added, no need to enter infos
                input_box_unique_id = ind_function.__name__+'_'+argument
                data_set = {"open_", "high", "low", "close", "volume"}
                text_set = {"mamode"}

                if argument == "talib": param_box = False
                elif argument == 'offset': param_box = 0
                elif argument in text_set: param_box = st.text_input(argument, key=input_box_unique_id)
                elif argument not in data_set: param_box = st.number_input(argument, step=1, key=input_box_unique_id)

                args_dict[argument] = param_box
            args_dicts[ind_function.__name__] = args_dict #multi indicator

        if st.button("Go Go Go"):
            (st.session_state['candle_dataframe'], st.session_state['indicator_dict']) = calc_ind(get_candles(ticker, timeframe, amount_of_candles), args_dicts)


    #######################################
    # Plot dataframe and Download buttons #
    #######################################
    if 'candle_dataframe' in st.session_state:
        with col2:
            filename = f"{ticker}_{timeframe}_{amount_of_candles}_candles"

            candle_dataframe = st.session_state['candle_dataframe']
            st.write(candle_dataframe)

            st.download_button(
                label="⬇️ CSV",
                data=candle_dataframe.to_csv().encode("utf-8"),
                file_name=f"{filename}.csv",
                mime="text/csv",
                help="Download CSV file",
                key="csv",
            )

            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            worksheet = workbook.add_worksheet()

            worksheet.write('A1', filename)
            workbook.close()

            st.download_button(
                label="⬇️ XLSX",
                data=output.getvalue(),
                file_name=f"{filename}.xlsx",
                mime="application/vnd.ms-excel",
                help="Download XLSX Excel file",
                key="xlsx",
            )


            #####################
            # BACKTEST DROPDOWN #
            #####################
            backtest_boxes = st.expander('Backtest Options', expanded=st.session_state['expanded'])
            with backtest_boxes:
                st.session_state['expanded'] = True

                ####################
                # Stoploss TP Zone #
                ####################
                long_short_both = st.selectbox('Long/Short/Both', ['long', 'short', 'both'], index=0, key='long_short_both')
                amount_of_candles = st.number_input('# of Candles on chart', value=1000, min_value=1, max_value=10000, step=1, key='amount_of_candles')

                st.write('#### Stop Loss/Take Profit/Trailing Stop')
                sl_start = st.number_input('SL Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_start', format="%.3f")
                sl_end = st.number_input('SL End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_end', format="%.3f")
                sl_increment = st.number_input('SL Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_increment', format="%.3f")

                tp_start = st.number_input('TP Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp_start', format="%.3f")
                tp_end = st.number_input('TP End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp_end', format="%.3f")
                tp_increment = st.number_input('TP Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp', format="%.3f")

                trail_start = st.number_input('Trail Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_start', format="%.3f")
                trail_end = st.number_input('Trail End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_end', format="%.3f")
                trail_increment = st.number_input('Trail Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_increment', format="%.3f")
                

                ##################################################
                # Choose Columns to plot separately and together #
                ##################################################
                clean_columns = [column for column in candle_dataframe.columns \
                    if column not in ['entries', 'exits'] \
                        and type(candle_dataframe[column].iloc[-1]) == np.float64]
                st.write('Select the columns from 1 indicator like ATR and RSI to plot below the chart')
                columns = st.multiselect('Column Names', clean_columns, key='clean_cols')
                if st.button('Submit Group as indicator'):
                    # check each chosen column against dict toget indicator name
                    name_array = []
                    for ind_name, ind_columns in st.session_state.indicator_dict.items():
                        for column in columns:
                            if column in ind_columns and column not in name_array:
                                name_array.append(ind_name)

                    indicator_dataframe = candle_dataframe[[x for x in columns]]
                    indicator_dataframe.name = '_'.join(name_array)
                    st.session_state.separate_panel_indicators.append(indicator_dataframe)
                    columns.clear()
                    




                ####################
                # ENTRY CONDITIONS #
                ####################
                #select column to use for backtest
                st.write('#### Entry Conditions')
                st.button('+', key='add_entry_condition', on_click=increment_entries)
                st.button('-', key='remove_entry_condition', on_click=remove_entry_box)
                
                # st.write(type(st.session_state.entries),st.session_state.entries)
                # if st.session_state.entries == []:
                    
                st.session_state.all_entries = []
                for i in range(st.session_state.entries):
                    (backtest_column1, comparison_operator, backtest_column2, combination_operator) = add_entry_boxes(clean_columns, i)
                    st.session_state.all_entries.append([backtest_column1, comparison_operator, backtest_column2, combination_operator])
                
                ###################
                # EXIT CONDITIONS #
                ###################
                st.write('#### Exit Conditions')
                st.button('+', key='add_exit_condition', on_click=increment_exits)
                st.button('-', key='remove_exit_condition', on_click=remove_exit_box)
                
                st.session_state.all_exits = []
                for i in range(st.session_state.exits):
                    (backtest_column1, comparison_operator, backtest_column2, combination_operator) = add_exit_boxes(clean_columns, i)
                    st.session_state.all_exits.append([backtest_column1, comparison_operator, backtest_column2, combination_operator])
                   


                #################
                # BACKTEST ZONE #
                #################
                if st.button('Run Backtest'):
                    for i in range(st.session_state.entries):
                        entries = operator_to_operation(candle_dataframe[backtest_column1], 
                                                        candle_dataframe[backtest_column2], 
                                                        comparison_operator)
                        entries.name = f"{backtest_column1}_{comparison_operator}_{backtest_column2}"

                        candle_dataframe['entries'] = entries
                        st.write(candle_dataframe)

                        combination_operator = st.session_state.all_entries[i][3]
                        if combination_operator == 'AND':
                            candle_dataframe['entries'] = np.bitwise_and(candle_dataframe['entries'] & st.session_state['all_entries'][i])
                        elif combination_operator == 'OR':
                            candle_dataframe['entries'] = np.bitwise_or(candle_dataframe['entries'] | st.session_state['all_entries'][i])
                        

                    for i in range(st.session_state.exits):
                        exits = operator_to_operation(candle_dataframe[backtest_column1], 
                                                    candle_dataframe[backtest_column2], 
                                                    comparison_operator)
                        exits.name = f"{backtest_column1}_{comparison_operator}_{backtest_column2}"
                        
                        candle_dataframe['exits'] = exits
                        combination_operator = st.session_state.all_exits[i][3]
                        if combination_operator == 'AND':
                            candle_dataframe['exits'] = np.bitwise_and(candle_dataframe['exits'] , st.session_state['all_exits'][i])
                        elif combination_operator == 'OR':
                            candle_dataframe['exits'] = np.bitwise_or(candle_dataframe['exits'] | st.session_state['all_exits'][i])
 

                    backtest(
                        candle_dataframe, 
                        st.session_state.separate_panel_indicators,
                        entries, exits, 
                        timeframe, long_short_both,
                        amount_of_candles=amount_of_candles,
                        sl_start=sl_start, sl_end=sl_end, sl_increment=sl_increment,
                        tp_start=tp_start, tp_end=tp_end, tp_increment=tp_increment,
                        trail_start=trail_start, trail_end=trail_end, trail_increment=trail_increment
                    )

            


