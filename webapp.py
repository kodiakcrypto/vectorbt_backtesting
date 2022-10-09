from email.policy import default
import streamlit as st
import pandas_ta as ta
import pandas as pd
import inspect
from pandas_ta_utils import list_ind
from strategy import calc_ind
from candle_fetcher import get_candles


def main():
    st.header("Data Downloader")

    col1, col2 = st.columns([2, 5])
    # container: will be used by callback function calc_ind to populate the page
    cont = st.container()
    cont.write("")
    with col1:
        # ticker
        ticker = st.text_input("Ticker", "BTC-USD")
        amount_of_candles = st.number_input("Amount of candles", 100, 100000, 1000)
        timeframe = st.selectbox("Timeframe", ["1m", "5m", "15m", "1h", "4h", "1d", "1w"])
        # List of all indicators
        indicators = list_ind()
        select_ind = st.multiselect("Choose indicators to apply to data", indicators)

        ind_functions = [getattr(ta, ind) for ind in select_ind]
        st.sidebar.write(ind_function.__doc__)

        list_args = {} #multi indicator
        #list indicator parameter boxes
        for ind_function in ind_functions:
            arguments = inspect.getfullargspec(ind_function) #get all params needed
            list_arg = {}
            for argument in arguments.args:
                param_box = f"{argument}input" #name the input box
                
                # toggle type of input according to variable. Data will be automatically added, no need to enter infos
                input_box_unique_id = ind_function.__name__+'_'+argument
                data_set = {"open_", "high", "low", "close", "volume"}
                text_set = {"mamode"}
                if argument in text_set:
                    param_box = st.text_input(argument, key=input_box_unique_id)
                elif argument == "talib":
                    param_box = False
                elif argument == 'offset':
                    param_box = 0
                elif argument not in data_set:
                    param_box = st.number_input(argument, step=1, key=input_box_unique_id)
                list_arg[argument] = param_box
            list_args[ind_function.__name__] = list_arg #multi indicator
        filename = ticker + "_" + str(amount_of_candles) + "_candles"
        def get_final_dataframe():
            calc_ind(filename, get_candles(ticker, timeframe, amount_of_candles), col2, list_args)
        st.button("Go Go Go", on_click=get_final_dataframe)
        


