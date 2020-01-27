#!/usr/bin/env python3

import unittest
from urllib.error import HTTPError
import json
import collector
import requests_mock
import pandas.core


class TestCollectorMainMethods(unittest.TestCase):
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
            "",
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
        prettified_data = self.av._prettify_dict(self.sample_data)
        self.assertIn("timeseries", prettified_data)
        self.assertIn("metadata", prettified_data)
        self.assertNotIn("Meta Data", prettified_data)
        self.assertNotIn("Time Series", prettified_data)

    def test_generate_parameters(self):
        self.assertIs(dict, type(self.av._generate_parameters("AAPL")))

    @requests_mock.Mocker()
    def test_api_call(self, mock_request):
        config = collector.Config("mock://test.url/404", "", "", "", "")
        av_404 = collector.Collector(self.args, config)
        mock_request.get(
            "mock://test.url", json=self.sample_data, status_code=200,
        )
        mock_request.get(
            "mock://test.url/404", status_code=404,
        )
        self.assertDictEqual(
            self.sample_data, self.av._api_call(self.av._generate_parameters("AAPL")),
        )
        try:
            self.assertRaises(
                HTTPError, av_404._api_call(av_404._generate_parameters("ERROR"))
            )
        except:
            pass

    @requests_mock.Mocker()
    def test_collector(self, mock_request):
        mock_request.get(
            "mock://test.url", json=self.sample_data, status_code=200,
        )
        self.assertIn("metadata", self.av.collect_data("AAPL"))

    @requests_mock.Mocker()
    def test_payload_to_data(self, mock_request):
        mock_request.get(
            "mock://test.url", json=self.sample_data, status_code=200,
        )
        self.assertIsInstance(
            collector.payload_to_dataframe(self.av.collect_data("AAPL")),
            pandas.core.frame.DataFrame,
        )
