from AppKit import *
from vanilla import VanillaBaseObject, VanillaError, Group
from vanilla.externalFrameworks.RBSplitView import RBSplitView, RBSplitSubview


class VanillaRBSplitView(RBSplitView):

    def init(self):
        self = super(VanillaRBSplitView, self).initWithFrame_(((0, 0), (0, 0)))
        image = NSImage.imageNamed_("RBSplitViewThumb8")
        if image is not None:
            image.setFlipped_(True)
            self.setDivider_(image)
        return self

    def viewDidMoveToSuperview(self):
        vanillaWrapper = self.vanillaWrapper()
        if vanillaWrapper is not None and self.superview() is not None:
            vanillaWrapper._setupPanes()

    def _recurseThroughSubviews(self, view):
        if hasattr(view, "vanillaWrapper"):
            vanillaWrapper = view.vanillaWrapper()
            if vanillaWrapper is not None:
                posSize = vanillaWrapper.getPosSize()
                vanillaWrapper.setPosSize(posSize)
                for subview in view.subviews():
                    self._recurseThroughSubviews(subview)

    def viewDidMoveToWindow(self):
        for subview in self.subviews():
            if isinstance(subview, RBSplitSubview):
                for subsubview in subview.subviews():
                    self._recurseThroughSubviews(subsubview)


class SplitView(VanillaBaseObject):

    """
    View that can be split into two or more subviews with dividers.

    pre.
    from vanilla import *
     
    class SplitViewDemo(object):
     
        def __init__(self):
            self.w = Window((200, 200), "SplitView Demo", minSize=(100, 100))
            list1 = List((0, 0, -0, 100), ["A", "B", "C"])
            list2 = List((0, 0, -0, 100), ["a", "b", "c"])
            paneDescriptors = [
                dict(view=list1),
                dict(view=list2),
            ]
            self.w.splitView = SplitView((0, 0, -0, -0), paneDescriptors)
            self.w.open()
     
    SplitViewDemo()
    """

    rbSplitViewClass = VanillaRBSplitView

    def __init__(self, posSize, paneDescriptions, isVertical=True, dividerThickness=8, dividerImage="thumb"):
        """
        *posSize* Tuple of form (left, top, width, height) representing the position and size of the split view.

        *paneDescriptions* An ordered list of dictionaries describing the subviews, or "panes". Those dictionaries can have the following keys:

        | *view*          | A view, either a Vanilla object or a NSView. Required. |
        | *"identifier"*  | A string identifying the pane. Required. |
        | *"size"*        | The initial size of the pane. Optional. |
        | *"minSize"*     | The minimum size of the pane. Optional. The default is 1. |
        | *"maxSize"*     | The maximum size of the pane. Optional. The default is no maximum size. |
        | *"canCollapse"* | Boolean indicating if the pane can collapse. Optional. The default is True. |

        *isVertical* Boolean representing if the split view is vertical. Default is True.
        """
        self._haveSetupSubviews = False
        self._setupView(self.rbSplitViewClass, posSize)
        if dividerImage != "thumb":
            self._nsObject.setDivider_(dividerImage)
        self._nsObject.setDividerThickness_(dividerThickness)
        self._nsObject.setVertical_(isVertical)
        self._paneDescriptions = paneDescriptions

    def _breakCycles(self):
        self._paneDescriptions = None
        super(SplitView, self)._breakCycles()

    def _setupPanes(self):
        if self._haveSetupSubviews:
            return
        self._haveSetupSubviews = True
        rbSplitView = self._nsObject
        splitViewFrame = rbSplitView.frame()
        rbW, rbH = splitViewFrame.size
        isHorizontal = rbSplitView.isHorizontal()
        mask = NSViewWidthSizable | NSViewHeightSizable
        self._identifierToSubview = {}
        for paneDescription in self._paneDescriptions:
            # get the pane data
            view = paneDescription["view"]
            identifier = paneDescription["identifier"]
            size = paneDescription.get("size")
            minSize = paneDescription.get("minSize", 1)
            maxSize = paneDescription.get("maxSize", 0)
            canCollapse = paneDescription.get("canCollapse", True)
            # unwrap the view if necessary
            if isinstance(view, VanillaBaseObject):
                l, t, w, h = view._posSize
                view._setFrame(splitViewFrame)
                view = view._nsObject
                view.setAutoresizingMask_(mask)
            # wrap the view in an RBSplitSubview
            if not isinstance(view, RBSplitSubview):
                rbSplitSubview = RBSplitSubview.alloc().initWithFrame_(((0, 0), view.frame().size))
                rbSplitSubview.setAutoresizingMask_(mask)
                rbSplitSubview.addSubview_(view)
                view = rbSplitSubview
            # store the view
            assert identifier is not None
            assert identifier not in self._identifierToSubview
            self._identifierToSubview[identifier] = view
            # set the min and max dimensions
            if minSize is not None and maxSize is not None:
                view.setMinDimension_andMaxDimension_(minSize, maxSize)
            # set the collapse option
            view.setCanCollapse_(canCollapse)
            # set the identifier
            view.setIdentifier_(identifier)
            # add the subview
            rbSplitView.addSubview_(view)
        # work back through the panes
        for paneDescription in self._paneDescriptions:
            size = paneDescription.get("size")
            identifier = paneDescription["identifier"]
            if size is not None:
                view = self._nsObject.subviewWithIdentifier_(identifier)
                view.setDimension_(size)
        # tell the main view to adjust itself
        rbSplitView.adjustSubviews()

    def getRBSplitView(self):
        return self._nsObject

    def isPaneVisible(self, identifier):
        view = self._identifierToSubview[identifier]
        return bool(not view.isCollapsed())

    def showPane(self, identifier, onOff, animate=True):
        currentState = self.isPaneVisible(identifier)
        if currentState == onOff:
            return
        view = self._identifierToSubview[identifier]
        if not onOff:
            if animate:
                view.collapseWithAnimation()
            else:
                view.collapse()
        else:
            if animate:
                view.expandWithAnimation()
            else:
                view.expand()

    def togglePane(self, identifier, animate=True):
        currentState = self.isPaneVisible(identifier)
        self.showPane(identifier, not currentState, animate)
