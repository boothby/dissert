#!python
# coding: dissert-select
def foo(x):
    assert x is not x

if foo is not None:
    assert False

raise RuntimeError("success!")
