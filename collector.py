#!/usr/bin/env python3

import argparse
import json
import time
from collections import namedtuple
import datetime
import re
import requests

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"
DATEFORMAT = "%Y-%m-%d"
TIMEFORMAT = "%H:%M:%S"
Config = namedtuple('Config', ['url', 'dateformat', 'timeformat', 'ts_key'])




class Collector:
    """This class will act as a collector, giving access to the Alpha Vantage API.
    Its methods return the recieved JSON."""
    def __init__(self, args, config):
        self.args = args
        self.config = config

    def _generate_endpoint(self, symbol):
        endpoint = "{}function={}&symbol={}{}&outputsize=full&apikey={}".format(
                self.config.url,
                "TIME_SERIES_DAILY" if self.args.daily else "TIME_SERIES_INTRADAY",
                symbol,
                "&interval=60min" if self.args.hourly else "",
                self.args.apikey)
        return endpoint

    def _api_call(self, endpoint):
        r = requests.request("GET", endpoint)
        if r.status_code == 200:
            r.json()['Meta Data']['fetched'] = datetime.datetime.now().strftime(self.config.dateformat + self.config.timeformat)
            return r.json()
        else:
            e = {"Error": endpoint + " returned " + str(r.status_code)}
            return e

    def collect_data(self, symbol):
        endpoint = self._generate_endpoint(symbol)
        payload = self._api_call(endpoint)
        if re.search("Error.*", str(payload.keys())):
            return payload
        else:
            return self._prettify_dict(payload, symbol)

    def _prettify_dict(self, payload, symbol):
        """The AlphaVantage API returns ugly, multi-word dictionary keys.
        Make them prettier. Returns a json/dict."""
        if self._validate_payload(payload):
            payload["metadata"] = payload.pop('Meta Data')
            payload["timeseries"] = payload.pop(self.config.ts_key)
            return payload 
        else:
            return {"Error": f"Data for {symbol} is not fresh"}

    def _validate_payload(self, data):
        """Check if the data is fresh. Returns a boolean."""
        if re.search(f"{datetime.date.today().strftime(self.config.dateformat)}.*", str(data[self.config.ts_key].keys())):
            return True

def main():
    """Do everythong"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", "--apikey", required=True, help="Must use apikey")
    parser.add_argument("-s", "--symbols", help="Name of file containing the stocks we shall fetch",
                        default="./NDX")
    parser.add_argument("-o", "--outfile", help="Name of file to write data to",
                        default="./stonks.json")
    parser.add_argument("--daily", help="Fetch daily history", action="store_true")
    parser.add_argument("--hourly", help="Fetch intraday history by the hour", action="store_true")
    args = parser.parse_args()

    config = Config(ALPHA_VANTAGE_API_URL, 
        DATEFORMAT,
        TIMEFORMAT,
        "Time Series " + "(Daily)" if args.daily else "Time Series " + "(60min)")

    av = Collector(args, config)
    with open(args.symbols, "r") as symbols:
        for s in symbols:
            with open(args.outfile, "a") as out:
                payload = av.collect_data(s.strip())
                out.write(json.dumps(payload) + "\n")

                time.sleep(13) #Let's be good API users and limit ourselves to 4-5 API calls a minute

if __name__ == "__main__":
    main()
