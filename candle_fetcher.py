import pandas as pd

def get_candles(ticker="BTC-USD", timeframe="1d", amount_of_candles=1000):
    df = pd.DataFrame()
    #valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    #convert amount of candles to period using timeframe
    periods = {
        "1m": 1,
        "5m": 5,
        "15m": 15,
        "30m": 30,
        "1h": 60,
        "4h": 240,
        "1d": 1440,
        "1w": 10080,
        "1mo": 43200,
        "3mo": 129600,
    }
    period = None
    minutes = str(amount_of_candles * periods[timeframe])
    #what period is greater than minutes
    for k, v in periods.items():
        if v >= minutes:
            period = k
            break
    if not period:
        if minutes <= 129600*4: #1y
            period = "ytd"
        else:
            period = "max"

    cac_df = df.ta.ticker( #yfinance
        ticker, interval=timeframe, period=period
    )
    cac_df.drop(labels=["Dividends", "Stock Splits"], axis=1, inplace=True)
    cac_df.columns = [col.lower().rstrip("_") for col in cac_df.columns]
    return cac_df