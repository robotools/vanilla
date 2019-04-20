import objc
from Foundation import NSObject
from AppKit import NSApp, NSWindow, NSPanel, NSScreen, NSWindowController, NSToolbar, NSToolbarItem, NSImage, NSNormalWindowLevel, NSFloatingWindowLevel, NSClosableWindowMask, NSMiniaturizableWindowMask, NSResizableWindowMask, NSTexturedBackgroundWindowMask, NSUnifiedTitleAndToolbarWindowMask, NSHUDWindowMask, NSUtilityWindowMask, NSTitledWindowMask, NSBorderlessWindowMask, NSBackingStoreBuffered, NSToolbarFlexibleSpaceItemIdentifier, NSToolbarSpaceItemIdentifier, NSToolbarSeparatorItemIdentifier, NSToolbarCustomizeToolbarItemIdentifier, NSToolbarPrintItemIdentifier, NSToolbarShowFontsItemIdentifier, NSToolbarShowColorsItemIdentifier, NSToolbarDisplayModeDefault, NSToolbarDisplayModeIconAndLabel, NSToolbarDisplayModeIconOnly, NSToolbarDisplayModeLabelOnly, NSToolbarSizeModeDefault, NSToolbarSizeModeRegular, NSToolbarSizeModeSmall


from vanilla.vanillaBase import _breakCycles, _calcFrame, _setAttr, _delAttr, _addConstraints, _flipFrame, \
        VanillaCallbackWrapper, VanillaError, VanillaBaseControl, osVersionCurrent, osVersion10_7, osVersion10_10
from vanilla.py23 import python_method

# PyObjC may not have these constants wrapped,
# so test and fallback if needed.
try:
    from AppKit import NSWindowCollectionBehaviorFullScreenPrimary, NSWindowCollectionBehaviorFullScreenAuxiliary
except ImportError:
    NSWindowCollectionBehaviorFullScreenPrimary = 1 << 7
    NSWindowCollectionBehaviorFullScreenAuxiliary = 1 << 8

try:
    from AppKit import NSWindowTitleVisible, NSWindowTitleHidden
except ImportError:
    NSWindowTitleVisible  = 0
    NSWindowTitleHidden = 1

try:
    from AppKit import NSFullSizeContentViewWindowMask
except ImportError:
    NSFullSizeContentViewWindowMask = 1 << 15


