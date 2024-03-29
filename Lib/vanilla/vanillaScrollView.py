from AppKit import NSScrollView, NSBezelBorder
from vanilla.vanillaBase import VanillaBaseObject


class ScrollView(VanillaBaseObject):

    """
    A view with scrollers for containing another view.

    .. image:: /_images/ScrollView.png

    ::

        from AppKit import NSView, NSColor, NSRectFill
        from vanilla import Window, ScrollView

        class DemoView(NSView):

            def drawRect_(self, rect):
                NSColor.redColor().set()
                NSRectFill(self.bounds())

        class ScrollViewDemo:

            def __init__(self):
                self.w = Window((200, 200))
                self.view = DemoView.alloc().init()
                self.view.setFrame_(((0, 0), (300, 300)))
                self.w.scrollView = ScrollView((10, 10, -10, -10),
                                        self.view)
                self.w.open()

        ScrollViewDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the scroll view.

    **nsView** A `NSView`_ object.

    **hasHorizontalScroller** Boolean representing if the scroll view has horizontal scrollers.

    **hasVerticalScroller** Boolean representing if the scroll view has vertical scrollers.

    **autohidesScrollers** Boolean representing if the scroll view auto-hides its scrollers.

    **backgroundColor** A `NSColor`_ object representing the background color of the scroll view.

    **drawsBackground** Boolean representing if the background should be drawn.

    .. _NSView: https://developer.apple.com/documentation/appkit/nsview?language=objc
    .. _NSColor: https://developer.apple.com/documentation/appkit/nscolor?language=objc
    """

    nsScrollViewClass = NSScrollView

    def __init__(self, posSize, nsView, hasHorizontalScroller=True, hasVerticalScroller=True,
                    autohidesScrollers=False, backgroundColor=None, clipView=None, drawsBackground=True):
        self._setupView(self.nsScrollViewClass, posSize)
        if clipView is not None:
            self._nsObject.setContentView_(clipView)
        self._nsObject.setDocumentView_(nsView)
        self._nsObject.setHasHorizontalScroller_(hasHorizontalScroller)
        self._nsObject.setHasVerticalScroller_(hasVerticalScroller)
        self._nsObject.setAutohidesScrollers_(autohidesScrollers)
        self._nsObject.setBorderType_(NSBezelBorder)
        if backgroundColor:
            self._nsObject.setBackgroundColor_(backgroundColor)
        self._nsObject.setDrawsBackground_(drawsBackground)

    def _testForDeprecatedAttributes(self):
        super()._testForDeprecatedAttributes()
        from warnings import warn
        if hasattr(self, "_scrollViewClass"):
            warn(DeprecationWarning("The _scrollViewClass attribute is deprecated. Use the nsScrollViewClass attribute."))
            self.nsScrollViewClass = self._scrollViewClass

    def getNSScrollView(self):
        """
        Return the `NSScrollView`_ that this object wraps.

        .. _NSScrollView: https://developer.apple.com/documentation/appkit/nsscrollview?language=objc
        """
        return self._nsObject

    def setBackgroundColor(self, color):
        """
        Set the background of the scrol view to *color*.
        """
        self._nsObject.setBackgroundColor_(color)

