import unittest

import config


class TestConfig(unittest.TestCase):
    def test_max_unchanged(self):
        self.assertEqual(config.MAX, 3)

    def test_parse(self):
        self.assertEqual(config.parse("a, b"), ["a", "b"])
