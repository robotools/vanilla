from Foundation import NSObject
from objc import super

from AppKit import NSViewController,\
    NSTabViewController, NSTabView, NSTabViewItem,\
    NSTabPositionTop,\
    NSTabPositionNone,\
    NSNoTabsNoBorder,\
    NSViewControllerTransitionNone,\
    NSViewControllerTransitionCrossfade,\
    NSViewControllerTransitionSlideUp,\
    NSViewControllerTransitionSlideDown,\
    NSViewControllerTransitionSlideLeft,\
    NSViewControllerTransitionSlideRight,\
    NSViewControllerTransitionSlideForward,\
    NSViewControllerTransitionSlideBackward,\
    NSFont
from vanilla.vanillaBase import VanillaBaseObject, _breakCycles, _sizeStyleMap, VanillaCallbackWrapper, \
    _reverseSizeStyleMap, _recursiveSetFrame
from vanilla.nsSubclasses import getNSSubclass


class VanillaTabView(NSTabView):

    def viewDidMoveToWindow(self):
        if self.window() is not None:
            wrapper = self.vanillaWrapper()
            wrapper._positionViews()
        super().viewDidMoveToWindow()


class VanillaTabViewController(NSTabViewController):

    def tabView_didSelectTabViewItem_(self, tabView, tabViewItem):
        if hasattr(self, "_target"):
            self._target.action_(tabView.vanillaWrapper())
        super().tabView_didSelectTabViewItem_(tabView, tabViewItem)


class VanillaTabItem(VanillaBaseObject):

    nsTabViewItemClass = NSTabViewItem
    nsViewControllerClass = NSViewController

    def __init__(self, title):
        self._autoLayoutViews = {}
        self._tabItem = getNSSubclass(self.nsTabViewItemClass).alloc().initWithIdentifier_(title)
        self._tabItem.setVanillaWrapper_(self)
        self._tabItem.setLabel_(title)
        viewController = getNSSubclass(self.nsViewControllerClass).alloc().init()
        viewController.setView_(self._tabItem.view())
        self._tabItem.setViewController_(viewController)
        self._posSize = (0, 0, 0, 0)
        self._nsObject = self._tabItem.view()

    def getNSTabViewItem(self):
        return self._tabItem

    def _getContentView(self):
        return self._tabItem.view()

    def _breakCycles(self):
        self._nsObject = None
        _breakCycles(self._tabItem.view())
        self._autoLayoutViews.clear()


_tabTransitionMap = {
    None : NSViewControllerTransitionNone,
    "crossfade" : NSViewControllerTransitionCrossfade,
    "slideUp" : NSViewControllerTransitionSlideUp,
    "slideDown" : NSViewControllerTransitionSlideDown,
    "slideLeft" : NSViewControllerTransitionSlideLeft,
    "slideRight" : NSViewControllerTransitionSlideRight,
    "slideForward" : NSViewControllerTransitionSlideForward,
    "slideBackward" : NSViewControllerTransitionSlideBackward
}


