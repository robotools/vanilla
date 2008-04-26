from Foundation import NSData
from AppKit import NSCursor, NSView, NSImage, NSCompositeSourceOver, NSControl
from vanilla import VanillaBaseObject, VanillaError, Group


class _VanillaSplitView(NSView):

    def setFrame_(self, frame):
        super(_VanillaSplitView, self).setFrame_(frame)
        v = self.vanillaWrapper()._setupSplitView()

    def viewDidMoveToSuperview(self):
        v = self.vanillaWrapper()
        if v is not None and self.superview() is not None:
            v._setupSplitView()


_thumbImageData = (
    '89504e470d0a1a0a0000000d4948445200000008000000080806000000c40fbe'
    '8b0000000467414d410000d6d8d44f58320000001974455874536f6674776172'
    '650041646f626520496d616765526561647971c9653c000000c14944415478da'
    '62fcffff3f033ec00222a64e9dca75f4e8519593274f1a313232329899999db7'
    'b2b2ba9d9393f30dace0d8b1632ad7af5f4ff9f7ef9fafb0b030e3dfbf7f373d'
    '7af4680e50ea1258c1e9d3a78dd8d9d97df5f5f5e5b5b4b418f9f9f97dd9d8d8'
    'cec115f0f1f131686b6b337a7b7b330215317cfffe9df1f5ebd70837b8baba9e'
    '575151d9646060e02b2f2fcff8e5cb974dbcbcbce7e00af4f4f46e8b8a8acee1'
    'e6e63e07d4cdf0f6eddb73af5ebdbaa3acacccc048c89b000106005e6d46e669'
    '9307280000000049454e44ae426082'
).decode("hex")


class _VanillaSplitterView(NSControl):

    _thumbImage = NSImage.alloc().initWithData_(NSData.dataWithBytes_length_(
            _thumbImageData, len(_thumbImageData)))

    def drawRect_(self, rect):
        w, h = self._thumbImage.size()
        bounds = self.bounds()
        x = bounds.origin.x
        y = bounds.origin.y
        x += (bounds.size.width - w) / 2
        y += (bounds.size.height - h) / 2
        self._thumbImage.compositeToPoint_operation_((x, y), NSCompositeSourceOver)

    def mouseDown_(self, event):
        splitView = self.superview().vanillaWrapper()
        splitView._splitterMouseDown(self.vanillaWrapper(), event)

    def mouseDragged_(self, event):
        splitView = self.superview().vanillaWrapper()
        splitView._splitterDragged(self.vanillaWrapper(), event)

    def mouseUp_(self, event):
        splitView = self.superview().vanillaWrapper()
        splitView._splitterMouseUp(self.vanillaWrapper(), event)

    def resetCursorRects(self):
        w, h = self.bounds().size
        if w < h:
            cursor = NSCursor.resizeLeftRightCursor()
        else:
            cursor = NSCursor.resizeUpDownCursor()
        self.addCursorRect_cursor_(self.visibleRect(), cursor)


class _SplitterView(VanillaBaseObject):

    def __init__(self, posSize, index):
        self._setupView(_VanillaSplitterView, posSize)
        self.index = index


