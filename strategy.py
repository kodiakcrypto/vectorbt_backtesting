import pandas_ta as ta
import streamlit as st
import xlsxwriter
from io import BytesIO

import finlab_crypto
import pandas as pd
import numpy as np

def calc_ind(filename, candle_dataframe, timeframe, col, args_dicts):
    
    _b1, _b2, b1, b2, b3, b4, c1, a1, a2, a3 = st.columns([1,1,1,1,1,1,2,1,1,1])
    candle_dataframe.index = candle_dataframe.index.tz_localize(None)

    for ind_name, arg_dict in args_dicts.copy().items():
        for arg in arg_dict:
            if arg in ("open_", "high", "low", "close", "volume"):
                args_dicts[ind_name][arg] = candle_dataframe[arg.rstrip("_")]
        ind_function = getattr(ta, ind_name)
        res = ind_function(**arg_dict)
        candle_dataframe = pd.concat([candle_dataframe, res], axis=1)

    clean_columns = [column for column in candle_dataframe.columns \
                if column not in ['open', 'high', 'low', 'close', 'volume', 'entries', 'exits'] \
                    and type(candle_dataframe[column].iloc[-1]) == np.float64]
                    
    # plot data
    with col:
        st.write(candle_dataframe)

    #download csv of data
    with _b1:
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
    with _b2:
        st.download_button(
            label="⬇️ XLSX",
            data=output.getvalue(),
            file_name=f"{filename}.xlsx",
            mime="application/vnd.ms-excel",
            help="Download XLSX Excel file"
        )


    backtest_boxes = st.expander('Backtest Options', expanded=False)
    with backtest_boxes:
        with b1:
            long_short_both = st.selectbox('Long/Short/Both', ['long', 'short', 'both'])
            amount_of_candles = st.number_input('# of Candles on chart', value=1000, min_value=1, max_value=10000, step=1)
        with b2:
            sl_start = st.number_input('SL Start', value=None, min_value=None, max_value=None, step=0.001)
            sl_end = st.number_input('SL End', value=None, min_value=None, max_value=None, step=0.001)
            sl_increment = st.number_input('SL Increment', value=None, min_value=None, max_value=None, step=0.001)
        with b3:
            tp_start = st.number_input('TP Start', value=None, min_value=None, max_value=None, step=0.001)
            tp_end = st.number_input('TP End', value=None, min_value=None, max_value=None, step=0.001)
            tp_increment = st.number_input('TP Increment', value=None, min_value=None, max_value=None, step=0.001)
        with b4:
            trail_start = st.number_input('Trail Start', value=None, min_value=None, max_value=None, step=0.001)
            trail_end = st.number_input('Trail End', value=None, min_value=None, max_value=None, step=0.001)
            trail_increment = st.number_input('Trail Increment', value=None, min_value=None, max_value=None, step=0.001)
        with c1:
            # add multi select box to choose dataframe columns to use
            st.write('Select the columns like ATR and RSI to plot below the chart')
            columns = st.multiselect('Column Names', clean_columns)
            separate_panel_indicators = candle_dataframe[columns]

        #select column to use for backtest
        st.write('Select the column to use for backtest')
        with a1: backtest_column1 = st.selectbox('Column #1', clean_columns)
        with a2: comparison_operator = st.selectbox('Comparison', ['>', '<', '>=', '<=', '==', '-', '+','*','/'])
        with a3: backtest_column2 = st.selectbox('Column #2', clean_columns)
        comparison_function = getattr(np, comparison_operator)

        #compare these dataframes
        comparison = candle_dataframe[backtest_column1].astype(float) \
                        .compare(candle_dataframe[backtest_column2].astype(float), 
                            comparison_function, keep_shape=True, keep_equal=True)

        if st.button('Run Backtest'):
            backtest(
                candle_dataframe, separate_panel_indicators,
                timeframe, long_short_both,
                amount_of_candles=amount_of_candles,
                sl_start=sl_start, sl_end=sl_end, sl_increment=sl_increment,
                tp_start=tp_start, tp_end=tp_end, tp_increment=tp_increment,
                trail_start=trail_start, trail_end=trail_end, trail_increment=trail_increment
            )



@finlab_crypto.Strategy()
def strategy(candles_ta_dataframe, separate_panel_indicators): 
    # give data to chart
    figures = {
      'figures': {
        'overlaps': { #plot all decimal data columns other than ohlcv
          col_name: candles_ta_dataframe[col_name] \
            for col_name in candles_ta_dataframe.columns \
              if col_name not in ['open', 'high', 'low', 'close', 'volume', 'entries', 'exits'] \
                and type(candles_ta_dataframe[col_name].iloc[-1]) == np.float64
        }
      }
    }

    for col_name in separate_panel_indicators.columns:
        figures[col_name] = { col_name: separate_panel_indicators[col_name] }

    entries = candles_ta_dataframe['entries']
    exits = candles_ta_dataframe['exits']

    return entries, exits, figures

def backtest(candles_dataframe, separate_panel_indicators, timeframe, long_short_both,
             amount_of_candles=1000,
             sl_start=None, sl_end=None, sl_increment=None,
             tp_start=None, tp_end=None, tp_increment=None,
             trail_start=None, trail_end=None, trail_increment=None,
    ):

    _vars = {}
    # Get stoploss/takeprofit/trailing stop values
    if sl_start and sl_end:
      if not sl_increment: sl_increment = round(sl_end - sl_start, 3)
      _vars['sl_stop'] = np.arange(sl_start, sl_end, sl_increment)
    if tp_start and tp_end and tp_increment:
      if not sl_increment: tp_increment = round(sl_end - sl_start, 3)
      _vars['tp_stop'] = np.arange(tp_start, tp_end, tp_increment)
    if trail_start and trail_end and trail_increment:
      if not sl_increment: trail_increment = round(sl_end - sl_start, 3)
      _vars['sl_trail'] = np.arange(trail_start, trail_end, trail_increment)

    portfolio = strategy.backtest(
        candles_dataframe,
        separate_panel_indicators,
        _vars,
        plot=True,
        size=1,
        init_cash='auto', 
        freq=timeframe, 
        side=long_short_both,
        amount_of_candles=amount_of_candles,
    )

    st.write(portfolio.stats())
    st.write(portfolio.plot())
