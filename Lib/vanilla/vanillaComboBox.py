from AppKit import NSObject, NSComboBox
from objc import python_method
from vanilla.vanillaBase import VanillaBaseControl


class VanillaComboBoxDelegate(NSObject):

    _continuous = True

    @python_method
    def _callVanillaCallback(self, notification):
        obj = notification.object()
        target = obj.target()
        if target is not None:
            target.action_(obj)

    def controlTextDidChange_(self, notification):
        if self._continuous:
            self._callVanillaCallback(notification)

    def controlTextDidEndEditing_(self, notification):
        if not self._continuous:
            self._callVanillaCallback(notification)

    def comboBoxSelectionDidChange_(self, notification):
        obj = notification.object()
        obj.setObjectValue_(obj.objectValueOfSelectedItem())
        self._callVanillaCallback(notification)


class ComboBox(VanillaBaseControl):

    """
    A text entry control that allows direct text entry or selection for a list
    of options.

    .. image:: /_images/ComboBox.png

    ::

        from vanilla import Window, ComboBox

        class ComboBoxDemo:

            def __init__(self):
                self.w = Window((100, 41))
                self.w.comboBox = ComboBox((10, 10, -10, 21),
                                    ["AA", "BB", "CC", "DD"],
                                    callback=self.comboBoxCallback)
                self.w.open()

            def comboBoxCallback(self, sender):
                print("combo box entry!", sender.get())

        ComboBoxDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the combo box control. The size of
    the combo box should match the appropriate value for the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +-----------+---+-----------+
    | *Regular* | H | 21        |
    +-----------+---+-----------+
    | *Small*   | H | 17        |
    +-----------+---+-----------+
    | *Mini*    | H | 14        |
    +-----------+---+-----------+

    **items** The items to be displayed in the combo box.

    **completes** Boolean representing if the combo box auto completes
    entered text.

    **continuous** If *True*, the callback (if any) will be called upon each
    keystroke, if *False*, only call the callback when editing finishes or
    after item selection. Default is *False*.

    **callback** The method to be called when the user enters text.

    **formatter** A `NSFormatter`_ for controlling the display and input of
    the text entry.

    **sizeStyle** A string representing the desired size style of the combo box.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    .. _NSFormatter: https://developer.apple.com/documentation/foundation/nsformatter?language=objc
    """

    nsComboBoxClass = NSComboBox

    frameAdjustments = {
        "mini": (0, -4, 1, 5),
        "small": (0, -4, 3, 5),
        "regular": (0, -3, 3, 5),
    }

    def __init__(self, posSize, items, completes=True, continuous=False,
            callback=None, formatter=None, sizeStyle="regular"):
        self._continuous = continuous
        self._setupView(self.nsComboBoxClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.addItemsWithObjectValues_(items)
        self._nsObject.setCompletes_(completes)
        if formatter is not None:
            self._nsObject.setFormatter_(formatter)

    def _breakCycles(self):
        super()._breakCycles()
        self._delegate = None

    def _setCallback(self, callback):
        super()._setCallback(callback)
        if callback is not None:
            self._delegate = VanillaComboBoxDelegate.alloc().init()
            self._delegate._continuous = self._continuous
            self._nsObject.setDelegate_(self._delegate)

    def getNSComboBox(self):
        """
        Return the `NSComboBox`_ that this object wraps.

        .. _NSComboBox: https://developer.apple.com/documentation/appkit/nscombobox?language=objc
        """
        return self._nsObject

    def get(self):
        """
        Get the text entered in the combo box.
        """
        return self._nsObject.objectValue()

    def set(self, value):
        """
        Set the text in the text field of the combo box.

        **value** A string to set in the combo box.
        """
        self._nsObject.setObjectValue_(value)

    def setItems(self, items):
        """
        Set the items in the combo box list.

        **items** A list of strings to set in the combo box list.
        """
        self._nsObject.removeAllItems()
        self._nsObject.addItemsWithObjectValues_(items)

    def getItems(self):
        """
        Get the items in the combo box as a list.
        """
        return list(self._nsObject.objectValues())
