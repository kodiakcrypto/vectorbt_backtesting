import pandas_ta as ta
import streamlit as st

import finlab_crypto
import pandas as pd
import numpy as np

def calc_ind(candle_dataframe, args_dicts):
    candle_dataframe.index = candle_dataframe.index.tz_localize(None)

    for ind_name, arg_dict in args_dicts.copy().items():
        for arg in arg_dict:
            if arg in ("open_", "high", "low", "close", "volume"):
                args_dicts[ind_name][arg] = candle_dataframe[arg.rstrip("_")]
        ind_function = getattr(ta, ind_name)
        res = ind_function(**arg_dict)
        candle_dataframe = pd.concat([candle_dataframe, res], axis=1)
    return candle_dataframe


@finlab_crypto.Strategy()
def strategy(candles_ta_dataframe, separate_panel_indicators, entries, exits): 
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

def backtest(candles_dataframe, separate_panel_indicators, 
             entries, exits, 
             timeframe, long_short_both,
             amount_of_candles=1000,
             sl_start=None, sl_end=None, sl_increment=None,
             tp_start=None, tp_end=None, tp_increment=None,
             trail_start=None, trail_end=None, trail_increment=None,
    ):

    _vars = {}
    # Get stoploss/takeprofit/trailing stop values
    if sl_end:
      if sl_start is None: sl_start = 0  
      if not sl_increment: sl_increment = round((sl_end - sl_start)/10, 3)
      _vars['sl_stop'] = np.arange(sl_start, sl_end, sl_increment)
    if tp_end:
      if tp_start is None: tp_start = 0
      if not tp_increment: tp_increment = round((tp_end - tp_start)/10, 3)
      _vars['tp_stop'] = np.arange(tp_start, tp_end, tp_increment)
    if trail_end:
      if trail_start is None: trail_start = 0
      if not trail_increment: trail_increment = round((trail_end - trail_start)/10, 3)
      _vars['sl_trail'] = np.arange(trail_start, trail_end, trail_increment)

    portfolio = strategy.backtest(
        candles_dataframe,
        separate_panel_indicators,
        entries,
        exits,
        _vars,
        plot=True,
        size=1,
        init_cash='auto', 
        freq=timeframe, 
        side=long_short_both,
        amount_of_candles=amount_of_candles,
    )

    # st.write(portfolio.stats())
    # st.write(portfolio.plot())
