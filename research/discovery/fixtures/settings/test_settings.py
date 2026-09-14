import unittest

import settings


class TestSettings(unittest.TestCase):
    def test_limit(self):
        self.assertEqual(settings.LIMIT, 9)
