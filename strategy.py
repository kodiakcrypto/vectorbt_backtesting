import pandas_ta as ta
import streamlit as st

import finlab_crypto
import pandas as pd
import numpy as np

def calc_ind(candle_dataframe, args_dicts):
    candle_dataframe.index = candle_dataframe.index.tz_localize(None)
    indicator_dict = {}
    for ind_name, arg_dict in args_dicts.copy().items():
        for arg in arg_dict:
            if arg in ("open_", "high", "low", "close", "volume"):
                args_dicts[ind_name][arg] = candle_dataframe[arg.rstrip("_")]
        ind_function = getattr(ta, ind_name)
        res = ind_function(**arg_dict)
        if isinstance(res, pd.Series):
            candle_dataframe = pd.concat([candle_dataframe, res], columns=candle_dataframe.columns+=res.columns, axis=1)
            indicator_dict[ind_name] = ind_name
        else:
            candle_dataframe = pd.concat([candle_dataframe, res], columns=candle_dataframe.columns+=ind_name, axis=1)
            indicator_dict[ind_name] = res.columns
    return candle_dataframe, indicator_dict


@finlab_crypto.Strategy(separate_panel_indicators=[])
def strategy(candles_ta_dataframe): 
    # give data to chart
    figures = { 
        'overlaps': { #plot all decimal data columns other than ohlcv
            col_name: candles_ta_dataframe[col_name] \
            for col_name in candles_ta_dataframe.columns \
                if col_name not in ['open', 'high', 'low', 'close', 'volume', 'entries', 'exits'] \
                and type(candles_ta_dataframe[col_name].iloc[-1]) == np.float64
        }
    }
    # if strategy.separate_panel_indicators != []:
    #     for indicator in strategy.separate_panel_indicators:
    #         figures[indicator.name] = {col_name: indicator[col_name] for col_name in indicator.columns}

    entries = candles_ta_dataframe['entries'].to_numpy()
    exits = candles_ta_dataframe['exits'].to_numpy()

    return entries, exits, figures

def backtest(candles_dataframe, separate_panel_indicators, 
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
      _vars['ts_stop'] = np.arange(trail_start, trail_end, trail_increment)

    _vars['separate_panel_indicators'] = separate_panel_indicators

    portfolio = strategy.backtest(
        candles_dataframe,
        _vars,
        plot=False,
        size=1,
        init_cash='auto', 
        freq=timeframe, 
        side=long_short_both,
        amount_of_candles=amount_of_candles,
    )
    st.session_state.portfolio = portfolio