class Tabs(VanillaBaseObject):

    """
    A set of tabs attached to a window. Each tab is capable of containing controls.

    .. image:: /_images/Tabs.png

    To add a control to a tab, simply set it as an attribute of the tab.

    ::

        from vanilla import Window, Tabs, TextBox

        class TabsDemo:

            def __init__(self):
                self.w = Window((250, 100))
                self.w.tabs = Tabs((10, 10, -10, -10), ["Tab One", "Tab Two"])
                tab1 = self.w.tabs[0]
                tab1.text = TextBox((10, 10, -10, -10), "This is tab 1")
                tab2 = self.w.tabs[1]
                tab2.text = TextBox((10, 10, -10, -10), "This is tab 2")
                self.w.open()

        TabsDemo()

    No special naming is required for the attributes. However, each attribute
    must have a unique name.

    To retrieve a particular tab, access it by index::

        myTab = self.w.tabs[0]

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing the position
    and size of the tabs.

    **titles** An ordered list of tab titles.

    **callback** The method to be called when the user selects a new tab.

    **sizeStyle** A string representing the desired size style of the tabs.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    **showTabs** Boolean representing if the tabview should display tabs.

    **transitionStyle** A string rerpresenting a transition style between tabs.
    The options are:

    +-----------------+
    | None            |
    +-----------------+
    | "crossfade"     |
    +-----------------+
    | "slideUp"       |
    +-----------------+
    | "slideDown"     |
    +-----------------+
    | "slideLeft"     |
    +-----------------+
    | "slideRight"    |
    +-----------------+
    | "slideForward"  |
    +-----------------+
    | "slideBackward" |
    +-----------------+

    """

    nsTabViewClass = VanillaTabView
    nsTabViewControllerClass = VanillaTabViewController
    vanillaTabViewItemClass = VanillaTabItem

    allFrameAdjustments = {
        # The sizeStyle will be part of the
        # className used for the lookup here.
        "Tabs-mini": (-7, -10, 14, 12),
        "Tabs-small": (-7, -10, 14, 13),
        "Tabs-regular": (-7, -10, 14, 16),
    }

    def __init__(self, posSize, titles=["Tab"], callback=None, sizeStyle="regular",
            showTabs=True, transitionStyle=None,
        ):
        self._setupView(self.nsTabViewClass, posSize, callback=None)
        self._nsObject.setVanillaWrapper_(self)
        self._tabViewController = getNSSubclass(self.nsTabViewControllerClass).alloc().init()
        self._tabViewController.setTabView_(self._nsObject)
        self._tabViewController.loadView()
        if not showTabs:
            self._nsObject.setTabPosition_(NSTabPositionNone)
            self._nsObject.setTabViewType_(NSNoTabsNoBorder)
        self._setSizeStyle(sizeStyle)
        self._tabViewController.setTransitionOptions_(_tabTransitionMap[transitionStyle])
        self._tabItems = []
        for title in titles:
            tab = self.vanillaTabViewItemClass(title)
            self._tabItems.append(tab)
            self._tabViewController.addTabViewItem_(tab._tabItem)
        # now that the tabs are all set, set the callback.
        # this is done because the callback will be called
        # while the tabs are being added.
        if callback is not None:
            self._setCallback(callback)

    def getNSTabView(self):
        """
        Return the `NSTabView`_ that this object wraps.

        .. _NSTabView: https://developer.apple.com/documentation/appkit/nstabview?language=objc
        """
        return self._nsObject

    _didPositionViews = False

    def _positionViews(self):
        if self._didPositionViews:
            return
        contentRect = self.getNSTabView().contentRect()
        # only do after the first because
        # adjusting the first gives it
        # incorrect positioning
        for item in self._tabItems[1:]:
            item._setFrame(contentRect)
            _recursiveSetFrame(item._nsObject)
        self._didPositionViews = True

    def _adjustPosSize(self, frame):
        if self._nsObject.tabViewType() == NSNoTabsNoBorder:
            return frame
        sizeStyle = _reverseSizeStyleMap[self._nsObject.controlSize()]
        tabsType = "Tabs-" + sizeStyle
        self.frameAdjustments = self.allFrameAdjustments[tabsType]
        return super()._adjustPosSize(frame)

    def _setCallback(self, callback):
        if callback is not None:
            self._target = VanillaCallbackWrapper(callback)
            delegate = self._nsObject.delegate()
            delegate._target = self._target

    def _setSizeStyle(self, value):
        value = _sizeStyleMap[value]
        self._nsObject.setControlSize_(value)
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(value))
        self._nsObject.setFont_(font)

    def __getitem__(self, index):
        return self._tabItems[index]

    def _breakCycles(self):
        super()._breakCycles()
        for item in self._tabItems:
            item._breakCycles()

    def get(self):
        """
        Get the index of the selected tab.
        """
        index = self._tabViewController.selectedTabViewItemIndex()
        return index

    def set(self, value):
        """
        Set the selected tab.

        **value** The index of the tab to be selected.
        """
        self._tabViewController.setSelectedTabViewItemIndex_(value)