class Window(NSObject):

    """
    A window capable of containing controls.

    To add a control to a window, simply set it as an attribute of the window.::

        from vanilla import *

        class WindowDemo(object):

            def __init__(self):
                self.w = Window((200, 70), "Window Demo")
                self.w.myButton = Button((10, 10, -10, 20), "My Button")
                self.w.myTextBox = TextBox((10, 40, -10, 17), "My Text Box")
                self.w.open()

        WindowDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* representing the position and
    size of the window. It may also be a tuple of form *(width, height)*. In this case,
    the window will be positioned on screen automatically.

    **title** The title to be set in the title bar of the window.

    **minSize** Tuple of the form *(width, height)* representing the minimum size that
    the window can be resized to.

    **maxSize** Tuple of the form *(width, height)* representing the maximum size that
    the window can be resized to.

    **textured** Boolean value representing if the window should have a textured
    appearance or not.

    **autosaveName** A string representing a unique name for the window. If given,
    this name will be used to store the window position and size in the application preferences.

    **closable** Boolean value representing if the window should have a close button in the
    title bar.

    **miniaturizable** Boolean value representing if the window should have a minimize button
    in the title bar.

    **initiallyVisible** Boolean value representing if the window will be initially visible.
    Default is *True*. If *False*, you can show the window later by calling `window.show()`.

    **fullScreenMode** An indication of the full screen mode. These are the options:

    +---------------+---------------------------------------------------------------+
    | *None*        | The window does not allow full screen.                        |
    +---------------+---------------------------------------------------------------+
    | *"primary"*   | Corresponds to NSWindowCollectionBehaviorFullScreenPrimary.   |
    +---------------+---------------------------------------------------------------+
    | *"auxiliary"* | Corresponds to NSWindowCollectionBehaviorFullScreenAuxiliary. |
    +---------------+---------------------------------------------------------------+

    **titleVisible** Boolean value indicating if the window title should be displayed.

    **fullSizeContentView** Boolean value indicating if the content view should be the
    full size of the window, including the area underneath the titlebar and toolbar.

    **screen** A `NSScreen <http://tinyurl.com/NSScreen>`_ object indicating the screen that
    the window should be drawn to. When None the window will be drawn to the main screen.
    """

    def __new__(cls, *args, **kwargs):
        return cls.alloc().init()

    nsWindowStyleMask = NSTitledWindowMask | NSUnifiedTitleAndToolbarWindowMask
    nsWindowClass = NSWindow
    nsWindowLevel = NSNormalWindowLevel

    def __init__(self, posSize, title="", minSize=None, maxSize=None, textured=False,
                autosaveName=None, closable=True, miniaturizable=True, initiallyVisible=True,
                fullScreenMode=None, titleVisible=True, fullSizeContentView=False, screen=None):
        mask = self.nsWindowStyleMask
        if closable:
            mask = mask | NSClosableWindowMask
        if miniaturizable:
            mask = mask | NSMiniaturizableWindowMask
        if minSize or maxSize:
            mask = mask | NSResizableWindowMask
        if textured:
            mask = mask | NSTexturedBackgroundWindowMask
        if fullSizeContentView and osVersionCurrent >= osVersion10_10:
            mask = mask | NSFullSizeContentViewWindowMask
        # start the window
        ## too magical?
        if len(posSize) == 2:
            l = t = 100
            w, h = posSize
            cascade = True
        else:
            l, t, w, h = posSize
            cascade = False
        if screen is None:
            screen = NSScreen.mainScreen()
        frame = _calcFrame(screen.visibleFrame(), ((l, t), (w, h)))
        self._window = self.nsWindowClass.alloc().initWithContentRect_styleMask_backing_defer_screen_(
            frame, mask, NSBackingStoreBuffered, False, screen)
        if autosaveName is not None:
            # This also sets the window frame if it was previously stored.
            # Make sure we do this before cascading.
            self._window.setFrameAutosaveName_(autosaveName)
        if cascade:
            self._cascade()
        if minSize is not None:
            self._window.setMinSize_(minSize)
        if maxSize is not None:
            self._window.setMaxSize_(maxSize)
        self._window.setTitle_(title)
        self._window.setLevel_(self.nsWindowLevel)
        self._window.setReleasedWhenClosed_(False)
        self._window.setDelegate_(self)
        self._autoLayoutViews = {}
        self._bindings = {}
        self._initiallyVisible = initiallyVisible
        # full screen mode
        if osVersionCurrent >= osVersion10_7:
            if fullScreenMode is None:
                pass
            elif fullScreenMode == "primary":
                self._window.setCollectionBehavior_(NSWindowCollectionBehaviorFullScreenPrimary)
            elif fullScreenMode == "auxiliary":
                self._window.setCollectionBehavior_(NSWindowCollectionBehaviorFullScreenAuxiliary)
        # titlebar visibility
        if osVersionCurrent >= osVersion10_10:
            if not titleVisible:
                self._window.setTitleVisibility_(NSWindowTitleHidden)
            else:
                self._window.setTitleVisibility_(NSWindowTitleVisible)
        # full size content view
        if fullSizeContentView and osVersionCurrent >= osVersion10_10:
            self._window.setTitlebarAppearsTransparent_(True)

    def _testForDeprecatedAttributes(self):
        from warnings import warn
        if hasattr(self, "_nsWindowStyleMask"):
            warn(DeprecationWarning("The _nsWindowStyleMask attribute is deprecated. Use the nsWindowStyleMask attribute."))
            self.nsWindowStyleMask = self._nsWindowStyleMask
        if hasattr(self, "_nsWindowClass"):
            warn(DeprecationWarning("The _nsWindowClass attribute is deprecated. Use the nsWindowClass attribute."))
            self.nsWindowClass = self._nsWindowClass
        if hasattr(self, "_nsWindowLevel"):
            warn(DeprecationWarning("The _nsWindowLevel attribute is deprecated. Use the nsWindowLevel attribute."))
            self.nsWindowLevel = self._nsWindowLevel

    def _cascade(self):
        allLeftTop = []
        for other in NSApp().orderedWindows():
            if other == self._window:
                continue
            (oL, oB), (oW, oH) = other.frame()
            allLeftTop.append((oL, oB + oH))
        (sL, sB), (sW, sH) = self._window.frame()
        leftTop = sL, sB + sH
        while leftTop in allLeftTop:
            leftTop = self._window.cascadeTopLeftFromPoint_(leftTop)
        self._window.setFrameTopLeftPoint_(leftTop)

    def _breakCycles(self):
        _breakCycles(self._window.contentView())
        drawers = self._window.drawers()
        if drawers is not None:
            for drawer in drawers:
                _breakCycles(drawer.contentView())

    def _getContentView(self):
        return self._window.contentView()

    def __setattr__(self, attr, value):
        _setAttr(Window, self, attr, value)

    def __delattr__(self, attr):
        _delAttr(Window, self, attr)

    @python_method
    def assignToDocument(self, document):
        """
        Add this window to the list of windows associated with a document.

        **document** should be a *NSDocument* instance.
        """
        document.addWindowController_(self.getNSWindowController())

    def getNSWindow(self):
        """
        Return the *NSWindow* that this Vanilla object wraps.
        """
        return self._window

    def getNSWindowController(self):
        """
        Return an *NSWindowController* for the *NSWindow* that this Vanilla
        object wraps, creating a one if needed.
        """
        controller = self._window.windowController()
        if controller is None:
            controller = NSWindowController.alloc().initWithWindow_(self._window)
        return controller

    def open(self):
        """
        Open the window.
        """
        if self._window is None:
            raise ValueError("can't re-open a window")
        if self._initiallyVisible:
            self.show()
        # We retain ourselves to ensure we don't go away, even if our
        # caller doesn't keep a reference. It's balanced by a release
        # in windowWillClose_().
        self.retain()

    def close(self):
        """
        Close the window.

        Once a window has been closed it can not be re-opened.
        """
        if self._window.isSheet():
            NSApp().endSheet_(self._window)
            self._window.orderOut_(None)
        self._window.close()

    def hide(self):
        """
        Hide the window.
        """
        self._window.orderOut_(None)

    def show(self):
        """
        Show the window if it is hidden.
        """
        self._window.makeKeyAndOrderFront_(None)

    def makeKey(self):
        """
        Make the window the key window.
        """
        self._window.makeKeyWindow()

    def makeMain(self):
        """
        Make the window the main window.
        """
        self._window.makeMainWindow()

    @python_method
    def setTitle(self, title):
        """
        Set the title in the window's title bar.

        **title** should be a string.
        """
        self._window.setTitle_(title)

    def getTitle(self):
        """
        The title in the window's title bar.
        """
        return self._window.title()

    def select(self):
        """
        Select the window if it is not the currently selected window.
        """
        self._window.makeKeyWindow()

    def isVisible(self):
        """
        A boolean value representing if the window is visible or not.
        """
        return self._window.isVisible()

    def _calculateTitlebarHeight(self):
        # Note: this will include the toolbar height if there is one
        contentFrame = self._window.contentRectForFrameRect_(self._window.frame())
        windowFrame = self._window.frame()
        contentHeight = contentFrame.size[1]
        windowHeight = windowFrame.size[1]
        return windowHeight - contentHeight

    def getPosSize(self):
        """
        A tuple of form *(left, top, width, height)* representing the window's
        position and size.
        """
        frame = self._window.frame()
        l, t, w, h = _flipFrame(self._window.screen().visibleFrame(), frame)
        titlebarHeight = self._calculateTitlebarHeight()
        t += titlebarHeight
        h -= titlebarHeight
        return (l, t, w, h)

    @python_method
    def setPosSize(self, posSize, animate=True):
        """
        Set the position and size of the window.

        **posSize** A tuple of form *(left, top, width, height)*.
        """
        titlebarHeight = self._calculateTitlebarHeight()
        l, t, w, h = posSize
        t -= titlebarHeight
        h += titlebarHeight
        screenFrame = self._window.screen().visibleFrame()
        # if the top is less than zero, force it to zero.
        # otherwise the window will be thrown to the bottom
        # of the screen.
        if t < 0:
            t = 0
            # the screen frame could have a bottom
            # value that is not zero. this will cause
            # an error if (and only if) a window is
            # being positioned at the top of the screen.
            # so, adjust it.
            (sL, sB), (sW, sH) = screenFrame
            screenFrame = ((sL, 0), (sW, sH + sB))
        frame = _calcFrame(screenFrame, ((l, t), (w, h)), absolutePositioning=True)
        self._window.setFrame_display_animate_(frame, True, animate)

    def addLayoutConstraints(self, constraints, metrics=None):
        """
        Add auto layout contraints for controls/view in this view.
        **constraints** must by a list of strings that follow the
        `Visual Format Language <https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/VisualFormatLanguage.html#//apple_ref/doc/uid/TP40010853-CH27-SW1>`_.
        **metrics** may be either **None** or a dict containing
        key value pairs representing metrics keywords used in the
        constraints.
        """
        _addConstraints(self, constraints, metrics)

    def center(self):
        """
        Center the window within the screen.
        """
        self._window.center()

    @python_method
    def move(self, x, y, animate=True):
        """
        Move the window by **x** units and **y** units.
        """
        (l, b), (w, h) = self._window.frame()
        l = l + x
        b = b - y
        self._window.setFrame_display_animate_(((l, b), (w, h)), True, animate)

    @python_method
    def resize(self, width, height, animate=True):
        """
        Change the size of the window to **width** and **height**.
        """
        l, t, w, h = self.getPosSize()
        self.setPosSize((l, t, width, height), animate)

    @python_method
    def setDefaultButton(self, button):
        """
        Set the default button in the window.

        **button** will be bound to the Return and Enter keys.
        """
        if not isinstance(button, VanillaBaseControl):
            raise VanillaError("invalid object")
        cell = button._nsObject.cell()
        self._window.setDefaultButtonCell_(cell)

    @python_method
    def bind(self, event, callback):
        """
        Bind a callback to an event.

        **event** A string representing the desired event. The options are:

        +-------------------+----------------------------------------------------------------------+
        | *"should close"*  | Called when the user attempts to close the window. This must return  |
        |                   | a bool indicating if the window should be closed or not.             |
        +-------------------+----------------------------------------------------------------------+
        | *"close"*         | Called immediately before the window closes.                         |
        +-------------------+----------------------------------------------------------------------+
        | *"move"*          | Called immediately after the window is moved.                        |
        +-------------------+----------------------------------------------------------------------+
        | *"resize"*        | Called immediately after the window is resized.                      |
        +-------------------+----------------------------------------------------------------------+
        | *"became main"*   | Called immediately after the window has become the main window.      |
        +-------------------+----------------------------------------------------------------------+
        | *"resigned main"* | Called immediately after the window has lost its main window status. |
        +-------------------+----------------------------------------------------------------------+
        | *"became key"*    | Called immediately after the window has become the key window.       |
        +-------------------+----------------------------------------------------------------------+
        | *"resigned key"*  | Called immediately after the window has lost its key window status.  |
        +-------------------+----------------------------------------------------------------------+

        *For more information about main and key windows, refer to the Cocoa
        `documentation <http://developer.apple.com/documentation/Cocoa/Conceptual/WinPanel/Concepts/ChangingMainKeyWindow.html>`_
        on the subject.*

        **callback** The callback that will be called when the event occurs. It should accept a *sender* argument which will
        be the Window that called the callback.::

            from vanilla import Window

            class WindowBindDemo(object):

                def __init__(self):
                    self.w = Window((200, 200))
                    self.w.bind("move", self.windowMoved)
                    self.w.open()

                def windowMoved(self, sender):
                    print("window moved!", sender)

            WindowBindDemo()
        """
        if event not in self._bindings:
            self._bindings[event] = []
        self._bindings[event].append(callback)

    @python_method
    def unbind(self, event, callback):
        """
        Unbind a callback from an event.

        **event** A string representing the desired event.
        Refer to *bind* for the options.

        **callback** The callback that has been bound to the event.
        """
        self._bindings[event].remove(callback)

    @python_method
    def _alertBindings(self, key):
        # test to see if the attr exists.
        # this is necessary because NSWindow
        # can move the window (and therefore
        # call the delegate method which calls
        # this method) before the super
        # call in __init__ is complete.
        returnValues = []
        if hasattr(self, "_bindings"):
            if key in self._bindings:
                for callback in self._bindings[key]:
                    value = callback(self)
                    if value is not None:
                        # elimitate None return value
                        returnValues.append(value)
        return all(returnValues)

    def windowWillClose_(self, notification):
        self.hide()
        self._alertBindings("close")
        # remove all bindings to prevent circular refs
        if hasattr(self, "_bindings"):
            del self._bindings
        self._breakCycles()
        # We must make sure that the window does _not_ get deallocated during
        # windowWillClose_, or weird things happen, such as that the window
        # below this window doesn't always properly gets activated. (For reference:
        # this happens when closing with cmd-W, but not when clicking the close
        # control.)
        # Yet we want to get rid of the NSWindow object here, mostly as a flag
        # so we can disallow re-opening windows. So we retain/autorelease the
        # NSWindow, then get rid of our own reference.
        self._window.retain()
        self._window.autorelease()
        self._window = None    # make sure we can't re-open the window
        self.autorelease()     # see self.open()

    def windowDidBecomeKey_(self, notification):
        self._alertBindings("became key")

    def windowDidResignKey_(self, notification):
        self._alertBindings("resigned key")

    def windowDidBecomeMain_(self, notification):
        self._alertBindings("became main")

    def windowDidResignMain_(self, notification):
        self._alertBindings("resigned main")

    def windowDidMove_(self, notification):
        self._alertBindings("move")

    def windowDidResize_(self, notification):
        self._alertBindings("resize")

    def windowDidEnterFullScreen_(self, notification):
        self._alertBindings("enter full screen")

    def windowWillEnterFullScreen_(self, notification):
        self._alertBindings("will enter full screen")

    def windowDidExitFullScreen_(self, notification):
        self._alertBindings("exit full screen")

    def windowWillExitFullScreen_(self, notification):
        self._alertBindings("will exit full screen")

    def windowShouldClose_(self, notification):
        shouldClose = self._alertBindings("should close")
        if shouldClose is None:
            shouldClose = True
        return shouldClose

    # -------
    # Toolbar
    # -------

    # credit where credit is due: much of this was learned
    # from the PyObjC demo: WSTConnectionWindowControllerClass

    @python_method
    def addToolbar(self, toolbarIdentifier, toolbarItems, addStandardItems=True, displayMode="default", sizeStyle="default"):
        """
        Add a toolbar to the window.

        **toolbarIdentifier** A string representing a unique name for the toolbar.

        **toolbarItems** An ordered list of dictionaries containing the following items:

        +-------------------------------+---------------------------------------------------------------------------+
        | *itemIdentifier*              | A unique string identifier for the item. This is only used internally.    |
        +-------------------------------+---------------------------------------------------------------------------+
        | *label* (optional)            | The text label for the item. Defaults to *None*.                          |
        +-------------------------------+---------------------------------------------------------------------------+
        | *paletteLabel* (optional)     | The text label shown in the customization palette. Defaults to *label*.   |
        +-------------------------------+---------------------------------------------------------------------------+
        | *toolTip* (optional)          | The tool tip for the item. Defaults to *label*.                           |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imagePath* (optional)        | A file path to an image. Defaults to *None*.                              |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageNamed* (optional)       | The name of an image already loaded as a *NSImage* by the application.    |
        |                               | Defaults to *None*.                                                       |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageObject* (optional)      | A _NSImage_ object. Defaults to *None*.                                   |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageTemplate* (optional)    | A boolean representing if the image should converted to a template image. |
        +-------------------------------+---------------------------------------------------------------------------+
        | *selectable* (optional)       | A boolean representing if the item is selectable or not. The default      |
        |                               | value is _False_. For more information on selectable toolbar items, refer |
        |                               | to Apple's `documentation <http://tinyurl.com/SelectableItems>`_          |
        +-------------------------------+---------------------------------------------------------------------------+
        | *view* (optional)             | A *NSView* object to be used instead of an image. Defaults to *None*.     |
        +-------------------------------+---------------------------------------------------------------------------+
        | *visibleByDefault* (optional) | If the item should be visible by default pass True to this argument.      |
        |                               | If the item should be added to the toolbar only through the customization |
        |                               | palette, use a value of _False_. Defaults to _True_. |                    |
        +-------------------------------+---------------------------------------------------------------------------+

        **addStandardItems** A boolean, specifying whether the standard Cocoa toolbar items
        should be added. Defaults to *True*. If you set it to *False*, you must specify any
        standard items manually in *toolbarItems*, by using the constants from the AppKit module:

        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarSeparatorItemIdentifier*        | The Separator item.                                            |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarSpaceItemIdentifier*            | The Space item.                                                |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarFlexibleSpaceItemIdentifier*    | The Flexible Space item.                                       |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarShowColorsItemIdentifier*       | The Colors item. Shows the color panel.                        |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarShowFontsItemIdentifier*        | The Fonts item. Shows the font panel.                          |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarCustomizeToolbarItemIdentifier* | The Customize item. Shows the customization palette.           |
        +-------------------------------------------+----------------------------------------------------------------+
        | *NSToolbarPrintItemIdentifier*            | The Print item. Refer to Apple's *NSToolbarItem* documentation |
        |                                           | for more information.                                          |
        +-------------------------------------------+----------------------------------------------------------------+

        **displayMode** A string representing the desired display mode for the toolbar.

        +-------------+
        | "default"   |
        +-------------+
        | "iconLabel" |
        +-------------+
        | "icon"      |
        +-------------+
        | "label"     |
        +-------------+

        **sizeStyle** A string representing the desired size for the toolbar

        +-----------+
        | "default" |
        +-----------+
        | "regular" |
        +-----------+
        | "small"   |
        +-----------+

        Returns a dictionary containing the created toolbar items, mapped by itemIdentifier.
        """
        STANDARD_TOOLBAR_ITEMS = [
            NSToolbarFlexibleSpaceItemIdentifier,
            NSToolbarSpaceItemIdentifier,
            NSToolbarSeparatorItemIdentifier,
            NSToolbarCustomizeToolbarItemIdentifier,
            NSToolbarPrintItemIdentifier,
            NSToolbarShowFontsItemIdentifier,
            NSToolbarShowColorsItemIdentifier,
        ]
        # create the reference structures
        self._toolbarItems = {}
        self._toolbarDefaultItemIdentifiers = []
        self._toolbarAllowedItemIdentifiers = []
        self._toolbarCallbackWrappers = {}
        self._toolbarSelectableItemIdentifiers = []
        # create the toolbar items
        for itemData in toolbarItems:
            self._createToolbarItem(itemData)
        if addStandardItems:
            for standardItem in STANDARD_TOOLBAR_ITEMS:
                if standardItem not in self._toolbarAllowedItemIdentifiers:
                    self._toolbarAllowedItemIdentifiers.append(standardItem)
        # create the toolbar
        toolbar = NSToolbar.alloc().initWithIdentifier_(toolbarIdentifier)
        toolbar.setDelegate_(self)
        toolbar.setAllowsUserCustomization_(True)
        toolbar.setAutosavesConfiguration_(True)

        displayModeMap = dict(
                default=NSToolbarDisplayModeDefault,
                iconLabel=NSToolbarDisplayModeIconAndLabel,
                icon=NSToolbarDisplayModeIconOnly,
                label=NSToolbarDisplayModeLabelOnly,
                )
        toolbar.setDisplayMode_(displayModeMap[displayMode])

        sizeStyleMap = dict(
                default=NSToolbarSizeModeDefault,
                regular=NSToolbarSizeModeRegular,
                small=NSToolbarSizeModeSmall)
        toolbar.setSizeMode_(sizeStyleMap[sizeStyle])
        self._window.setToolbar_(toolbar)
        # Return the dict of toolbar items, so our caller can choose to
        # keep references to them if needed.
        return self._toolbarItems

    def getToolbarItems(self):
        if hasattr(self, "_toolbarItems"):
            return self._toolbarItems
        return {}

    @python_method
    def addToolbarItem(self, itemData, index=None):
        """
        Add a toolbar item to the windows toolbar.

        **itemData** item description with the same format as a toolbarItem description in `addToolbar`

        **index** An integer, specifying the place to insert the toolbar itemIdentifier.
        """
        if not hasattr(self, "_toolbarItems"):
            raise VanillaError("window has not toolbar")
        itemIdentifier = itemData.get("itemIdentifier")
        self._createToolbarItem(itemData)
        if itemData.get("visibleByDefault", True):
            if index is not None:
                self._toolbarDefaultItemIdentifiers.remove(itemIdentifier)
                self._toolbarDefaultItemIdentifiers.insert(index, itemIdentifier)
            index = self._toolbarDefaultItemIdentifiers.index(itemIdentifier)
            self._window.toolbar().insertItemWithItemIdentifier_atIndex_(itemIdentifier, index)

    @python_method
    def removeToolbarItem(self, itemIdentifier):
        """
        Remove a toolbar item by his identifier.

        **itemIdentifier** A unique string identifier for the removed item.
        """
        if not hasattr(self, "_toolbarItems"):
            raise VanillaError("window has not toolbar")
        if itemIdentifier not in self._toolbarItems:
            raise VanillaError("itemIdentifier %r not in toolbar" % itemIdentifier)
        item = self._toolbarItems[itemIdentifier]
        toolbarItems = self._window.toolbar().items()
        if item in toolbarItems:
            ## it can happen a user changed the toolbar manually
            index = toolbarItems.indexOfObject_(item)
            self._window.toolbar().removeItemAtIndex_(index)
        self._toolbarAllowedItemIdentifiers.remove(itemIdentifier)
        self._toolbarDefaultItemIdentifiers.remove(itemIdentifier)
        del self._toolbarItems[itemIdentifier]

    @python_method
    def _createToolbarItem(self, itemData):
        itemIdentifier = itemData.get("itemIdentifier")
        if itemIdentifier is None:
            raise VanillaError("toolbar item data must contain a unique itemIdentifier string")
        if itemIdentifier in self._toolbarItems:
            raise VanillaError("toolbar itemIdentifier is not unique: %r" % itemIdentifier)

        if itemIdentifier not in self._toolbarAllowedItemIdentifiers:
            self._toolbarAllowedItemIdentifiers.append(itemIdentifier)
        if itemData.get("visibleByDefault", True):
            self._toolbarDefaultItemIdentifiers.append(itemIdentifier)

        if itemIdentifier.startswith("NS"):
            # no need to create an actual item for a standard Cocoa toolbar item
            return

        label = itemData.get("label")
        paletteLabel = itemData.get("paletteLabel", label)
        toolTip = itemData.get("toolTip", label)
        imagePath = itemData.get("imagePath")
        imageNamed = itemData.get("imageNamed")
        imageObject = itemData.get("imageObject")
        imageTemplate = itemData.get("imageTemplate")
        view = itemData.get("view")
        callback = itemData.get("callback", None)
        # create the NSImage if needed
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        else:
            image = None
        toolbarItem = NSToolbarItem.alloc().initWithItemIdentifier_(itemIdentifier)
        toolbarItem.setLabel_(label)
        toolbarItem.setPaletteLabel_(paletteLabel)
        toolbarItem.setToolTip_(toolTip)
        if image is not None:
            if imageTemplate is not None:
                # only change the image template setting if its either True or False
                image.setTemplate_(imageTemplate)
            toolbarItem.setImage_(image)
        elif view is not None:
            toolbarItem.setView_(view)
            toolbarItem.setMinSize_(view.frame().size)
            toolbarItem.setMaxSize_(view.frame().size)
        if callback is not None:
            target = VanillaCallbackWrapper(callback)
            toolbarItem.setTarget_(target)
            toolbarItem.setAction_("action:")
            self._toolbarCallbackWrappers[itemIdentifier] = target
        if itemData.get("selectable", False):
            self._toolbarSelectableItemIdentifiers.append(itemIdentifier)
        self._toolbarItems[itemIdentifier] = toolbarItem

    # Toolbar delegate methods

    def toolbarDefaultItemIdentifiers_(self, anIdentifier):
        return self._toolbarDefaultItemIdentifiers

    def toolbarAllowedItemIdentifiers_(self, anIdentifier):
        return self._toolbarAllowedItemIdentifiers

    def toolbar_itemForItemIdentifier_willBeInsertedIntoToolbar_(self, toolbar, itemIdentifier, flag):
        return self._toolbarItems.get(itemIdentifier)

    def toolbarSelectableItemIdentifiers_(self, toolbar):
        return self._toolbarSelectableItemIdentifiers


