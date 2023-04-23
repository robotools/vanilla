from objc import super
from AppKit import NSBox, NSColor, NSFont, NSSmallControlSize, NSNoTitle, NSLineBorder, NSBoxSeparator, NSBoxCustom
from vanilla.vanillaBase import VanillaBaseObject, _breakCycles, osVersionCurrent, osVersion10_10


class Box(VanillaBaseObject):

    """
    A bordered container for other controls.

    .. image:: /_images/Box.png

    To add a control to a box, simply set it as an attribute of the box.

    ::

        from vanilla import Window, Box, TextBox

        class BoxDemo:

            def __init__(self):
                self.w = Window((150, 70))
                self.w.box = Box((10, 10, -10, -10))
                self.w.box.text = TextBox((10, 10, -10, -10), "This is a box")
                self.w.open()

        BoxDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the box.

    **title** The title to be displayed above the box. Pass *None* if no title is desired.
    """

    allFrameAdjustments = {
        # Box does not have sizeStyle, but the
        # adjustment is differeent based on the
        # presence of a title.
        "Box-Titled": (-3, -4, 6, 4),
        "Box-None": (-3, -4, 6, 6)
    }
    _ignoreFrameAdjustments = False

    nsBoxClass = NSBox

    def __init__(self, posSize, title=None,
            fillColor=None, borderColor=None, borderWidth=None,
            cornerRadius=None, margins=None
        ):
        self._ignoreFrameAdjustments = set((fillColor, borderColor, borderWidth, cornerRadius)) != set((None,))
        self._setupView(self.nsBoxClass, posSize)
        if title:
            self._nsObject.setTitle_(title)
            if osVersionCurrent < osVersion10_10:
                self._nsObject.titleCell().setTextColor_(NSColor.blackColor())
            font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize))
            self._nsObject.setTitleFont_(font)
        else:
            self._nsObject.setTitlePosition_(NSNoTitle)
        if fillColor is not None:
            self.setFillColor(fillColor)
        if borderColor is not None:
            self.setBorderColor(borderColor)
        if borderWidth is not None:
            self.setBorderWidth(borderWidth)
        if cornerRadius is not None:
            self.setCornerRadius(cornerRadius)
        if margins is not None:
            self.setMargins(margins)

    def getNSBox(self):
        """
        Return the `NSBox`_ that this object wraps.

        .. _NSBox: https://developer.apple.com/documentation/appkit/nsbox?language=objc
        """
        return self._nsObject

    def _adjustPosSize(self, frame):
        if self._ignoreFrameAdjustments:
            self.frameAdjustments = (0, 0, 0, 0)
        # skip subclasses
        elif self.__class__.__name__ == "Box":
            pos = self._nsObject.titlePosition()
            if pos != NSNoTitle:
                title = "Titled"
            else:
                title = "None"
            boxType = "Box-" + title
            self.frameAdjustments = self.allFrameAdjustments[boxType]
        return super()._adjustPosSize(frame)

    def _getContentView(self):
        return self._nsObject.contentView()

    def _breakCycles(self):
        super()._breakCycles()
        view = self._nsObject.contentView()
        if view is not None:
            _breakCycles(view)

    def setTitle(self, title):
        """
        Set the title of the box.
        """
        self._nsObject.setTitle_(title)

    def getTitle(self):
        """
        Get the title of the box.
        """
        return self._nsObject.title()

    def setFillColor(self, color):
        """
        Set the fill color of the box.
        """
        self._nsObject.setBoxType_(NSBoxCustom)
        self._nsObject.setFillColor_(color)

    def setBorderColor(self, color):
        """
        Set the border color of the box.
        """
        self._nsObject.setBoxType_(NSBoxCustom)
        self._nsObject.setBorderColor_(color)

    def setBorderWidth(self, value):
        """
        Set the border width of the box.
        """
        self._nsObject.setBoxType_(NSBoxCustom)
        self._nsObject.setBorderWidth_(value)

    def setCornerRadius(self, value):
        """
        Set the corner radius of the box.
        """
        self._nsObject.setBoxType_(NSBoxCustom)
        self._nsObject.setCornerRadius_(value)

    def setMargins(self, value):
        """
        Set the x, y margins for the content.
        """
        if isinstance(value, int):
            value = (value, value)
        self._nsObject.setContentViewMargins_(value)
        self._nsObject.sizeToFit()

class _Line(Box):

    nsBoxClass = NSBox

    def __init__(self, posSize):
        self._setupView(self.nsBoxClass, posSize)
        self._nsObject.setBorderType_(NSLineBorder)
        self._nsObject.setBoxType_(NSBoxSeparator)
        self._nsObject.setTitlePosition_(NSNoTitle)

    def _getContentView(self):
        return self._nsObject


class HorizontalLine(_Line):

    """
    A horizontal line.

    .. image:: /_images/HorizontalLine.png

    ::

        from vanilla import Window, HorizontalLine

        class HorizontalLineDemo:

            def __init__(self):
                self.w = Window((100, 20))
                self.w.line = HorizontalLine((10, 10, -10, 1))
                self.w.open()

        HorizontalLineDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the line.

    +-------------------------+
    | **Standard Dimensions** |
    +===+=====================+
    | H | 1                   |
    +---+---------------------+
    """

    def __init__(self, posSize):
        super().__init__(posSize)


class VerticalLine(_Line):

    """
    A vertical line.

    .. image:: /_images/VerticalLine.png

    ::

        from vanilla import Window, VerticalLine

        class VerticalLineDemo:

            def __init__(self):
                self.w = Window((80, 100))
                self.w.line = VerticalLine((40, 10, 1, -10))
                self.w.open()

        VerticalLineDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the line.

    +-------------------------+
    | **Standard Dimensions** |
    +===+=====================+
    | V | 1                   |
    +---+---------------------+
    """

    def __init__(self, posSize):
        super().__init__(posSize)
