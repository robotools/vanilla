__all__ = ['basestring', 'unicode', 'long', 'python_method']

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

try:
    unichr = unichr
except NameError:
    unichr = chr

try:
    from objc import python_method
except ImportError:
    def python_method(arg):
        return arg
try:
    print "import NSLayoutAttributeLastBaseline"
    from AppKit import NSLayoutAttributeLastBaseline
except ImportError:
    import AppKit
    AppKit.NSLayoutAttributeLastBaseline = 11
    AppKit.NSLayoutAttributeFirstBaseline = 12