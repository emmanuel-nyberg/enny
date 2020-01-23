#!/usr/bin/env python3

import os
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn
import db_operations as db
import mpld3


def make_plot(dfs):
    plt.figure()
    seaborn.set()
    symbol = list(dfs.keys())[0]
    df = dfs.pop(symbol)[::-1]
    matplotlib.use("agg")
    ax = df.close.plot(label=symbol)
    for symbol in dfs:
        df = dfs[symbol]
        df[::-1].close.plot(kind="line", label=symbol, ax=ax)
    return plt


def print_plot(dfs):
    fig = make_plot(dfs)
    fig.show()


def plot_to_html(dfs):
    matplotlib.use("agg")
    fig = make_plot(dfs).gcf()
    plt.legend()
    return mpld3.fig_to_html(fig)


def main():
    symbols = os.getenv("ENNY_SYMBOLS_TO_GRAPH", ["AAPL", "FB"])
    dfs = {}
    for symbol in symbols:
        dfs[symbol] = db.get_dataframe(symbol)
    print_plot(dfs)


if __name__ == "__main__":
    main()
