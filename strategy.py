import pandas_ta as ta
import streamlit as st
import pandas as pd


def calc_ind(filename, candle_dataframe, col, list_args):
    data_set = {"open_", "high", "low", "close", "volume"}

    # replace value with data[value]
    tmp_list_args = {}
    for ind_name, list_arg in list_args.items():
        for col_name in list_arg:
            if col_name in data_set:
                tmp_list_args[ind_name] = {}
                tmp_list_args[ind_name][col_name] = candle_dataframe[col_name.title().rstrip("_")]
        
        ind_function = getattr(ta, ind_name)
        candle_dataframe[ind_name] = ind_function(**list_arg)
            # candle_dataframe[ind_name] = res
        candle_dataframe.index = candle_dataframe.index.tz_localize(None)
        
    # # # plot data
    with col:
        st.write(candle_dataframe)
        #download csv of data
        st.download_button(
            label="⬇️ CSV",
            data=candle_dataframe.to_csv().encode("utf-8"),
            file_name=f"{filename}.csv",
            mime="text/csv",
            help="Download CSV file",
        )
        #download xlsx
        st.download_button(
            label="⬇️ XLSX",
            data=candle_dataframe.to_excel(f"{filename}.xlsx"),
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download XLSX Excel file"
        )