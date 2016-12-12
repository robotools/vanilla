__all__ = ['unicode', 'long']

# In Python 3, unicode == str, and long == int
try:
    unicode = unicode
except NameError:
    unicode = str
try:
    long = long
except NameError:
    long = int
