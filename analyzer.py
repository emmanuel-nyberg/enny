def closing_value(df):
    return df.close


def cumulative_returns(df):
    return (monthly_returns(df) + 1).cumprod()


def daily_returns(df):
    return df.close.pct_change()


def monthly_returns(df):
    return df.close.resample("M").ffill().pct_change()
