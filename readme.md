Dissert
=======

Dissert is a granular assertion disabler.  Lets you write all the inline
assertions you want for development and testing, but puts the fast version
into the hands of your users.  All the code lives in a happy little file with
an MIT license and everything, so feel free to grab it and put it wherever.

There was a [long-lost feature](
https://mail.python.org/pipermail/python-list/2002-March/156528.html) of
Python, where you could disable asserts in a file.  It was cool, if before my
time.  I use like using asserts as in-line unit tests in C++, and ship with
them disabled.  A coworker asked how to do the same in Python.  I'd recently
seen [some](https://github.com/georgek42/inlinec) fun
[projects](https://github.com/pyxl4/pyxl4) abusing
[source code encodings](https://www.python.org/dev/peps/pep-0263/) to fill
weird niches, and this project was born that very night.

We want to litter our code with assertions, and write "always-on" unit tests.
But then your code is sluggish!  Many say to use `python -O`, but your user
might want asserts for something they're using your module for!  Well good
news, we can eat cake and also have cake.  As long as we're all good at 
cleaning up our rooms (or `__pycache__` or whatever).

Absolute file-level dissertion
------------------------------

To disable all asserts in a file, simply set its source encoding to `dissert`.

```python
> source = b"""# encoding: dissert
assert False
print("okay")"""
> exec(source)
okay
```

Selectable file-level dissertion
--------------------------------

We also provide a toggle mechanism for somewhat granular control.

File "fail.py":

```python
# encoding: dissert-select
def foo(x):
    print("oh no, I got called")
    assert x is not x

if foo is not None:
    assert foo() is not None

print("okay")
```

Include it without asserts (delete your `__pycache__`!):

```python
> from dissert import dissert_selector
> with dissert_selector(True):
>     import fail.py
okay
```

Include it with asserts (delete your `__pycache__`!):

```python
> from dissert import dissert_selector
> with dissert_selector(False):
>     import fail.py
oh no, I got called
AssertionError: ...
```

Selectable module-level dissertion
----------------------------------

Dissert your module for release builds by renaming your `__init__.py` to 
`_init_.py` and replacing it with a shim.  Of course, it will only remove
asserts from `dissert` and `dissert-select`-encoded files, but that's more
of a feature than a drawback.

```python
from dissert import dissert
from mymodule.__package_info__ import __release__
with dissert_selector(__release__):
    from mymodule._init_ import *
```

Note that this uses a global variable under the hood, so you might want to
clear the `__pycache__` of dependent projects which also use `dissert`.  It
can be a bit of a rabbit-hole if you want very granular selectivity, as
you'll have to be extremely careful about import order.

Bypass `Assert` and `ASSERT`
----------------------------
The module also defines an `Assert` function that works even in affected
files (but also goes away with `-O`).  Additionally, we provide an `ASSERT`
function that emulates assertions with `if...raise` and doesn't go away under
`-O`.  In a future version, these may be accomplished through mangling the AST
rather than imports.  Make a PR or open a discussion ticket if you think this
is a good/bad idea.

```python
> source = b'''
> # encoding: dissert
> from dissert import Assert
> assert(False, "wrong failure!")
> Assert(False, "successfully failed!")
> raise RuntimeError("bad success")
> '''
> exec(source)
...
AssertionError: successfully failed!
```

