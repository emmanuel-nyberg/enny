#!/usr/bin/env python3

import unittest
import collector


class TestCollectorMethods(unittest.TestCase):
    def test_parser(self):
        parser = collector.parse_args(["-k abc123", "--daily"])
        self.assertEqual(parser.apikey.strip(), "abc123")
        self.assertTrue(parser.daily)
