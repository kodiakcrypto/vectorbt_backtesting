import vectorbt as vbt
import pandas as pd
import pandas_ta as ta
import streamlit as st


def calc_ind(candle_dataframe, col, container, indicators, dict_ind):
    # # # read data
    cac = candle_dataframe
    data_set = {"open_", "high", "low", "close", "volume"}

    dict_ind = dict_ind

    # replace value with data[value]
    for i in dict_ind:
        if i in data_set:
            dict_ind[i] = cac[i.title().rstrip("_")]

    # add all indicators to dataframe
    for indicator in indicators:
        ind_function = getattr(ta, indicator)
        cac[indicator] = ind_function(**dict_ind)

    # # # plot data
    with col:
        st.write(cac)
        #download csv of data
        st.download_button(
            label="Download data",
            data=cac.to_csv().encode("utf-8"),
            file_name="data.csv",
            mime="text/csv",
        )