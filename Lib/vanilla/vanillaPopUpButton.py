from AppKit import NSPopUpButton, NSPopUpButtonCell, NSMenuItem, NSImageNameActionTemplate, NSImage, NSMenu, NSTexturedRoundedBezelStyle
from vanilla.vanillaBase import VanillaBaseControl, VanillaCallbackWrapper, _reverseSizeStyleMap
from vanilla.vanillaList import VanillaMenuBuilder


class PopUpButton(VanillaBaseControl):

    """
    A button which, when selected, displays a list of items for the user to choose from.

    .. image:: /_images/PopUpButton.png

    ::

        from vanilla import Window, PopUpButton

        class PopUpButtonDemo:

            def __init__(self):
                self.w = Window((100, 40))
                self.w.popUpButton = PopUpButton((10, 10, -10, 20),
                                      ["A", "B", "C"],
                                      callback=self.popUpButtonCallback)
                self.w.open()

            def popUpButtonCallback(self, sender):
                print("pop up button selection!", sender.get())

        PopUpButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the pop up button. The size of the button should match
    the appropriate value for the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +-----------+---+-----------+
    | *Regular* | H | 20        |
    +-----------+---+-----------+
    | *Small*   | H | 17        |
    +-----------+---+-----------+
    | *Mini*    | H | 15        |
    +-----------+---+-----------+

    **items** A list of items to appear in the pop up list.

    **callback** The method to be called when the user selects an item in the
    pop up list.

    **sizeStyle** A string representing the desired size style of the pop up button.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsPopUpButtonClass = NSPopUpButton
    nsPopUpButtonCellClass = NSPopUpButtonCell

    frameAdjustments = {
        "mini": (-1, 0, 3, 0),
        "small": (-3, -4, 6, 5),
        "regular": (-3, -4, 6, 6),
    }

    def __init__(self, posSize, items, callback=None, sizeStyle="regular"):
        self._setupView(self.nsPopUpButtonClass, posSize)
        if self.nsPopUpButtonCellClass != NSPopUpButtonCell:
            self._nsObject.setCell_(self.nsPopUpButtonCellClass.alloc().init())
        if callback is not None:
            self._setCallback(callback)
        self._setSizeStyle(sizeStyle)
        self.setItems(items)

    def getNSPopUpButton(self):
        """
        Return the `NSPopUpButton`_ that this object wraps.

        .. _NSPopUpButton: https://developer.apple.com/documentation/appkit/nspopupbutton?language=objc
        """
        return self._nsObject

    def get(self):
        """
        Get the index selected item in the pop up list.
        """
        return self._nsObject.indexOfSelectedItem()

    def set(self, value):
        """
        Set the index of the selected item in the pop up list.
        """
        self._nsObject.selectItemAtIndex_(value)

    def getItem(self):
        """
        Get the selected item title in the pop up list.
        """
        return self._nsObject.titleOfSelectedItem()

    def setItem(self, item):
        """
        Set the selected item title in the pop up list.
        """
        self._nsObject.selectItemWithTitle_(item)

    def setItems(self, items):
        """
        Set the items to appear in the pop up list.
        """
        self._nsObject.removeAllItems()
        for item in items:
            if isinstance(item, NSMenuItem):
                menu = self._nsObject.menu()
                menu.addItem_(item)
            else:
                self._nsObject.addItemWithTitle_(item)

    def getItems(self):
        """
        Get the list of items that appear in the pop up list.
        """
        return self._nsObject.itemTitles()


class ActionButton(PopUpButton):

    """
    An action button with a menu.

    .. image:: /_images/ActionButton.png

    ::

        from vanilla import Window, ActionButton

        class ActionPopUpButtonDemo:

            def __init__(self):
                self.w = Window((100, 40))
                items = [
                        dict(title="first", callback=self.firstCallback),
                        dict(title="second", callback=self.secondCallback),
                        dict(title="third", items=[
                                dict(title="sub first", callback=self.subFirstCallback)
                            ])
                        ]
                self.w.actionPopUpButton = ActionButton((10, 10, 30, 20), items)
                self.w.open()

            def firstCallback(self, sender):
                print("first")

            def secondCallback(self, sender):
                print("second")

            def subFirstCallback(self, sender):
                print("sub first")

        ActionPopUpButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the pop up button. The size of the button should match
    the appropriate value for the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +-----------+---+-----------+
    | *Regular* | H | 20        |
    +-----------+---+-----------+
    | *Small*   | H | 17        |
    +-----------+---+-----------+
    | *Mini*    | H | 15        |
    +-----------+---+-----------+

    **items** A list of items to appear in the pop up list as dictionaries.
    Optionally an item could be a `NSMenuItem`_.
    When an item is set to ``----``, it will be a menu item separator.

    +------------+----------------------------------------------+
    | "title"    | The title of the item.                       |
    +------------+----------------------------------------------+
    | "callback" | The callback of the item.                    |
    +------------+----------------------------------------------+
    | "items"    | Each item could have sub menus, as list of   |
    |            | dictionaries with the same format.           |
    +------------+----------------------------------------------+

    **sizeStyle** A string representing the desired size style of the pop up button.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    **bordered** Boolean representing if the button should be bordered.

    .. _NSMenuItem: https://developer.apple.com/documentation/appkit/nsmenuitem?language=objc
    """

    def __init__(self, posSize, items, sizeStyle="regular", bordered=True):
        super().__init__(posSize, items, sizeStyle=sizeStyle)
        self._nsObject.setPullsDown_(True)
        self._nsObject.setBezelStyle_(NSTexturedRoundedBezelStyle)
        self._nsObject.setBordered_(bordered)

    def _breakCycles(self):
        self._menuItemCallbackWrappers = None
        super()._breakCycles()

    def getFirstItem(self):
        actionImage = NSImage.imageNamed_(NSImageNameActionTemplate).copy()
        sizeStyle = _reverseSizeStyleMap[self._nsObject.cell().controlSize()]
        if sizeStyle == "small":
            actionImage.setSize_((10, 10))
        elif sizeStyle == "mini":
            actionImage.setSize_((10, 10))
        firstActionItem = NSMenuItem.alloc().init()
        firstActionItem.setImage_(actionImage)
        firstActionItem.setTitle_("")
        return firstActionItem

    def setItems(self, items):
        """
        Set the items to appear in the pop up list.
        """
        self._callbackWrappers = []
        self._nsObject.removeAllItems()
        menu = NSMenu.alloc().init()
        menu.addItem_(self.getFirstItem())
        VanillaMenuBuilder(self, items, menu)
        self._nsObject.setMenu_(menu)
