#!/usr/bin/env python3

import argparse
import json
import time
from datetime import date
import requests

ALPHA_VANTAGE_API_URL = "https://www.alphavantage.co/query?"

class AlphaVantage:
    """This class will act as a collector, giving access to the Alpha Vantage API.
    Its methods return the recieved JSON as a string for ease of storage."""
    def __init__(self, args):
        self.key = args.apikey
        self.url = ALPHA_VANTAGE_API_URL
    def get_full_daily(self, symbol):
        endpoint = "{}function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey={}".format(
            self.url, symbol, self.key)
        r = requests.request("GET", endpoint)
        return json.dumps(r.json())
    def get_full_hourly(self, symbol):
        endpoint = "{}function=TIME_SERIES_INTRADAY&symbol={}&interval=60min&outputsize=full&apikey={}".format(
            self.url, symbol, self.key)
        r = requests.request("GET", endpoint)
        return json.dumps(r.json())

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

    av = AlphaVantage(args)
    with open(args.symbols, "r") as symbols:
        for s in symbols:
            with open(args.outfile, "a") as out:
                if args.daily:
                    payload = av.get_full_daily(s.strip("\n"))
                elif args.hourly:
                    payload = av.get_full_hourly(s.strip("\n"))
                out.write(payload + "\n")
                time.sleep(13) #Let's be good API users and limit us to 4-5 API calls a minute

if __name__ == "__main__":
    main()
