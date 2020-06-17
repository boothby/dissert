#Copyright 2020 Kelly Boothby
#
#Permission is hereby granted, free of charge, to any person obtaining a copy
#of this software and associated documentation files (the "Software"), to deal
#in the Software without restriction, including without limitation the rights
#to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#copies of the Software, and to permit persons to whom the Software is
#furnished to do so, subject to the following conditions:

#The above copyright notice and this permission notice shall be included in 
#all copies or substantial portions of the Software.

#THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
#IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
#THE SOFTWARE.

from ast import parse as _parse, Assert as _Assert, Pass as _Pass
from astunparse import unparse as _unparse
from contextlib import contextmanager as _contextmanager
import codecs as _codecs, re as _re

"""
A release-mode assertion disabler.  Lets you write all the inline assertions
you want for development and testing, but puts the fast version into the hands
of your users.

File "fail.py":

    # encoding: dissert
    def foo(x):
        print("oh no, I got called")
        assert x is not x

    if foo is not None:
        assert foo() is not None

    print("okay")

Include it without asserts (delete your `_pycache_`!):

    > from dissert import dissert
    > with dissert(True):
    >     import fail.py
    okay

Include it with asserts (delete your `_pycache_`!):

    > from dissert import dissert
    > with dissert(False):
    >     import fail.py
    oh no, I got called
    AssertionError: ...

Slap it on your module by renaming your `__init__.py` to `_init_.py` and
replacing it with a shim:

    from dissert import dissert
    from mymodule.__package_info__ import __release__
    with dissert(__release__):
        from mymodule._init_ import *

Of course, it will only remove asserts from marked files, but we can call
that a feature since it gives some control over which files are disserted. To
prove that it's a feature, we'll throw in an Assert function that works even
in affected files (but also goes away with `-O`)

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
"""

def Assert(check, msg):
    """def Assert(check, msg): assert check, msg"""
    assert check, msg

_pass = _Pass()
def _remove_asserts(tree):
    """
    replaces all Assert nodes in the input ast with Pass nodes, inplace.
    """
    stack = (tree.body, [], 0), ()
    while stack:
        (incoming, outgoing, i), stack = stack
        if i == len(incoming):
            incoming[:] = outgoing
            continue
        else:
            stack = (incoming, outgoing, i+1), stack
        node = incoming[i]
        if isinstance(node, _Assert):
            outgoing.append(_pass)
        else:
            outgoing.append(node)
            if hasattr(node, 'body'):
                stack = (node.body, [], 0), stack

_dissert = False    
_encoding_tag = _re.compile(b"^[ \t\f]*#.*?coding[:=][ \t]*[-_.a-zA-Z0-9]+")
def _decode(binary):
    """
    replaces all assert statements in a body of python code, unless the global
    value _dissert is False.
    """
    if _dissert:
        #strip out the character encoding to prevent loops
        lines = binary.tobytes().split(b'\n')
        if _encoding_tag.match(lines[0]) is not None:
            lines = lines[1:]
        elif len(lines) > 1 and _encoding_tag.match(lines[1]) is not None:
            lines = lines[:1] + lines[2:]
        binary = b'\n'.join(lines)
        tree = _parse(binary)
        _remove_asserts(tree)
        text = _unparse(tree)
    else:
        text = binary.tobytes().decode('utf-8')
    return text, len(text)

def _encode(text):
    raise NotImplementedError("Uhhhhhhh... I'm not putting asserts into your"
                              " code for you.")

_codecs.register(lambda name: _codecs.CodecInfo(_encode, _decode, name='dissert'))

def set_dissert(strip=True):
    """
    Turn assertions off (or on, if strip=False) for source files marked with
    the dissert character encoding.  Note that this can fail if a given module
    has already been imported since the last change to that module.  Delete 
    the __pycache__ for affected modules.
    """
    global _dissert
    _dissert = strip

@_contextmanager
def dissert(strip=False):
    """
    A context manager for selectively disabling inserts on includes within the
    managed context.  Note that this can fail if a given module has already
    been imported since the last change to that module.  Delete the __pycache__ 
    for affected modules.  

    Also note that this selectivity is controlled through a global variable,
    and calls made by nested imports may change the value of that global 
    variable.  This context restores the global state to what it was upon
    creation of the context.
    """
    global _dissert
    prev = _dissert
    _dissert = strip
    try:
        yield
    finally:
        _dissert = prev