class FloatingWindow(Window):

    """
    A window that floats above all other windows.

    To add a control to a window, simply set it as an attribute of the window.::

        from vanilla import *

        class FloatingWindowDemo(object):

            def __init__(self):
                self.w = FloatingWindow((200, 70), "FloatingWindow Demo")
                self.w.myButton = Button((10, 10, -10, 20), "My Button")
                self.w.myTextBox = TextBox((10, 40, -10, 17), "My Text Box")
                self.w.open()

        FloatingWindowDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the window. It may also be a tuple of form *(width, height)*.
    In this case, the window will be positioned on screen automatically.

    **title** The title to be set in the title bar of the window.

    **minSize** Tuple of the form *(width, height)* representing the minimum size
    that the window can be resized to.

    **maxSize** Tuple of the form *(width, height)* representing the maximum size
    that the window can be resized to.

    **textured** Boolean value representing if the window should have a textured
    appearance or not.

    **autosaveName** A string representing a unique name for the window. If given,
    this name will be used to store the window position and size in the application
    preferences.

    **closable** Boolean value representing if the window should have a close button
    in the title bar.

    **screen** A `NSScreen <http://tinyurl.com/NSScreen>`_ object indicating the screen that
    the window should be drawn to. When None the window will be drawn to the main screen.
    """

    nsWindowStyleMask = NSTitledWindowMask | NSUtilityWindowMask
    nsWindowClass = NSPanel
    nsWindowLevel = NSFloatingWindowLevel

    def __init__(self, posSize, title="", minSize=None, maxSize=None,
            textured=False, autosaveName=None, closable=True,
            initiallyVisible=True, screen=None):
        super(FloatingWindow, self).__init__(posSize, title, minSize, maxSize,
                textured, autosaveName, closable, initiallyVisible=initiallyVisible, screen=screen)
        self._window.setBecomesKeyOnlyIfNeeded_(True)

    def show(self):
        """
        Show the window if it is hidden.
        """
        # don't make key!
        self._window.orderFront_(None)


