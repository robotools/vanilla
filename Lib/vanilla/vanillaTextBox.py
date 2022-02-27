from AppKit import NSTextField, NSAttributedString, NSTextAlignmentLeft, NSTextAlignmentRight, NSTextAlignmentCenter, NSTextAlignmentJustified, NSTextAlignmentNatural
from vanilla.vanillaBase import VanillaBaseControl


_textAlignmentMap = {
    "left": NSTextAlignmentLeft,
    "right": NSTextAlignmentRight,
    "center": NSTextAlignmentCenter,
    "justified": NSTextAlignmentJustified,
    "natural": NSTextAlignmentNatural,
}


class TextBox(VanillaBaseControl):

    """
    A rectangle containing static text.

    .. image:: /_images/TextBox.png

    ::

        from vanilla import Window, TextBox

        class TextBoxDemo:

             def __init__(self):
                 self.w = Window((100, 37))
                 self.w.textBox = TextBox((10, 10, -10, 17), "A TextBox")
                 self.w.open()

        TextBoxDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the text box.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 17        |
    +---------+---+-----------+
    | Small   | H | 14        |
    +---------+---+-----------+
    | Mini    | H | 12        |
    +---------+---+-----------+

    **text** The text to be displayed in the text box. If the object is a
    `NSAttributedString`_, the attributes will be used for display.

    **alignment** A string representing the desired visual alignment of the
    text in the text box. The options are:

    +-------------+-----------------------------------------------------+
    | "left"      | Text is aligned left.                               |
    +-------------+-----------------------------------------------------+
    | "right"     | Text is aligned right.                              |
    +-------------+-----------------------------------------------------+
    | "center"    | Text is centered.                                   |
    +-------------+-----------------------------------------------------+
    | "justified" | Text is justified.                                  |
    +-------------+-----------------------------------------------------+
    | "natural"   | Follows the natural alignment of the text's script. |
    +-------------+-----------------------------------------------------+

    **selectable** Boolean representing if the text is selectable or not.

    **sizeStyle** A string representing the desired size style of the button.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    .. _NSAttributedString: https://developer.apple.com/documentation/foundation/nsattributedstring?language=objc
    """

    nsTextFieldClass = NSTextField

    def __init__(self, posSize, text="", alignment="natural", selectable=False, sizeStyle="regular"):
        self._setupView(self.nsTextFieldClass, posSize)
        self._setSizeStyle(sizeStyle)
        if isinstance(text, NSAttributedString):
            self._nsObject.setAttributedStringValue_(text)
        else:
            self._nsObject.setStringValue_(text)
        self._nsObject.setDrawsBackground_(False)
        self._nsObject.setBezeled_(False)
        self._nsObject.setEditable_(False)
        self._nsObject.setSelectable_(selectable)
        self._nsObject.setAlignment_(_textAlignmentMap[alignment])

    def getNSTextField(self):
        """
        Return the `NSTextField`_ that this object wraps.

        .. _NSTextField: https://developer.apple.com/documentation/appkit/nstextfield?language=objc
        """
        return self._nsObject

    def get(self):
        """
        Get the contents of the text box.
        """
        return self._nsObject.stringValue()

    def set(self, value):
        """
        Set the contents of the text box.

        **value** A string representing the contents of the text box.
        """
        if isinstance(value, NSAttributedString):
            self._nsObject.setAttributedStringValue_(value)
        else:
            self._nsObject.setStringValue_(value)
