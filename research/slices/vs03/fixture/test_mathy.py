import unittest

import mathy


class TestMulUnrelated(unittest.TestCase):
    def test_mul(self):
        self.assertEqual(mathy.mul(2, 3), 6)