class HUDFloatingWindow(FloatingWindow):

    """
    A window that floats above all other windows and has the HUD appearance.

    To add a control to a window, simply set it as an attribute of the window.::

        from vanilla import *

        class HUDFloatingWindowDemo(object):

            def __init__(self):
                self.w = HUDFloatingWindow((200, 70), "HUDFloatingWindow Demo")
                self.w.myButton = Button((10, 10, -10, 20), "My Button")
                self.w.myTextBox = TextBox((10, 40, -10, 17), "My Text Box")
                self.w.open()

        HUDFloatingWindowDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* representing the position
    and size of the window. It may also be a tuple of form *(width, height)*.
    In this case, the window will be positioned on screen automatically.

    **title** The title to be set in the title bar of the window.

    **minSize** Tuple of the form *(width, height)* representing the minimum size
    that the window can be resized to.

    **maxSize** Tuple of the form *(width, height)* representing the maximum size
    that the window can be resized to.

    **textured** Boolean value representing if the window should have a textured
    appearance or not.

    **autosaveName** A string representing a unique name for the window. If given,
    this name will be used to store the window position and size in the application
    preferences.

    **closable** Boolean value representing if the window should have a close button
    in the title bar.

    **screen** A `NSScreen <http://tinyurl.com/NSScreen>`_ object indicating the screen that
    the window should be drawn to. When None the window will be drawn to the main screen.
    """

    nsWindowStyleMask = NSHUDWindowMask | NSUtilityWindowMask | NSTitledWindowMask | NSBorderlessWindowMask


