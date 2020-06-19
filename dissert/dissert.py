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
from codecs import CodecInfo as _Codec, register as _register_codec
import re as _re

def Assert(check, msg):
    """
    This is a bypass function to provide assertions in otherwise disserted 
    code.  Note that it utilizes `assert`, so these assertions are still
    disabled by -O.  See ASSERT() for an unstoppable version.

    This function is not as efficient as a traditional `assert`, since it's
    wrapped in a function call.
    """
    assert check, msg

def ASSERT(check, msg):
    """
    This is a bypass function to provide assertions in otherwise disserted 
    code.  This does not use `assert`, so these assertions remain active even
    under -O.  See Assert() for a version that respects -O.

    This function is inefficient compared to a traditional `assert`, due to
    function overhead and emulation with `if ...: raise ...`.
    """
    if not check:
        raise AssertionError(str(msg))

_pass = _Pass()
def _ast_dissert(tree):
    """
    Replaces all Assert nodes in the input ast with Pass nodes, inplace.
    """
    stack = (tree.body, len(tree.body)-1), ()
    while stack:
        (body, i), stack = stack
        if i > 0:
            stack = (body, i-1), stack
        node = body[i]
        if isinstance(node, _Assert):
            body[i] = _pass
        elif hasattr(node, 'body'):
            stack = (node.body, len(node.body) - 1), stack

_encoding_tag = _re.compile(b"^[ \t\f]*#.*?coding[:=][ \t]*[-_.a-zA-Z0-9]+")
def _decode_dissert(binary):
    """
    Replaces all assert statements in a body of python code with `pass`.
    """
    #strip out the character encoding to prevent loops
    lines = binary.tobytes().split(b'\n')
    if _encoding_tag.match(lines[0]) is not None:
        lines = lines[1:]
    elif len(lines) > 1 and _encoding_tag.match(lines[1]) is not None:
        lines = lines[:1] + lines[2:]
    binary = b'\n'.join(lines)
    tree = _parse(binary)
    _ast_dissert(tree)
    return _unparse(tree)


_dissert = False    
def _decode_select(binary):
    """
    Replaces all assert statements in a body of python code with `pass`,
    unless the global value _dissert is False.
    """
    if _dissert:
        text = _decode_dissert(binary)
    else:
        text = binary.tobytes().decode('utf-8')
    return text, len(text)

def _nope_encoder(text):
    """
    Cowardly raises a NotImplementedError rather than adding asserts or
    (more sensibly) doing nothing with the text and re-encoding it to utf-8.
    The cowardly behavior is preferable in the case that somebody expects this
    function to restore assertions to their previously-disserted code.  
    """
    raise NotImplementedError("Uhhhhhhh... I'm not putting asserts into your"
                              " code for you.")

#register our encodings
_dissert_select = _Codec(_nope_encoder, _decode_select, name='dissert-select')
_register_codec(lambda name: _dissert_select)

_dissert = _Codec(_nope_encoder, _decode_dissert, name='dissert')
_register_codec(lambda name: _dissert)

def dissert_select(strip):
    """
    Turn assertions off (or on, if strip=False) for source files marked
    with the dissert-select character encoding.

    Note that this fails silently if a given module has already been
    imported since the last change to that module.  Delete the __pycache__
    for affected modules.

    Also note that this selectivity is controlled through a global 
    variable, and calls made by nested imports may change the value of 
    that global variable.  Use the `dissert_selector` context manager if
    this is important to you.
    """
    global _dissert
    _dissert = strip

class dissert_selector:
    def __init__(self, strip=True):
        """
        A context manager for selectively disabling assert on includes marked
        with the dissert-select character encoding within the managed context.

        Note that this fails silently if a given module has already been
        imported since the last change to that module.  Delete the __pycache__
        for affected modules.

        Also note that this selectivity is controlled through a global 
        variable, and calls made by nested imports may change the value of 
        that global variable.  This context restores the global state to what
        it was upon entry to the context.  This is naturally unstable
        according to import order.
        """
        self._strip = strip

    def __enter__(self):
        """
        Enters the context by storing the old value of the global _dissert and
        setting _dissert to this context's value.
        """
        global _dissert
        self._prev = _dissert
        _dissert = self._strip
        return self

    def __exit__(self, exc_type, exc_value, tb):
        """
        Exits the context by restoring the old value of the global _dissert.
        """
        global _dissert
        _dissert = self._prev
