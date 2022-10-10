import pandas_ta as ta
import streamlit as st
import xlsxwriter
from io import BytesIO
import pandas as pd

def calc_ind(filename, candle_dataframe, col, list_args):
    candle_dataframe.index = candle_dataframe.index.tz_localize(None)

    for ind_name, list_arg in list_args.copy().items():
        for arg in list_arg:
            if arg in ("open_", "high", "low", "close", "volume"):
                list_arg[arg] = candle_dataframe[arg.title().rstrip("_")]
        ind_function = getattr(ta, ind_name)
        res = ind_function(**list_arg)
        # candle_dataframe[ind_name] = res
        with col:
            st.write(res)
            # st.write(pd.DataFrame(res, index=candle_dataframe.index))

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