#!/usr/bin/env python3

import sqlite3 as db
import pandas as pd
import matplotlib.pyplot as plt
import seaborn


def get_dataframe(symbol):
    with db.connect("test.db") as con:
        df = pd.read_sql(f"SELECT * FROM {symbol};", con, index_col="index")
    df["date"] = pd.to_datetime(df.index)
    return df.set_index("date")


def print_plot(dfs, symbols):
    df = dfs.pop(list(dfs.keys())[0])[::-1]
    ax = df.close.plot()
    for symbol in dfs:
        df = dfs[symbol]
        axis = df[::-1].close.plot(kind="line", ax=ax)
    plt.legend(symbols)
    plt.show()


def main():
    symbols = ["AMZN", "AAPL", "FB", "GOOG"]
    dfs = {}
    plt.figure()
    seaborn.set()
    for symbol in symbols:
        dfs[symbol] = get_dataframe(symbol)
    print_plot(dfs, symbols)


if __name__ == "__main__":
    main()
