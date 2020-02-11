#!/usr/bin/env python3
import os
from datetime import date
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import seaborn
import mpld3
import db_operations as db
import configure


def make_plot(timeseries, **kwargs):
    """ Get a dataframe and optionally a to and from-date and return a Matplotlib plot object """
    plt.figure(figsize=(10, 8))
    seaborn.set()
    symbol = list(timeseries.keys())[0]
    df = pd.read_json(timeseries.pop(symbol))
    matplotlib.use("agg")
    ax = df.plot(label=symbol)
    for symbol in timeseries:
        df = pd.read_json(timeseries[symbol])
        df.plot(kind="line", label=symbol, ax=ax)
    return plt


def print_plot(dfs):
    """Print plot for local testing."""
    fig = make_plot(dfs)
    fig.show()


def plot_to_html(dfs, **kwargs):
    """Takes a dataframe and optionally a to- and from date, returns a honking big HTML"""
    matplotlib.use("agg")
    fig = make_plot(dfs, **kwargs).gcf()
    plt.legend()
    return mpld3.fig_to_html(fig)


def main():
    """If you want to run this program from the command line, you can supply a list of symbols
    to graph with an environment variable."""
    symbols = os.getenv("ENNY_SYMBOLS_TO_GRAPH", ["AAPL", "FB"])
    config = configure.parse_env()
    dfs = {}
    for symbol in symbols:
        dfs[symbol] = db.get_dataframe(symbol, config)
    print_plot(dfs)


if __name__ == "__main__":
    main()
