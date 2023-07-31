from AppKit import NSMatrix, NSRadioButton, NSButtonCell, NSRadioModeMatrix, NSFont, NSCellDisabled
from vanilla.vanillaBase import VanillaBaseControl, _sizeStyleMap
from vanilla.vanillaButton import Button
from vanilla.vanillaStackGroup import VerticalStackGroup, HorizontalStackGroup

try:
    from AppKit import NSRadioButtonType
except ImportError:
    from AppKit import NSRadioButton
    NSRadioButtonType = NSRadioButton


class _RadioGroupMixin(object):

    _heights = dict(
        regular=18,
        small=15,
        mini=12
    )

    def _init(self, cls, posSize, titles, callback=None, sizeStyle="regular"):
        spacing = self._spacing[sizeStyle]
        self._buttonHeight = self._heights[sizeStyle]
        self._callback = callback
        self._sizeStyle = sizeStyle
        super().__init__(posSize, spacing=spacing, alignment="leading")
        self._buildButtons(titles, sizeStyle)

    def _buildButtons(self, titles, sizeStyle):
        self._buttons = []
        for title in titles:
            button = RadioButton("auto", title, callback=self._buttonCallback, sizeStyle=sizeStyle)
            self._buttons.append(button)
            self.addView(button, height=self._buttonHeight)

    def _buttonCallback(self, sender):
        for button in self._buttons:
            if button != sender:
                button.set(False)
        if self._callback is not None:
            self._callback(self)

    def getFittingHeight(self):
        """
        Get the fitting height for all buttons in the group.
        """
        count = len(self._buttons)
        size = self._heights[self._sizeStyle]
        spacing = self._spacing[self._sizeStyle]
        height = size * count
        height += spacing * (count - 1)
        return height

    def get(self):
        """
        Get the index of the selected radio button.
        """
        for index, button in enumerate(self._buttons):
            if button.get():
                return index

    def set(self, index):
        """
        Set the index of the selected radio button.
        """
        for other, button in enumerate(self._buttons):
            button.set(other == index)


class VerticalRadioGroup(VerticalStackGroup, _RadioGroupMixin):

    """
    A vertical collection of radio buttons.

    .. image:: /_images/VerticalRadioGroup.png

    ::

        from vanilla import Window, VerticalRadioGroup

        class VerticalRadioGroupDemo:

            def __init__(self):
                self.w = Window((100, 100))
                self.w.radioGroup = VerticalRadioGroup(
                    "auto",
                    ["Option 1", "Option 2"],
                    callback=self.radioGroupCallback
                )
                self.w.radioGroup.set(0)
                rules = [
                    "H:|-[radioGroup]-|",
                    "V:|-[radioGroup(==%d)]-|" % self.w.radioGroup.getFittingHeight()
                ]
                self.w.addAutoPosSizeRules(rules)
                self.w.open()

            def radioGroupCallback(self, sender):
                print("radio group edit!", sender.get())

        VerticalRadioGroupDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the radio group.

    **titles** A list of titles to be shown next to the radio buttons.

    **callback** The method to be caled when a radio button is selected.

    **sizeStyle** A string representing the desired size style of the radio group.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    _spacing = dict(
        regular=2,
        small=2,
        mini=2
    )

    def __init__(self, posSize, titles, callback=None, sizeStyle="regular"):
        self._init(VerticalRadioGroup, posSize, titles, callback=callback, sizeStyle=sizeStyle)


class HorizontalRadioGroup(HorizontalStackGroup, _RadioGroupMixin):

    ### TODO: Example is not horizontal but vertical!

    """
    A horizontal collection of radio buttons.

    ::

        from vanilla import Window, HorizontalRadioGroup

        class RadioGroupDemo:

            def __init__(self):
                self.w = Window((300, 100))
                self.w.radioGroup = HorizontalRadioGroup(
                    "auto",
                    ["Option 1", "Option 2"],
                    callback=self.radioGroupCallback
                )
                self.w.radioGroup.set(0)
                rules = [
                    "H:|-[radioGroup]-|",
                    "V:|-[radioGroup(==%d)]-|" % self.w.radioGroup.getFittingHeight()
                ]
                self.w.addAutoPosSizeRules(rules)
                self.w.open()

            def radioGroupCallback(self, sender):
                print("radio group edit!", sender.get())

        RadioGroupDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the radio group.

    **titles** A list of titles to be shown next to the radio buttons.

    **callback** The method to be caled when a radio button is selected.

    **sizeStyle** A string representing the desired size style of the radio group.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    _spacing = dict(
        regular=4,
        small=3,
        mini=3
    )

    def __init__(self, posSize, titles, callback=None, sizeStyle="regular"):
        self._init(HorizontalRadioGroup, posSize, titles, callback=callback, sizeStyle=sizeStyle)