class Sheet(Window):

    """
    A window that is attached to another window.

    To add a control to a sheet, simply set it as an attribute of the sheet.::

        from vanilla import *

        class SheetDemo(object):

            def __init__(self, parentWindow):
                self.w = Sheet((200, 70), parentWindow)
                self.w.myButton = Button((10, 10, -10, 20), "My Button")
                self.w.myTextBox = TextBox((10, 40, -10, 17), "My Text Box")
                self.w.open()

        SheetDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    **posSize** Tuple of form *(width, height)* representing the size of the sheet.

    **parentWindow** The window that the sheet should be attached to.

    **minSize** Tuple of the form *(width, height)* representing the minimum size that
    the sheet can be resized to.

    **maxSize** Tuple of the form *(width, height)* representing the maximum size that
    the sheet can be resized to.

    **autosaveName** A string representing a unique name for the sheet. If given,
    this name will be used to store the sheet size in the application preferences.
    """

    def __init__(self, posSize, parentWindow, minSize=None, maxSize=None,
            autosaveName=None):
        if isinstance(parentWindow, Window):
            parentWindow = parentWindow._window
        self.parentWindow = parentWindow
        textured = bool(parentWindow.styleMask() & NSTexturedBackgroundWindowMask)
        super(Sheet, self).__init__(posSize, "", minSize, maxSize, textured,
                autosaveName=autosaveName)

    def open(self):
        """
        Open the window.
        """
        parentWindow = self.parentWindow
        NSApp().beginSheet_modalForWindow_modalDelegate_didEndSelector_contextInfo_(
            self._window, parentWindow, None, None, 0)
        # See Window.open():
        self.retain()
