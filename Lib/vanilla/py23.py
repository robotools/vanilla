__all__ = ['basestring', 'unicode', 'long']

try:
    basestring = basestring
except NameError:
    basestring = str

try:
    unicode = unicode
except NameError:
    unicode = str

try:
    long = long
except NameError:
    long = int

try:
    range = xrange
except NameError:
    range = range
