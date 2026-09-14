"""Unrelated fixture behavior — must still pass after LABEL change."""
import unittest

import widget


class TestWidget(unittest.TestCase):
    def test_greet_prefix(self):
        self.assertTrue(widget.greet().startswith("hello "))

    def test_ping(self):
        self.assertEqual(widget.ping(), "pong")
