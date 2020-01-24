#!/usr/bin/env python3

import os
import json
import time
from collections import namedtuple
import sqlite3
from urllib.error import HTTPError
import requests
import pandas as pd

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"
DATEFORMAT = "%Y-%m-%d"
TIMEFORMAT = "%H:%M:%S"


class Collector:
    """This class will act as a collector, giving access to the Alpha Vantage API.
    It is configured by environment variables and will return a JSON object."""

    def __init__(self):
        self.config = self._parse_env()

    def _parse_env(self):

        """Parse config. Retuns a Config NamedTuple."""
        Config = namedtuple(
            "Config",
            ["url", "dateformat", "timeformat", "ts_key", "db", "symbols", "apikey",],
        )
        config = Config(
            os.getenv("ENNY_API_URL", ALPHA_VANTAGE_API_URL),
            os.getenv("ENNY_DATEFORMAT", DATEFORMAT),
            os.getenv("ENNY_TIMEFORMAT", TIMEFORMAT),
            "Time Series (60min)"
            if os.getenv("ENNY_HOURLY")
            else "Time Series (Daily)",
            os.getenv("ENNY_DATABASE", "./test.db"),
            os.getenv("ENNY_SYMBOLFILE", "./NDX"),
            os.getenv("ENNY_APIKEY"),
        )
        return config

    def _generate_parameters(self, symbol):
        params = {"symbol": symbol, "outputsize": "full", "apikey": self.config.apikey}
        if "60min" in self.config.ts_key:
            params.update({"interval": "60min", "function": "TIME_SERIES_INTRADAY"})
        elif "Daily" in self.config.ts_key:
            params.update({"function": "TIME_SERIES_DAILY"})
        else:
            raise Exception("Either hourly or daily should be defined")
        return params

    def _api_call(self, params):
        """Use Requests to get the data. Returns json or a HTTPError."""
        r = requests.get(self.config.url, params=params)
        r.raise_for_status()
        return r.json()

    def collect_data(self, symbol):
        """Get the data. Returns a pretty dict."""
        params = self._generate_parameters(symbol)
        try:
            payload = self._api_call(params)
        except HTTPError:
            return {"Error": f"There was a problem fetching data for {symbol}."}
        return self._prettify_dict(payload)

    def _prettify_dict(self, payload):
        """The AlphaVantage API returns ugly, multi-word dictionary keys.
        Make them prettier. Returns a json/dict."""
        try:
            if self._validate_payload(payload):
                payload["metadata"] = payload.pop("Meta Data")
                payload["timeseries"] = payload.pop(self.config.ts_key)
                return payload
        except KeyError as e:
            return e

    def _validate_payload(self, data):
        """Check if the data contains the expected data structure. Returns True or an exception"""
        if "Meta Data" in data.keys():
            return True
        else:
            raise KeyError


def payload_to_dataframe(payload):
    """Turn the timeseries into a Pandas dataframe for further operations."""
    return pd.read_json(json.dumps(payload["timeseries"]), orient="index")


def store_data(df, symbol, instance):
    """Store the data in a SQL database.
        TODO: Set up a real db. instead of sqlite3 files."""
    df.rename(columns=lambda x: "".join([i for i in x if i.isalpha()]), inplace=True)

    with sqlite3.connect(instance.config.db) as con:
        df.to_sql(symbol, con, if_exists="replace")
        con.commit()


def main():
    """Do everythong"""
    av = Collector()
    with open(av.config.symbols, "r") as symbols:
        for s in symbols:
            payload = av.collect_data(s.strip())
            df = payload_to_dataframe(payload)
            store_data(df, s.strip(), av)
            time.sleep(13)  # Let's limit ourselves to 4-5 API calls a minute


if __name__ == "__main__":
    main()