def _calcTotalSize(paneDescriptions, gutter):
    if not paneDescriptions:
        return 0
    size = gutter * (len(paneDescriptions) - 1)
    for desc in paneDescriptions:
        size += desc["size"]
    return size


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

    _gutter = 8
    def __init__(self, posSize, paneDescriptions, isVertical=True):
        """
        *posSize* Tuple of form (left, top, width, height) representing the position and size of the split view.

        *paneDescriptions* An ordered list of dictionaries describing the subviews, or "panes". Those dictionaries can have the following keys:

        | *"view"*              | This is the vanilla object to be used as a pane. This field is mandatory. |
        | *"size"*              | The initial size for the pane. This value is optional. |
        | *"minSize"*           | The minimum size the pane should have. It is not guaranteed to be taken into account. Adjust your window's minSize accordingly. Default is 50 |
        | *"flexible"*          | A number >= 0. The higher the number, the earlier this pane is used to grow or shrink when the window resizes. Default is 0. |
        | *"visible"*           | A boolean value. If False, the pane will not be shown. To show/hide panes later, use the showSubview(), hideSubview() or toggleSubview() methods. _visible_ is optional, and True by default. |

        *isVertical* Boolean representing if the split view is vertical. Default is True.
        """
        self._didAddSubviews = False
        self._setupView(_VanillaSplitView, posSize)
        self.paneDescriptions = paneDescriptions
        self.isVertical = isVertical
        self._splitters = []
        self._subviewNames = []
        self._validatePaneDescriptions()

    def _getVisiblePaneDescriptions(self):
        return [desc for desc in self.paneDescriptions if desc["visible"]]

    def _validatePaneDescriptions(self):
        for desc in self.paneDescriptions:
            assert isinstance(desc["view"], VanillaBaseObject)
            view = desc["view"]
            view.setPosSize((0, 0, 0, 0))
            pane = Group((0, 0, 0, 0))
            pane.view = view
            desc["pane"] = pane
            if "minSize" not in desc:
                desc["minSize"] = 50
            if "visible" not in desc:
                desc["visible"] = True
            if "flexible" not in desc:
                desc["flexible"] = 0
            elif desc["flexible"] < 0:
                raise VanillaError("the flexible value can't be less than zero.")
            if "size" not in desc:
                desc["size"] = 100

    def _setupSplitView(self):
        paneDescriptions = self._getVisiblePaneDescriptions()
        self._addSubviews(paneDescriptions)
        self._setupPaneSizes(paneDescriptions)
        self._applyPaneSizes(paneDescriptions)

    def _changePaneSizes(self, paneDescriptions, growth=None, force=False):
        remainder = 0
        for desc in paneDescriptions:
            targetSize = desc["size"] + growth
            if force:
                size = targetSize
            else:
                size = max(desc["minSize"], targetSize)
                if size > targetSize:
                    remainder -= size - targetSize
            desc["size"] = size
        return remainder

    def _distributeSpace(self, paneDescriptions, growth):
        assert growth < 0
        while growth < 0:
            paneDescriptions = [desc for desc in paneDescriptions
                    if desc["size"] > desc["minSize"]]
            if not paneDescriptions:
                break
            growth = self._changePaneSizes(paneDescriptions,
                    growth / len(paneDescriptions))
        return growth

    def _getFrameSize(self):
        frameSize = self._nsObject.frame().size
        if self.isVertical:
            return frameSize.width
        else:
            return frameSize.height

    def _findMostFlexiblePanes(self, paneDescriptions):
        paneDescriptions = [(desc["flexible"], desc) for desc in paneDescriptions]
        paneDescriptions.sort()
        paneDescriptions = [desc for flexible, desc in paneDescriptions]
        highest = paneDescriptions.pop()
        highestPanes = [highest]
        highestValue = highest["flexible"]
        while paneDescriptions and paneDescriptions[-1]["flexible"] == highestValue:
            highestPanes.append(paneDescriptions.pop())
        return highestPanes, paneDescriptions

    def _setupPaneSizes(self, paneDescriptions):
        paneCount = len(paneDescriptions)
        if not paneCount:
            return
        targetTotalSize = round(self._getFrameSize() - self._gutter * (paneCount - 1))
        currentTotalSize = sum([desc["size"] for desc in paneDescriptions])
        growth = targetTotalSize - currentTotalSize
        if growth > 0:
            # Growing. There is space to be divided among the panes.
            # First see whether there are any panes that are smaller
            # than their minSize. If so, use the space there.
            # Else divide among the most flexible panes.
            tooSmallPanes = [desc for desc in paneDescriptions
                    if desc["size"] < desc["minSize"]]
            if tooSmallPanes:
                # XXX nitpick: only grow the "too small panes" until
                # they're as big as their minSize.
                growth = self._changePaneSizes(tooSmallPanes,
                        growth / len(tooSmallPanes), force=True)
            else:
                highest, rest = self._findMostFlexiblePanes(paneDescriptions)
                growth = self._changePaneSizes(highest,
                        growth / len(highest), force=True)
            assert growth == 0
        elif growth < 0:
            # Shrinking. There is space to be taken away. First take
            # space away from the most flexible panes, until they reach their
            # minSize, moving on to less flexible panes and so forth.
            # If there's *still* space left: take it away from all panes,
            # disregarding their minSize (this really means the window's
            # minSize needs to be bigger.)
            panes = paneDescriptions
            while panes and growth < 0:
                mostFlexible, panes = self._findMostFlexiblePanes(panes)
                growth = self._distributeSpace(mostFlexible, growth)
            if growth < 0:
                growth = self._changePaneSizes(paneDescriptions,
                        growth / paneCount, force=True)

    def _applyPaneSizes(self, paneDescriptions):
        paneCount = len(paneDescriptions)
        pos = 0
        for index, desc in enumerate(paneDescriptions):
            size = desc["size"]
            nextPos = pos + size
            # Non-integer positions and sizes don't work well in Cocoa
            roundedPos = round(pos)
            roundedSize = round(nextPos) - roundedPos
            if self.isVertical:
                posSize = (roundedPos, 0, roundedSize, 0)
                splitterPosSize = (roundedPos + roundedSize, 0, self._gutter, 0)
            else:
                posSize = (0, roundedPos, 0, roundedSize)
                splitterPosSize = (0, roundedPos + roundedSize, 0, self._gutter)
            view = desc["pane"]
            view.setPosSize(posSize)
            if index < paneCount - 1:
                self._splitters[index].setPosSize(splitterPosSize)
            pos += size + self._gutter

    def _addSubviews(self, paneDescriptions):
        if self._didAddSubviews:
            return
        if self._subviewNames:
            # remove any existing subviews
            for attrName in self._subviewNames:
                delattr(self, attrName)
            self._subviewNames = []
            self._splitters = []
        self._didAddSubviews = True
        paneCount = len(paneDescriptions)
        for index, desc in enumerate(paneDescriptions):
            view = desc["pane"]
            attrName = "subview" + str(index)
            self._subviewNames.append(attrName)
            setattr(self, attrName, view)
            if index < paneCount - 1:
                splitter = _SplitterView((0, 0, 0, 0), index)
                attrName = "splitter" + str(index)
                self._subviewNames.append(attrName)
                setattr(self, attrName, splitter)
                self._splitters.append(splitter)

    def _findPaneDescription(self, view):
        for desc in self.paneDescriptions:
            if desc["view"] == view:
                return desc
        raise VanillaError("no description found for view %r" % view)

    def isSubviewVisible(self, view):
        return self._findPaneDescription(view)["visible"]

    def _showHideSubview(self, view, onOff, animate=True):
        desc = self._findPaneDescription(view)
        if desc["visible"] != onOff:
            flexible = desc["flexible"]
            self._didAddSubviews = False
            # Temporarily set flexible to lower than anything:
            # other panes should make place for the new one, which
            # will keep the size it had when it was removed.
            desc["flexible"] = -1
            if animate:
                self._animatePaneToggle(desc, onOff)
            else:
                desc["visible"] = onOff
                self._setupSplitView()
            desc["flexible"] = flexible

    def _animatePaneToggle(self, desc, onOff):
        import time
        minSize = desc["minSize"]
        desc["minSize"] = 0
        if onOff:
            desc["visible"] = True
        paneDescriptions = self._getVisiblePaneDescriptions()
        if onOff:
            self._addSubviews(paneDescriptions)
        finalSize = float(desc["size"])
        if self.isVertical:
            tmpPosSize = (0, 0, finalSize, 0)
        else:
            tmpPosSize = (0, 0, 0, finalSize)
        desc["view"].setPosSize(tmpPosSize)
        startTime = time.time()
        DURATION = 0.25  # could make this depend on finalSize
        MINFRAMETIME = 1/25.0
        while True:
            startFrameTime = time.time()
            elapsed = startFrameTime - startTime
            if onOff:
                size = finalSize * min(DURATION, elapsed) / DURATION
            else:
                size = finalSize * (1 - min(DURATION, elapsed) / DURATION)
            size = max(1.0, size)
            desc["size"] = size
            self._setupPaneSizes(paneDescriptions)
            self._applyPaneSizes(paneDescriptions)
            self._nsObject.display()
            if elapsed >= DURATION:
                break
            frameTime = time.time() - startFrameTime
            if frameTime < MINFRAMETIME:
                time.sleep(MINFRAMETIME - frameTime)

        desc["minSize"] = minSize
        desc["view"].setPosSize((0, 0, 0, 0))
        if not onOff:
            desc["visible"] = False
            desc["size"] = finalSize  # restore
            paneDescriptions = self._getVisiblePaneDescriptions()
            self._addSubviews(paneDescriptions)
            self._setupPaneSizes(paneDescriptions)
            self._applyPaneSizes(paneDescriptions)

    def showSubview(self, view, animate=True):
        self._showHideSubview(view, True, animate)

    def hideSubview(self, view, animate=True):
        self._showHideSubview(view, False, animate)

    def toggleSubview(self, view, animate=True):
        desc = self._findPaneDescription(view)
        self._showHideSubview(view, not desc["visible"], animate)

    def _getMousePos(self, event):
        point = event.locationInWindow()
        if self.isVertical:
            return point.x
        else:
            # flip Y axis, we only care about relative movement, so
            # just taking the negative is fine
            return -point.y

    def _splitterMouseDown(self, splitter, event):
        mousePos = self._getMousePos(event)
        paneDescriptions = self._getVisiblePaneDescriptions()
        prev = paneDescriptions[splitter.index]
        next = paneDescriptions[splitter.index + 1]
        minMousePos = mousePos - (prev["size"] - prev["minSize"])
        maxMousePos = mousePos + (next["size"] - next["minSize"])
        if maxMousePos < minMousePos:
            minMousePos = maxMousePos = 0.5 * (maxMousePos + minMousePos)
        self._mouseClip = minMousePos, maxMousePos
        self._lastMousePos = min(maxMousePos, max(minMousePos, mousePos))

    def _getClippedMousePos(self, event):
        mousePos = self._getMousePos(event)
        minMousePos, maxMousePos = self._mouseClip
        return min(maxMousePos, max(minMousePos, mousePos))

    def _splitterMouseUp(self, splitter, event):
        pass

    def _splitterDragged(self, splitter, event):
        mousePos = self._getClippedMousePos(event)
        delta = mousePos - self._lastMousePos
        self._lastMousePos = mousePos
        if not delta:
            return

        paneDescriptions = self._getVisiblePaneDescriptions()
        index = splitter.index
        prev = paneDescriptions[splitter.index]
        next = paneDescriptions[splitter.index + 1]
        prev["size"] = prev["size"] + delta
        next["size"] = next["size"] - delta
        self._applyPaneSizes(paneDescriptions)


#
# These should move elsewhere (somewhere in vanilla.test.*)
#

class _VanillaTestViewForSplitView(NSView):

    def drawRect_(self, rect):
        from AppKit import NSRectFill, NSBezierPath, NSColor
        NSColor.redColor().set()
        NSRectFill(self.bounds())
        NSColor.blackColor().set()
        p = NSBezierPath.bezierPathWithRect_(self.bounds())
        p.stroke()


class _TestView(VanillaBaseObject):

    def __init__(self, posSize):
        self._setupView(_VanillaTestViewForSplitView, posSize)
