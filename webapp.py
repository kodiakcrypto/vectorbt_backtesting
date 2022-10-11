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


def main():
    st.header("Data Downloader")
    candle_dataframe = None
    expanded = False
    col1, col2 = st.columns([2, 3])

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
            filename = f"{ticker}_{timeframe}_{amount_of_candles}_candles"
            candle_dataframe = calc_ind(get_candles(ticker, timeframe, amount_of_candles), args_dicts)

    # plot data
    if candle_dataframe is not None:
        with col2:
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

            backtest_boxes = st.expander('Backtest Options', expanded=expanded)
            with backtest_boxes:
                expanded = True

                long_short_both = st.selectbox('Long/Short/Both', ['long', 'short', 'both'], index=0, key='long_short_both')
                amount_of_candles = st.number_input('# of Candles on chart', value=1000, min_value=1, max_value=10000, step=1, key='amount_of_candles')

                sl_start = st.number_input('SL Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_start')
                sl_end = st.number_input('SL End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_end')
                sl_increment = st.number_input('SL Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='sl_increment')

                tp_start = st.number_input('TP Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp_start')
                tp_end = st.number_input('TP End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp_end')
                tp_increment = st.number_input('TP Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='tp')

                trail_start = st.number_input('Trail Start', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_start')
                trail_end = st.number_input('Trail End', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_end')
                trail_increment = st.number_input('Trail Increment', value=0.000, min_value=0.000, max_value=0.5, step=0.001, key='trail_increment')
                # add multi select box to choose dataframe columns to use
                st.write('Select the columns like ATR and RSI to plot below the chart')
                columns = st.multiselect('Column Names', clean_columns, key='clean_cols')
                separate_panel_indicators = candle_dataframe[columns]

                #select column to use for backtest
                st.write('#### Backtest Entry Conditions')
                backtest_column1 = st.selectbox('Column #1', clean_columns, key='bt_1')
                comparison_operator = st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'], key='bt_2')
                backtest_column2 = st.selectbox('Column #2', clean_columns, key='bt_3')
                
                #compare these dataframes
                entries = operator_to_operation(candle_dataframe[backtest_column1], 
                                                candle_dataframe[backtest_column2], 
                                                comparison_operator)



                st.write('#### Exit Entry Conditions')
                ex_backtest_column1 = st.selectbox('Column #1', clean_columns, key='ex_1')
                ex_comparison_operator = st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'], key='ex_2')
                ex_backtest_column2 = st.selectbox('Column #2', clean_columns, key='ex_3')
                
                #compare these dataframes
                exits = operator_to_operation(candle_dataframe[ex_backtest_column1], 
                                              candle_dataframe[ex_backtest_column2], 
                                              ex_comparison_operator)

                if st.button('Run Backtest'):
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

            


