from dissert import dissert_selector, dissert_select
import unittest

class test_dissert(unittest.TestCase):
    def test_absolute(self):
        from . import fail_absolute

    def test_selector_true(self):
        with dissert_selector(True):
            with self.assertRaises(RuntimeError):
                from . import fail_select0

    def test_selector_false(self):
        with dissert_selector(False):
            with self.assertRaises(AssertionError):
                from . import fail_select1

    def test_dissert_bypass(self):
        head = b'\n'.join((b'# coding: dissert',
                          b'from dissert import Assert, ASSERT',
                          b'try: assert False',
                          b'except AssertionError: raise RuntimeError'))

        with self.assertRaises(AssertionError):
            exec(b'\n'.join((head, b'Assert(False, "hello world")')))

        with self.assertRaises(AssertionError):
            exec(b'\n'.join((head, b'ASSERT(False, "hello world")')))

    def test_select(self):
        dissert_select(True)
        exec(b'# coding: dissert-select\nassert False, "hello world"')
        dissert_select(False)
        with self.assertRaises(AssertionError):
            exec(b'# coding: dissert-select\nassert False, "hello world"')

    def test_encode(self):
        with self.assertRaises(NotImplementedError):
            "".encode("dissert")
