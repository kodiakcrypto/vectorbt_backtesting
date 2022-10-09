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

        # List of all indicators
        indicators = list_ind()
        select_ind = st.multiselect("Choose indicators to apply to data", indicators)

        ind_functions = [getattr(ta, ind) for ind in select_ind]
        # st.sidebar.write(ind_function.__doc__)

        list_args = {} #multi indicator
        #list indicator parameter boxes
        for ind_function in ind_functions:
            arguments = inspect.getfullargspec(ind_function)
            list_arg = {}
            for argument in arguments.args:
                name_textin = f"{argument}input"
                # toggle type of input according to variable. Data will be automatically added, no need to enter infos
                data_set = {"open_", "high", "low", "close", "volume"}
                text_set = {"mamode"}
                bool_set = {"talib"}
                if argument in text_set:
                    name_textin = st.text_input(argument, key=ind_function.__name__+'_'+argument)
                elif argument in bool_set:
                    name_textin = st.radio(argument, options=(True, False), key=ind_function.__name__+'_'+argument)
                elif argument not in data_set:
                    name_textin = st.number_input(argument, step=1, key=ind_function.__name__+'_'+argument)

                list_arg[argument] = name_textin
            list_args[ind_function.__name__] = list_arg #multi indicator

        get_final_dataframe = lambda *args: calc_ind(get_candles(ticker, amount_of_candles), *args)
        st.button("Submit", on_click=get_final_dataframe, args=(col2, cont, select_ind, list_args))
        