class RadioButton(Button):

    """
    A single radio button.
    """

    nsBezelStyle = None
    nsButtonType = NSRadioButtonType

    def __init__(self, posSize, title, value=False, callback=None, sizeStyle="regular"):
        super().__init__(posSize, title, callback=callback, sizeStyle=sizeStyle)
        self.set(value)

    def set(self, value):
        """
        Set the state of the radio button.

        **value** A boolean representing the state of the radio button.
        """
        self._nsObject.setState_(value)

    def get(self):
        """
        Get the state of the radio button.
        """
        return self._nsObject.state()


# ------
# Legacy
# ------

class RadioGroup(VanillaBaseControl):

    """
    A collection of radio buttons.

    .. image:: /_images/RadioGroup.png

    .. note:: This should be used only for frame layout.

    ::

        from vanilla import Window, RadioGroup

        class RadioGroupDemo:

            def __init__(self):
                self.w = Window((100, 60))
                self.w.radioGroup = RadioGroup((10, 10, -10, 40),
                                        ["Option 1", "Option 2"],
                                        callback=self.radioGroupCallback)
                self.w.radioGroup.set(0)
                self.w.open()

            def radioGroupCallback(self, sender):
                print("radio group edit!", sender.get())

        RadioGroupDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the radio group.

    **titles** A list of titles to be shown next to the radio buttons.

    **isVertical** Boolean representing if the radio group is
    vertical or horizontal.

    **callback** The method to be caled when a radio button is selected.

    **sizeStyle** A string representing the desired size style of the radio group.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsMatrixClass = NSMatrix
    nsCellClass = NSButtonCell

    def __init__(self, posSize, titles, isVertical=True, callback=None, sizeStyle="regular"):
        self._setupView(self.nsMatrixClass, posSize, callback=callback)
        self._isVertical = isVertical
        matrix = self._nsObject
        matrix.setMode_(NSRadioModeMatrix)
        matrix.setCellClass_(self.nsCellClass)
        # XXX! this does not work for vertical radio groups!
        matrix.setAutosizesCells_(True)
        # we handle the control size setting here
        # since the actual NS object is a NSMatrix
        cellSizeStyle = _sizeStyleMap[sizeStyle]
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(cellSizeStyle))
        # intercell spacing and cell spacing are based on the sizeStyle
        if posSize == "auto":
            w = 0
        else:
            w = posSize[2]
        if sizeStyle == "regular":
            matrix.setIntercellSpacing_((4.0, 2.0))
            matrix.setCellSize_((w, 18))
        elif sizeStyle == "small":
            matrix.setIntercellSpacing_((3.5, 2.0))
            matrix.setCellSize_((w, 15))
        elif sizeStyle == "mini":
            matrix.setIntercellSpacing_((3.0, 2.0))
            matrix.setCellSize_((w, 12))
        else:
            raise ValueError("sizeStyle must be 'regular', 'small' or 'mini'")
        for _ in range(len(titles)):
            if isVertical:
                matrix.addRow()
            else:
                matrix.addColumn()
        for title, cell in zip(titles, matrix.cells()):
            cell.setButtonType_(NSRadioButton)
            cell.setTitle_(title)
            cell.setControlSize_(cellSizeStyle)
            cell.setFont_(font)

    def _testForDeprecatedAttributes(self):
        super()._testForDeprecatedAttributes()
        from warnings import warn
        if hasattr(self, "_cellClass"):
            warn(DeprecationWarning("The _cellClass attribute is deprecated. Use the nsCellClass attribute."))
            self.nsCellClass = self._cellClass

    def getNSMatrix(self):
        """
        Return the `NSMatrix`_ that this object wraps.

        .. _NSMatrix: https://developer.apple.com/documentation/appkit/nsmatrix?language=objc
        """
        return self._nsObject

    def get(self):
        """
        Get the index of the selected radio button.
        """
        if self._isVertical:
            return self._nsObject.selectedRow()
        else:
            return self._nsObject.selectedColumn()

    def set(self, index):
        """
        Set the index of the selected radio button.
        """
        if self._isVertical:
            row = index
            column = 0
        else:
            row = 0
            column = index
        self._nsObject.selectCellAtRow_column_(row, column)

    def enableRadioButton(self, index, onOff=True):
        """
        Enable or disable a RadioGroup button specified by its index.
        """
        self._nsObject.cells()[index].setCellAttribute_to_(NSCellDisabled, not onOff)
