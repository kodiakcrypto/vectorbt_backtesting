import streamlit as st
import pandas_ta as ta
import inspect
from pandas_ta_utils import list_ind
from strategy import calc_ind, backtest
from candle_fetcher import get_candles
import xlsxwriter
from io import BytesIO
import pandas as pd
import numpy as np
from random import randint

def operator_to_operation(data1, data2, comparison_operator):
    if comparison_operator == '>':
        data = np.greater(data1, data2)
    elif comparison_operator == '<':
        data = np.less(data1, data2)
    elif comparison_operator == '>=':
        data = np.greater_equal(data1, data2)
    elif comparison_operator == '<=':
        data = np.less_equal(data1, data2)
    elif comparison_operator == '==':
        data = np.equal(data1, data2)
    elif comparison_operator == '-':
        data = data1 - data2
    elif comparison_operator == '+':
        data = data1 + data2
    elif comparison_operator == '*':
        data = data1 * data2
    elif comparison_operator == '/':
        data = data1 / data2
    return data

def add_entry_boxes(clean_columns):
    st.session_state['entries'].append([
            st.selectbox('Column #1', clean_columns, key=str(randint(0,999999))), \
            st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'], key=str(randint(0,999999))), \
            st.selectbox('Column #2', clean_columns, key=str(randint(0,999999)))
    ])
    if len(st.session_state.entries) > 1:
        st.session_state['entries'][-1].append(st.radio('Combine with', ['AND', 'OR'], key=str(randint(0,999999))))

def remove_entry_box():
    st.session_state['entries'].remove(-1)

def add_exit_boxes(clean_columns):
    st.session_state['exits'].append([
        st.selectbox('Column #1', clean_columns, key=str(randint(0,999999))), \
        st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'], key=str(randint(0,999999))), \
        st.selectbox('Column #2', clean_columns, key=str(randint(0,999999)))
    ])
    if len(st.session_state.exits) > 1:
        st.session_state['exits'][-1].append(st.radio('Combine with', ['AND', 'OR'], key=str(randint(0,999999))))
def remove_exit_box():
    st.session_state['exits'].remove(-1)

def main():
    if 'expanded' not in st.session_state:
        st.session_state.expanded = False
    if 'entries' not in st.session_state:
        st.session_state.entries = []
    if 'exits' not in st.session_state:
        st.session_state.exits = []
    
    st.header("Data Downloader")
    col1, col2 = st.columns([2, 3])

    if 'portfolio' in st.session_state:
        try:
            st.plotly_chart(st.session_state.portfolio.plot())
            st.write(st.session_state.portfolio.stats())
        except:
            st.write("# Try Again, Backtest Data Missing")

    with col1:
        # ticker
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
            st.write("(leave unchanged to use defaults):")

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
            st.session_state['candle_dataframe'] = calc_ind(get_candles(ticker, timeframe, amount_of_candles), args_dicts)

    # plot data
    if 'candle_dataframe' in st.session_state:
        with col2:
            filename = f"{ticker}_{timeframe}_{amount_of_candles}_candles"

            candle_dataframe = st.session_state['candle_dataframe']
            clean_columns = [column for column in candle_dataframe.columns \
                                if column not in ['entries', 'exits'] \
                                    and type(candle_dataframe[column].iloc[-1]) == np.float64]
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

            backtest_boxes = st.expander('Backtest Options', expanded=st.session_state['expanded'])
            with backtest_boxes:
                st.session_state['expanded'] = True

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
                
                # add multi select box to choose dataframe columns to use
                st.write('Select the columns like ATR and RSI to plot below the chart')
                columns = st.multiselect('Column Names', clean_columns, key='clean_cols')
                separate_panel_indicators = candle_dataframe[columns]





                #select column to use for backtest
                st.write('#### Entry Conditions')
                st.button('# +', key='add_entry_condition', onclick=add_entry_boxes, args=(clean_columns)):
                st.button('# -', key='remove_entry_condition', onclick=remove_entry_box)
                
                if len(st.session_state.entries == 0):
                    add_entry_boxes(clean_columns)

                for i in range(len(st.session_state.entries)):
                    backtest_column1 = st.session_state.entries[i][0]
                    comparison_operator = st.session_state.entries[i][1]
                    backtest_column2 = st.session_state.entries[i][2]

                   
                    entry_string = f"{backtest_column1} {comparison_operator} {backtest_column2}"
                    entries = operator_to_operation(candle_dataframe[backtest_column1], 
                                                    candle_dataframe[backtest_column2], 
                                                    comparison_operator)
                    entries = entries.rename(entry_string)
                    st.session_state.all_entries[i] = entries


                st.write('#### Exit Conditions')
                st.button('# +', key='add_exit_condition', onclick=add_exit_boxes, args=(clean_columns)):
                st.button('# -', key='remove_exit_condition', onclick=remove_exit_box)
                
                if len(st.session_state.exits == 0):
                    add_exit_boxes(clean_columns)

                for i in range(len(st.session_state.exits)):
                    backtest_column1 = st.session_state.exits[i][0]
                    comparison_operator = st.session_state.exits[i][1]
                    backtest_column2 = st.session_state.exits[i][2]

                   
                    exit_string = f"{backtest_column1} {comparison_operator} {backtest_column2}"
                    exits = operator_to_operation(candle_dataframe[backtest_column1], 
                                                  candle_dataframe[backtest_column2], 
                                                  comparison_operator)
                    exits = exits.rename(entry_string)
                    st.session_state.all_exits[i] = exits





                if st.button('Run Backtest'):

                    candle_dataframe['entries'] = st.session_state.all_entries[0]
                    for i in range(len(st.session_state.entries)):
                        if len(st.session_state.entries[i]) == 4:
                            combination_operator = st.session_state.entries[i][3]
                            if combination_operator == 'AND':
                                candle_dataframe['entries'] = (candle_dataframe['entries'] & st.session_state.all_entries[i])
                            elif combination_operator == 'OR':
                                candle_dataframe['entries'] = (candle_dataframe['entries'] | st.session_state.all_entries[i])
                    
                    candle_dataframe['exits'] = st.session_state.all_exits[0]
                    for i in range(len(st.session_state.exits)):
                        if len(st.session_state.exits[i]) == 4:
                            combination_operator = st.session_state.exits[i][3]
                            if combination_operator == 'AND':
                                candle_dataframe['exits'] = (st.session_state.all_exits[i] & st.session_state.all_exits[i-1])
                            elif combination_operator == 'OR':
                                candle_dataframe['exits'] = (st.session_state.all_exits[i] | st.session_state.all_exits[i-1])

                    backtest(
                        candle_dataframe, 
                        separate_panel_indicators,
                        entries, exits, 
                        timeframe, long_short_both,
                        amount_of_candles=amount_of_candles,
                        sl_start=sl_start, sl_end=sl_end, sl_increment=sl_increment,
                        tp_start=tp_start, tp_end=tp_end, tp_increment=tp_increment,
                        trail_start=trail_start, trail_end=trail_end, trail_increment=trail_increment
                    )

            


