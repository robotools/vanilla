from warnings import warn
from AppKit import *
from vanillaBase import VanillaBaseObject

import objc
objc.setVerbose(True)


_dividerStyleMap = {
    "splitter": NSSplitViewDividerStylePaneSplitter,
    "thin": NSSplitViewDividerStyleThin,
    "thick": NSSplitViewDividerStyleThick
}


class VanillaSplitViewSubclass(NSSplitView):

    _dividerThickness = None

    def viewDidMoveToWindow(self):
        self.delegate().splitViewInitialSizing_(self)

    # Divider

    def dividerThickness(self):
        if self._dividerThickness is None:
            return super(VanillaSplitViewSubclass, self).dividerThickness()
        return self._dividerThickness

    def setDividerThickness_(self, value):
        self._dividerThickness = value

    # def drawDividerInRect_(self, rect):

    # Pane Visibility

    def getStateForPane_(self, identifier):
        wrapper = self.vanillaWrapper()
        paneDescription = wrapper._identifierToPane[identifier]
        view = paneDescription["nsView"]
        return view.isHidden()

    def setState_forPane_(self, onOff, identifier):
        # already have the desired state
        isVisible = self.getStateForPane_(identifier)
        if isVisible == onOff:
            return
        # get the subview
        wrapper = self.vanillaWrapper()
        paneDescription = wrapper._identifierToPane[identifier]
        view = paneDescription["nsView"]
        # set its visibility
        view.setHidden_(onOff)
        # apply the size adjustments
        if self.isVertical():
            sizeChange = view.frame().size.width
        else:
            sizeChange = view.frame().size.height
        if not onOff:
            sizeChange = -sizeChange
        self.delegate().splitView_applyPaneSizeChange_wifthFrameSize_ignoreView_(
            self,
            sizeChange,
            self.frame().size,
            view
        )
        # adjust the other views
        self.adjustSubviews()


