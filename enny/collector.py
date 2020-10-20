#!/usr/bin/env python3

import json
import time
from urllib.error import HTTPError
import requests
import pandas as pd
import db_operations as db
import configure


class Collector:
    """This class will act as a collector, giving access to the Alpha Vantage API.
    It is configured by environment variables and will return a JSON object."""

    def __init__(self):
        self.config = configure.parse_env()

    def _generate_parameters(self, symbol):
        """Build our request to Alpha Vantage."""
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


def collect(symbol):
    """Initialise the Collector instance and use it to get some stonks."""
    av = Collector()
    try:
        payload = av.collect_data(symbol)
        df = payload_to_dataframe(payload)
        db.store_data(df.resample('D').interpolate(), symbol, av)
        return {"msg": f"Collected {symbol}."}
    except Exception as e:
        return {"error": f"Failed at collecting {symbol}. /n{e}"}


def main():
    """Do everythong"""
    av = Collector()
    with open(av.config.symbols, "r") as symbols:
        for s in symbols:
            collect(s.strip())
            time.sleep(13)  # Let's limit ourselves to 4-5 API calls a minute


if __name__ == "__main__":
    main()
