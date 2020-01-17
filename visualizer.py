#!/usr/bin/env python3

import sqlite3 as db
import pandas as pd
import matplotlib.pyplot as plt


def get_dataframe(symbol):
    with db.connect("test.db") as con:
        return pd.read_sql(f"SELECT * FROM {symbol};", con)


def print_plot(df):
    df.plot(kind="line", x="index", y="2. high")
    plt.show()
    # plt.savefig("./plot.png")


def main():
    print_plot(get_dataframe("AMZN"))


if __name__ == "__main__":
    main()