class VanillaSplitViewDelegate(NSObject):

    # Initial Sizing

    def splitViewInitialSizing_(self, splitView):
        # NSSplitView is pretty dumb at first. It's going to ignore pane widths
        # and adjust things willy-nilly to make everything flush in the view.
        # So, we need to loop through the views and try to flush them out
        # before NSSplitView clumsily resizes everything.
        # 
        # This doesn't catch all edge cases, but we'll let NSView handle those.
        # Plus, at that point, it's the responsibility of the entity that set the
        # pane sizes to make sure that they aren't doing anything crazy.
        wrapper = splitView.vanillaWrapper()
        paneDescriptions = wrapper._paneDescriptions
        identifierToPane = wrapper._identifierToPane
        # make a storage location for all view sizes
        viewSizes = {}
        # figure out the desired size, gather views into groups
        # depending on their size settings
        if splitView.isVertical():
            splitViewSize = splitView.frame().size[0]
        else:
            splitViewSize = splitView.frame().size[1]
        hiddenViews = []
        fixedSizeViews = []
        desiredSizeViews = []
        minMaxViews = []
        flexibleViews = []
        for paneDescription in paneDescriptions:
            identifier = paneDescription["identifier"]
            size = paneDescription["size"]
            if size == 0:
                hiddenViews.append(identifier)
                viewSizes[identifier] = size
            elif paneDescription["fixedSize"]:
                fixedSizeViews.append(identifier)
                viewSizes[identifier] = size
            elif size is not None:
                fixedSizeViews.append(identifier)
                viewSizes[identifier] = size
            elif paneDescription["minSize"] or paneDescription["maxSize"]:
                if paneDescription["minSize"]:
                    viewSizes[identifier] = paneDescription["minSize"]
                else:
                    viewSizes[identifier] = 0
                minMaxViews.append(identifier)
            else:
                flexibleViews.append(identifier)
                viewSizes[identifier] = 0
        # calculate the amount of space needed to balance everything out
        dividerThickness = (len(paneDescriptions) - 1) * splitView.dividerThickness()
        desiredSize = sum(viewSizes.values()) + dividerThickness
        remainder = splitViewSize - desiredSize
        viewAdjustment = int(round(remainder / (len(minMaxViews) + len(flexibleViews))))
        # now apply the difference to minMaxViews respecting the min/max values
        for identifier in minMaxViews:
            for paneDescription in paneDescriptions:
                if paneDescription["identifier"] == identifier:
                    break
            minSize = paneDescription["minSize"]
            if minSize is None:
                minSize = 0
            maxSize = paneDescription["maxSize"]
            size = viewSizes[identifier]
            test = size + viewAdjustment
            if test < minSize:
                continue
            elif maxSize is not None and test > maxSize:
                continue
            viewSizes[identifier] = test
        # recalculate the remainder
        remainder = splitViewSize - desiredSize
        viewAdjustment = int(round(remainder / (len(minMaxViews) + len(flexibleViews))))
        # apply to the flexible views
        for identifier in flexibleViews:
            viewSizes[identifier] += viewAdjustment
        # now set the view sizes
        isVertical = splitView.isVertical()
        for identifier, size in viewSizes.items():
            view = identifierToPane[identifier]["nsView"]
            w, h = view.frame().size
            if isVertical:
                w = size
            else:
                h = size
            view.setFrame_(((0, 0), (w, h)))
        # tell NSSplitView to mess everything up
        splitView.adjustSubviews()

    # Pane Collapsing

    def splitView_shouldCollapseSubview_forDoubleClickOnDividerAtIndex_(self, splitView, subview, dividerIndex):
        paneIndex = splitView.subviews().indexOfObject_(subview)
        wrapper = splitView.vanillaWrapper()
        paneDescription = wrapper._paneDescriptions[paneIndex]
        return paneDescription["canCollapse"]

    def splitView_canCollapseSubview_(self, splitView, subview):
        paneIndex = splitView.subviews().indexOfObject_(subview)
        wrapper = splitView.vanillaWrapper()
        paneDescription = wrapper._paneDescriptions[paneIndex]
        return paneDescription["canCollapse"]

    # Pane Size Constraints

    def splitView_constrainMinCoordinate_ofSubviewAt_(self, splitView, proposedMin, dividerIndex):
        newMinThis = newMinNext = proposedMin
        coordIndex = self._splitViewCoordinateIndex_(splitView)
        wrapper = splitView.vanillaWrapper()
        paneDescriptions = wrapper._paneDescriptions
        # if there is a min size set for the first pane,
        # calculate where that would be
        paneDescription = paneDescriptions[dividerIndex]
        minSize = paneDescription["minSize"]
        if minSize is not None:
            view = paneDescription["nsView"]
            newMinThis = view.frame().origin[coordIndex] + minSize
        # if there is a max size for the next pane,
        # calculate where that would be
        paneDescription = paneDescriptions[dividerIndex + 1]
        maxSize = paneDescription["maxSize"]
        if maxSize is not None:
            view = paneDescription["nsView"]
            frame = view.frame()
            newMinNext = frame.origin[coordIndex] + frame.size[coordIndex] - maxSize - splitView.dividerThickness()
        # determine where the new min will be
        newMin = max(newMinThis, newMinNext, proposedMin)
        return newMin

    def splitView_constrainMaxCoordinate_ofSubviewAt_(self, splitView, proposedMax, dividerIndex):
        newMaxThis = newMaxNext = proposedMax
        coordIndex = self._splitViewCoordinateIndex_(splitView)
        wrapper = splitView.vanillaWrapper()
        paneDescriptions = wrapper._paneDescriptions
        # if there is a max size set for the first pane,
        # calculate where that would be
        paneDescription = paneDescriptions[dividerIndex]
        maxSize = paneDescription["maxSize"]
        if maxSize is not None:
            view = paneDescription["nsView"]
            newMaxThis = view.frame().origin[coordIndex] + maxSize
        # if there is a min size for the next pane,
        # calculate where that would be
        paneDescription = paneDescriptions[dividerIndex + 1]
        minSize = paneDescription["minSize"]
        if minSize is not None:
            view = paneDescription["nsView"]
            frame = view.frame()
            newMaxNext = frame.origin[coordIndex] + frame.size[coordIndex] - minSize - splitView.dividerThickness()
        # determine where the new max will be
        newMax = min(newMaxThis, newMaxNext, proposedMax)
        return newMax

    # Pane Resizing

    def splitView_resizeSubviewsWithOldSize_(self, splitView, oldSize):
        coordIndex = self._splitViewCoordinateIndex_(splitView)
        newSize = splitView.frame().size
        self.splitView_applyPaneSizeChange_wifthFrameSize_ignoreView_(
            splitView,
            newSize[coordIndex] - oldSize[coordIndex],
            newSize,
            None
        )

    def splitView_applyPaneSizeChange_wifthFrameSize_ignoreView_(self, splitView, sizeChange, frameSize, ignoreSubview):
        # don't bother if the view is invisible
        if frameSize.width == 0 or frameSize.height == 0:
            return
        # gather the panes
        wrapper = splitView.vanillaWrapper()
        changablePanes = {}
        unchangablePanes = {}
        for paneDescription in wrapper._paneDescriptions:
            identifier = paneDescription["identifier"]
            if paneDescription["nsView"] == ignoreSubview:
                unchangablePanes[identifier] = paneDescription
            elif paneDescription["nsView"].isHidden():
                unchangablePanes[identifier] = paneDescription
            elif not paneDescription["resizeFlexibility"]:
                unchangablePanes[identifier] = paneDescription
            else:
                changablePanes[identifier] = paneDescription
        # calculate the change difference
        coordIndex = self._splitViewCoordinateIndex_(splitView)
        difference = sizeChange
        evenChange = difference / len(changablePanes)
        # determine tha pane size changes
        paneSizeChanges = dict.fromkeys(unchangablePanes.keys(), 0)
        ## handle min/max limited panes
        for identifier, paneDescription in changablePanes.items():
            currentSize = paneDescription["nsView"].frame().size[coordIndex]
            paneChange = None
            # shrinking
            if difference < 0:
                if paneDescription["minSize"] is not None:
                    test = currentSize + evenChange
                    if test == paneDescription["minSize"]:
                        paneChange = 0
                    elif test < paneDescription["minSize"]:
                        paneChange =  paneDescription["minSize"] - currentSize
                    else:
                        paneChange = evenChange
            # expanding
            if difference > 0:
                if paneDescription["maxSize"] is not None:
                    test = currentSize + evenChange
                    if test == paneDescription["maxSize"]:
                        paneChange = 0
                    elif test > paneDescription["maxSize"]:
                        paneChange = paneDescription["maxSize"] - currentSize
                    else:
                        paneChange = evenChange
            if paneChange is not None:
                paneSizeChanges[identifier] = paneChange
        # handle the remaining panes
        evenChange = (difference - sum(paneSizeChanges.values())) / len(changablePanes)
        for identifier, paneDescription in changablePanes.items():
            if identifier in paneSizeChanges:
                continue
            paneSizeChanges[identifier] = evenChange
        # apply the changes to the views
        isVertical = coordIndex == 0
        isVertical = splitView.isVertical()
        paneDescriptions = changablePanes
        paneDescriptions.update(unchangablePanes)
        for identifier, paneDescription in paneDescriptions.items():
            paneChange = paneSizeChanges[identifier]
            view = paneDescription["nsView"]
            frame = view.frame()
            if isVertical:
                frame.size.width += paneChange
                frame.size.height = frameSize.height
            else:
                frame.size.width = frameSize.width
                frame.size.height += paneChange
            view.setFrame_(frame)
        splitView.adjustSubviews()

    def splitView_shouldAdjustSizeOfSubview_(self, splitView, subview):
        paneIndex = splitView.subviews().indexOfObject_(subview)
        wrapper = splitView.vanillaWrapper()
        paneDescription = wrapper._paneDescriptions[paneIndex]
        return paneDescription["resizeFlexibility"]

    # Dividers

    def splitView_shouldHideDividerAtIndex_(self, splitView, dividerIndex):
        return True

    # helpers

    def _splitViewCoordinateIndex_(self, splitView):
        isVertical = splitView.isVertical()
        if isVertical:
            coordIndex = 0
        else:
            coordIndex = 1
        return coordIndex


