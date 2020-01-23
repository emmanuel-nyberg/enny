import sqlite3 as db
import pandas as pd


def get_dataframe(symbol):
    with db.connect("test.db") as con:
        df = pd.read_sql(f"SELECT * FROM {symbol};", con, index_col="index")
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")
