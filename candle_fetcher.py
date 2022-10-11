import pandas as pd

def get_candles(ticker="BTC-USD", timeframe="1d", amount_of_candles=1000):
    df = pd.DataFrame()
    #valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
    #convert amount of candles to period using timeframe
    periods_to_minutes = {
        '1d': 1440,
        '5d': 7200,
        '1mo': 43200,
        '3mo': 129600,
        '6mo': 259200,
        '1y': 518400,
        '2y': 1036800,
        '5y': 2592000,
        '10y' : 5184000,
    }
    intervals_to_minutes = {
        '1m': 1,
        '2m': 2,
        '5m': 5,
        '15m': 15,
        '30m': 30,
        '90m': 90,
        '1h':60,
        '1d':1440,
        '5d':7200,
        '1wk':10080,
        '1mo':43200,
        '3mo': 129600,
    }
    period = None
    minutes = str(amount_of_candles * intervals_to_minutes[timeframe])
    #what period is greater than minutes
    for k, v in periods_to_minutes.items():
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