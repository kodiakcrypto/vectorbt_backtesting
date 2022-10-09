import pandas_ta as ta
import streamlit as st


def calc_ind(filename, candle_dataframe, col, container, indicators, list_args):
    data_set = {"open_", "high", "low", "close", "volume"}

    # replace value with data[value]
    for ind_name, list_arg in list_args.items():
        for i in list_arg:
            if i in data_set:
                list_args[ind_name][i] = candle_dataframe[i.title().rstrip("_")]
        ind_function = getattr(ta, ind_name)
        candle_dataframe[ind_name] = ind_function(**list_arg)

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
            data=candle_dataframe.to_excel().encode("utf-8"),
            file_name=f"{filename}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            help="Download XLSX Excel file"
        )