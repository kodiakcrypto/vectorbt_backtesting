import pandas as pd

def get_candles(ticker="BTC-USD", timeframe="1d", amount_of_candles=1000):
    df = pd.DataFrame()
    cac_df = df.ta.ticker( #yfinance
        ticker, timeframe=timeframe, limit=amount_of_candles
    )
    cac_df.drop(labels=["Dividends", "Stock Splits"], axis=1, inplace=True)
    cac_df.columns = [col.title().rstrip("_") for col in cac_df.columns]
    return cac_df