class SplitView(VanillaBaseObject):

    """
    TO DO:
    - autosavename
    - custom divider drawing. maybe do this via a function(splitView, rect) and have 1+ predefined functions.
    - review the docs and see what can be supported
    - document the new arguments and stuff

    notes:
    - to lock a size, make minSize == maxSize

    ------------------------


    View that can be split into two or more subviews with dividers.::

        from vanilla import *

        class SplitViewDemo(object):

            def __init__(self):
                self.w = Window((200, 200), "SplitView Demo", minSize=(100, 100))
                list1 = List((0, 0, -0, 100), ["A", "B", "C"])
                list2 = List((0, 0, -0, 100), ["a", "b", "c"])
                paneDescriptors = [
                    dict(view=list1, identifier="pane1"),
                    dict(view=list2, identifier="pane2"),
                ]
                self.w.splitView = SplitView((0, 0, -0, -0), paneDescriptors)
                self.w.open()

        SplitViewDemo()

    **posSize** Tuple of form *(left, top, width, height)* representing
    the position and size of the split view.

    **paneDescriptions** An ordered list of dictionaries describing the
    subviews, or "panes". Those dictionaries can have the following keys:

    +-----------------------+-----------------------------------------------------------------------------+
    | *view*                | A view, either a Vanilla object or a NSView. Required.                      |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"identifier"*        | A string identifying the pane. Required.                                    |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"size"*              | The initial size of the pane. Optional.                                     |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"minSize"*           | The minimum size of the pane. Optional. The default is 0.                   |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"maxSize"*           | The maximum size of the pane. Optional. The default is no maximum size.     |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"canCollapse"*       | Boolean indicating if the pane can collapse. Optional. The default is True. |
    +-----------------------+-----------------------------------------------------------------------------+
    | *"resizeFlexibility"* | Boolean indicating if the pane can adjust its size automatically when the   |
    |                       | SplitView size changes. Optional. The default is True unless the pane has a |
    |                       | fixed size.                                                                 |
    +-----------------------+-----------------------------------------------------------------------------+

    **isVertical** Boolean representing if the split view is vertical.
    Default is *True*.
    """

    nsSplitViewClass = VanillaSplitViewSubclass

    def __init__(self, posSize, paneDescriptions, isVertical=True, dividerStyle="splitter", dividerThickness=None,
        autosaveName=None,
        # deprecated
        dividerImage=None
    ):
        # RBSplitView phase out
        if dividerImage is not None:
            warn(DeprecationWarning("The dividerImage argument is deprecated and will be ignored. Use the dividerStyle attribute."))
        # set up and basic attributes
        self._setupView(self.nsSplitViewClass, posSize)
        self._nsObject.setVertical_(isVertical)
        self._nsObject.setDividerThickness_(dividerThickness)
        dividerStyle = _dividerStyleMap[dividerStyle]
        self._nsObject.setDividerStyle_(dividerStyle)
        if autosaveName is not None:
            self._nsObject.setAutosaveName_(autosaveName)
        # delegate
        self._delegate = VanillaSplitViewDelegate.alloc().init()
        self._nsObject.setDelegate_(self._delegate)
        # panes
        self._paneDescriptions = paneDescriptions
        self._setupPanes()

    def _breakCycles(self):
        self._nsObject.setDelegate_(None)
        self._delegate = None
        self._paneDescriptions = None
        self._identifierToPane = None
        super(SplitView, self)._breakCycles()

    def _setupPanes(self):
        self._identifierToPane = {}
        splitView = self.getNSSplitView()
        splitViewFrame = splitView.frame()
        mask = NSViewWidthSizable | NSViewHeightSizable
        for index, paneDescription in enumerate(self._paneDescriptions):
            # get the pane data
            view = paneDescription["view"]
            identifier = paneDescription["identifier"]
            size = paneDescription.get("size")
            minSize = paneDescription.get("minSize")
            maxSize = paneDescription.get("maxSize")
            canCollapse = paneDescription.get("canCollapse", True)
            resizeFlexibility = paneDescription.get("resizeFlexibility", True)
            # unwrap the view if necessary
            if isinstance(view, VanillaBaseObject):
                l, t, w, h = view._posSize
                view._setFrame(splitViewFrame)
                view = view._nsObject
                view.setAutoresizingMask_(mask)
            # push all of the items into the description
            # so that we can reduce the get calls and
            # centralize the default values here.
            paneDescription["index"] = index
            paneDescription["nsView"] = view
            paneDescription["size"] = size
            paneDescription["minSize"] = minSize
            paneDescription["maxSize"] = maxSize
            paneDescription["canCollapse"] = canCollapse
            paneDescription["fixedSize"] = minSize is not None and minSize == maxSize
            if resizeFlexibility and paneDescription["fixedSize"]:
                resizeFlexibility = False
            paneDescription["resizeFlexibility"] = resizeFlexibility
            # store the view
            assert identifier is not None
            assert identifier not in self._identifierToPane
            self._identifierToPane[identifier] = paneDescription
            # add the subview
            splitView.addSubview_(view)


    def getRBSplitView(self):
        warn("SplitView no longet wraps RBSplitView. Use getNSSplitView instead of getRBSplitView.")
        return self.getNSSplitView()

    def getNSSplitView(self):
        """
        Return the *NSSplitView* that this object wraps.
        """
        return self._nsObject

    def isPaneVisible(self, identifier):
        """
        Returns a boolean indicating if the pane with **identifier**
        is visible or not.
        """
        return self.getNSSplitView().getStateForPane_(identifier)

    def showPane(self, identifier, onOff, animate=False):
        """
        Set the visibility of the pane with **identifier**.
        **onOff* should be a boolean indicating the desired
        visibility of the pane. If **animate** is True,
        the pane will expand or collapse with and animation.
        """
        if animate:
            warn("Pane animation is not supported at this time.")
        self.getNSSplitView().setState_forPane_(onOff, identifier)

    def togglePane(self, identifier, animate=False):
        """
        Toggle the visibility of the pane with **identifier**.
        If **animate** is True, the pane will expand or collapse
        with and animation.
        """
        currentState = self.isPaneVisible(identifier)
        self.showPane(identifier, not currentState, animate)
