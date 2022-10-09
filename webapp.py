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
            arguments = inspect.getfullargspec(ind_function) #get all params needed
            list_arg = {}
            for argument in arguments.args:
                param_box_label = f"{argument}input" #name the input box
                # toggle type of input according to variable. Data will be automatically added, no need to enter infos

                #check what datatype argument is
                input_box_unique_id = ind_function.__name__+'_'+argument
                arg_type = type(argument)
                if arg_type == int:
                    param_box_label = st.number_input(argument, step=1, key=input_box_unique_id)
                elif arg_type == float:
                    param_box_label = st.number_input(argument, step=0.1, key=input_box_unique_id)
                elif arg_type == str:
                    param_box_label = st.text_input(argument, key=input_box_unique_id)
                elif arg_type == bool:
                    param_box_label = st.checkbox(argument, key=input_box_unique_id)
                else:
                    param_box_label = st.text_input(argument, key=input_box_unique_id)

                list_arg[argument] = param_box_label
            list_args[ind_function.__name__] = list_arg #multi indicator
        filename = ticker + "_" + str(amount_of_candles) + "_candles"
        get_final_dataframe = lambda *args: calc_ind(filename, get_candles(ticker, amount_of_candles), *args)
        st.button("Submit", on_click=get_final_dataframe, args=(col2, cont, select_ind, list_args))
        


