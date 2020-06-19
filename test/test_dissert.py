from dissert import dissert_selector
import unittest

class test_dissert(unittest.TestCase):
    def test_absolute(self):
        from . import fail_absolute

    def test_selector_true(self):
        with dissert_selector(True):
            from . import fail_select0

    def test_selector_false(self):
        with dissert_selector(False):
            with self.assertRaises(AssertionError):
                from . import fail_select1


