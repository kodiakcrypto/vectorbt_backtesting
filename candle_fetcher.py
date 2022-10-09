import pandas as pd

def get_candles(ticker, amount_of_candles):
    df = pd.DataFrame()
    cac_df = df.ta.ticker( #yfinance
        ticker, timeframe="1d", limit=amount_of_candles
    )
    cac_df.drop(labels=["Dividends", "Stock Splits"], axis=1, inplace=True)
    return cac_df