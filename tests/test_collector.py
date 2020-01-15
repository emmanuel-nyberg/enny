#!/usr/bin/env python3

import unittest
import requests_mock
import collector
import json


class TestCollectorMethods(unittest.TestCase):
    def test_parser(self):
        parser = collector.parse_args(["-k", "abc123", "--daily"])
        self.assertEqual(parser.apikey.strip(), "abc123")
        self.assertTrue(parser.daily)


class TestCollectorMethods(unittest.TestCase):
    def __init__(self, methodName):
        super().__init__(methodName)
        self.args = collector.parse_args(["-k", "testkey", "--daily"])
        self.config = collector.Config(
            "mock://test.url",
            collector.DATEFORMAT,
            collector.TIMEFORMAT,
            "Time Series (Daily)" if self.args.daily else "Time Series (60min)",
        )
        self.av = collector.Collector(self.args, self.config)
        with open("tests/sample_data.json", "r") as self.sample_data_file:
            self.sample_data = json.loads(self.sample_data_file.readline())

    def test_validator(self):
        self.assertTrue(self.av._validate_payload(self.sample_data))
        try:
            self.assertRaises(
                KeyError, self.av._validate_payload({"Error": "Bad data"}),
            )
        except:
            pass

    def test_normalizer(self):
        prettified_data = self.av._prettify_dict(self.sample_data, "AAPL")
        self.assertIn("timeseries", prettified_data)
        self.assertIn("metadata", prettified_data)
        self.assertNotIn("Meta Data", prettified_data)
        self.assertNotIn("Tine Series", prettified_data)

    @requests_mock.Mocker()
    def test_collector(self, mock_request):
        mock_request.get(
            "mock://test.url", json=self.sample_data, status_code=200,
        )
        self.assertIn("metadata", self.av.collect_data("AAPL"))
