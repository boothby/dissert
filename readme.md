A release-mode assertion disabler.  Lets you write all the inline assertions
you want for development and testing, but puts the fast version into the hands
of your users.

File "fail.py":

```python
# encoding: dissert
def foo(x):
    print("oh no, I got called")
    assert x is not x

if foo is not None:
    assert foo() is not None

print("okay")
```

Include it without asserts (delete your `_pycache_`!):

```python
> from dissert import dissert
> with dissert(True):
>     import fail.py
okay
```

Include it with asserts (delete your `_pycache_`!):

```python
> from dissert import dissert
> with dissert(False):
>     import fail.py
oh no, I got called
AssertionError: ...
```

Slap it on your module by renaming your `__init__.py` to `_init_.py` and
replacing it with a shim:

```python
from dissert import dissert
from mymodule.__package_info__ import __release__
with dissert(__release__):
    from mymodule._init_ import *
```

Of course, it will only remove asserts from marked files, but we can call
that a feature since it gives some control over which files are disserted. To
prove that it's a feature, we'll throw in an Assert function that works even
in affected files (but also goes away with `-O`)

```python
> source = '''
> # encoding: dissert
> from dissert import Assert
> assert(False, "wrong failure!")
> Assert(False, "successfully failed!")
> '''
> with dissert(True)
>     eval(source)
...
AssertionError: successfully failed!
```
