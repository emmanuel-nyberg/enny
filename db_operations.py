import sqlite3 as db
import pandas as pd


def get_dataframe(symbol):
    """This function takes a symbol as input and returns a Pandas dataframe, indexed by date."""
    with db.connect("test.db") as con:
        df = pd.read_sql(f"SELECT * FROM {symbol};", con, index_col="index")
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")
