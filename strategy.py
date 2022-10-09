import vectorbt as vbt
import pandas as pd
import pandas_ta as ta
import streamlit as st


def calc_ind(candle_dataframe, col, container, indicators, list_args):
    data_set = {"open_", "high", "low", "close", "volume"}

    # replace value with data[value]
    for ind_name, list_arg in list_args.items():
        for i in list_arg:
            if i in data_set:
                list_args[ind_name][i] = candle_dataframe[i.title().rstrip("_")]

    # add all indicators to dataframe
    for indicator in indicators:
        ind_function = getattr(ta, indicator)
        candle_dataframe[indicator] = ind_function(**list_arg)

    # # # plot data
    with col:
        st.write(candle_dataframe)
        #download csv of data
        st.download_button(
            label="Download data",
            data=candle_dataframe.to_csv().encode("utf-8"),
            file_name="data.csv",
            mime="text/csv",
        )