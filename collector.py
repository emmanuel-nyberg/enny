#!/usr/bin/env python3

import argparse
import json
import time
from collections import namedtuple
import datetime
import re
import sys
import requests

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"
DATEFORMAT = "%Y-%m-%d"
TIMEFORMAT = "%H:%M:%S"
Config = namedtuple("Config", ["url", "dateformat", "timeformat", "ts_key"])


class Collector:
    """This class will act as a collector, giving access to the Alpha Vantage API.
    Its methods return the recieved JSON."""

    def __init__(self, args, config):
        self.args = args
        self.config = config

    def _generate_parameters(self, symbol):
        params = {"symbol": symbol, "outputsize": "full", "apikiey": self.args.apikey}
        if self.args.hourly:
            params.update({"interval": "60min", "function": "TIME_SERIES_INTRADAY"})
        elif self.args.daily:
            params.update({"function": "TIME_SERIES_DAILY"})
        else:
            raise Exception("Either hourly or daily should be defined")
        return params

    def _api_call(self, params):
        r = requests.get(self.config.url, params=params)
        if r.status_code == 200:
            return r.json()
        else:
            e = {"Error": r.url + " returned " + str(r.status_code)}
            return e

    def collect_data(self, symbol):
        params = self._generate_parameters(symbol)
        payload = self._api_call(params)
        if re.search("Error.*", str(payload.keys())):
            return payload
        else:
            return self._prettify_dict(payload, symbol)

    def _prettify_dict(self, payload, symbol):
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


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--apikey", required=True, help="Must use apikey")
    parser.add_argument(
        "-s",
        "--symbols",
        help="Name of file containing the stocks we shall fetch",
        default="./NDX",
    )
    parser.add_argument(
        "-o", "--outfile", help="Name of file to write data to", default="./stonks.json"
    )
    parser.add_argument("--daily", help="Fetch daily history", action="store_true")
    parser.add_argument(
        "--hourly", help="Fetch intraday history by the hour", action="store_true"
    )
    return parser.parse_args(args)


def main():
    """Do everythong"""

    args = parse_args(sys.argv[1:])

    config = Config(
        ALPHA_VANTAGE_API_URL,
        DATEFORMAT,
        TIMEFORMAT,
        "Time Series (Daily)" if args.daily else "Time Series (60min)",
    )

    av = Collector(args, config)
    with open(args.symbols, "r") as symbols:
        for s in symbols:
            with open(args.outfile, "a") as out:
                payload = av.collect_data(s.strip())
                out.write(json.dumps(payload) + "\n")

                time.sleep(13)  # Let's limit ourselves to 4-5 API calls a minute


if __name__ == "__main__":
    main()
