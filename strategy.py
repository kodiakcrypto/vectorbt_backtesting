import pandas_ta as ta
import streamlit as st
import xlsxwriter
from io import BytesIO
import pandas as pd

def calc_ind(filename, candle_dataframe, col, list_args):
    candle_dataframe.index = candle_dataframe.index.tz_localize(None)

    for ind_name, list_arg in list_args.items():
        ind_function = getattr(ta, ind_name)
        with col:
            st.write(ind_function(**list_arg), pd.DataFrame(ind_function(**list_arg), index=candle_dataframe.index))
        candle_dataframe[ind_name] = ind_function(**list_arg)

    # plot data
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
            help="Download XLSX Excel file"
        )