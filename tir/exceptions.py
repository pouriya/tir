"""
tir.exceptions
~~~~~~~~~~~~~~~~~~~
This module contains the set of Tir's exceptions.
"""

class TagNotFound(Exception):
    def __init__(self, tag, attr=None, value=None):
        text = 'could not found HTML tag {!r} '.format(tag)
        if attr:
            text += 'with attribute '
            if type(attr) == tuple:
                text += 'which should contain {!r} '.format(attr[0])
            else:
                text += '{!r} '.format(attr)
            text += 'and value '
            if type(value) == tuple:
                text += 'which should contain {!r}'.format(value[0])
            else:
                text += '{!r}'.format(value)
        Exception.__init__(self, text)
