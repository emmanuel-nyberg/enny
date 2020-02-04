import pandas


def closing_value(df):
    return df.close[::-1]


def cumulative_returns(df):
    return (monthly_returns(df) + 1).cumprod()


def daily_returns(df):
    return df[::-1].close.pct_change()


def monthly_returns(df):
    return df[::-1].close.resample("M").ffill().pct_change()
