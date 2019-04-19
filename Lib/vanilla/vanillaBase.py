import platform
from Foundation import NSObject
from AppKit import NSFont, NSRegularControlSize, NSSmallControlSize, NSMiniControlSize, NSViewMinXMargin, NSViewWidthSizable, NSViewMaxXMargin, NSViewMaxYMargin, NSViewHeightSizable, NSViewMinYMargin, NSLayoutConstraint, NSLayoutFormatAlignAllLeft
from distutils.version import StrictVersion
from vanilla.nsSubclasses import getNSSubclass

osVersionCurrent = StrictVersion(platform.mac_ver()[0])
osVersion10_14 = StrictVersion("10.14")
osVersion10_13 = StrictVersion("10.13")
osVersion10_12 = StrictVersion("10.12")
osVersion10_11 = StrictVersion("10.11")
osVersion10_10 = StrictVersion("10.10")
osVersion10_9 = StrictVersion("10.9")
osVersion10_8 = StrictVersion("10.8")
osVersion10_7 = StrictVersion("10.7")
osVersion10_6 = StrictVersion("10.6")


class VanillaError(Exception): pass


class VanillaBaseObject(object):

    frameAdjustments = None

    def __setattr__(self, attr, value):
        _setAttr(VanillaBaseObject, self, attr, value)

    def __delattr__(self, attr):
        _delAttr(VanillaBaseObject, self, attr)

    def _setupView(self, classOrName, posSize, callback=None):
        self._autoLayoutViews = {}
        self._testForDeprecatedAttributes()
        cls = getNSSubclass(classOrName)
        self._nsObject = cls(self)
        self._posSize = posSize
        self._setCallback(callback)
        self._setAutosizingFromPosSize(posSize)

    def _breakCycles(self):
        if hasattr(self, "_target"):
            self._target.callback = None

    def _testForDeprecatedAttributes(self):
        from warnings import warn
        if hasattr(self, "_frameAdjustments"):
            warn(DeprecationWarning("The _frameAdjustments attribute is deprecated. Use the frameAdjustments attribute."))
            self.frameAdjustments = self._frameAdjustments
        if hasattr(self, "_allFrameAdjustments"):
            warn(DeprecationWarning("The _allFrameAdjustments attribute is deprecated. Use the allFrameAdjustments attribute."))
            self.allFrameAdjustments = self._allFrameAdjustments

    def _setCallback(self, callback):
        if callback is not None:
            self._target = VanillaCallbackWrapper(callback)
            self._nsObject.setTarget_(self._target)
            self._nsObject.setAction_("action:")

    def _setAutosizingFromPosSize(self, posSize):
        if posSize == "auto":
            return
        l, t, w, h = posSize
        mask = 0

        if l < 0:
            mask |= NSViewMinXMargin
        if w <= 0 and (w > 0 or l >= 0):
            mask |= NSViewWidthSizable
        if w > 0 and l >= 0:
            mask |= NSViewMaxXMargin

        if t < 0:
            mask |= NSViewMaxYMargin
        if h <= 0 and (h > 0 or t >= 0):
            mask |= NSViewHeightSizable
        if h > 0 and t >= 0:
            mask |= NSViewMinYMargin

        self._nsObject.setAutoresizingMask_(mask)

    def _setFrame(self, parentFrame, animate=False):
        if self._posSize == "auto":
            return
        l, t, w, h = self._posSize
        frame  = _calcFrame(parentFrame, ((l, t), (w, h)))
        frame = self._adjustPosSize(frame)
        if animate:
            self._nsObject.animator().setFrame_(frame)
        else:
            self._nsObject.setFrame_(frame)

    def _adjustPosSize(self, frame):
        if hasattr(self._nsObject, "cell") and self._nsObject.cell() is not None:
            sizeStyle = _reverseSizeStyleMap[self._nsObject.cell().controlSize()]
        else:
            sizeStyle = None
        #
        adjustments = self.frameAdjustments
        if adjustments:
            if sizeStyle is None:
                aL, aB, aW, aH = adjustments
            else:
                aL, aB, aW, aH = adjustments.get(sizeStyle, (0, 0, 0, 0))
            (fL, fB), (fW, fH) = frame
            fL = fL + aL
            fB = fB + aB
            fW = fW + aW
            fH = fH + aH
            frame = ((fL, fB), (fW, fH))
        return frame

    def _getContentView(self):
        return self._nsObject

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        self._nsObject.setEnabled_(onOff)

    def isVisible(self):
        """
        Return a bool indicating if the object is visible or not.
        """
        return not self._nsObject.isHidden()

    def show(self, onOff):
        """
        Show or hide the object.

        **onOff** A boolean value representing if the object should be shown or not.
        """
        self._nsObject.setHidden_(not onOff)

    def getPosSize(self):
        """
        The position and size of the object as a tuple of form *(left, top, width, height)*.
        """
        return self._posSize

    def setPosSize(self, posSize, animate=False):
        """
        Set the postion and size of the object.

        **posSize** A tuple of form *(left, top, width, height)*.
        **animate** A boolean flag telling to animate the transition. Off by default.
        """
        self._posSize = posSize
        if posSize == "auto":
            return
        self._setAutosizingFromPosSize(posSize)
        superview = self._nsObject.superview()
        if superview is not None:
            self._setFrame(superview.frame(), animate)
            superview.setNeedsDisplay_(True)

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

    def move(self, x, y):
        """
        Move the object by **x** units and **y** units.
        """
        posSize = self.getPosSize()
        if posSize == "auto":
            return
        l, t, w, h = posSize
        l = l + x
        t = t + y
        self.setPosSize((l, t, w, h))

    def resize(self, width, height):
        """
        Change the size of the object to **width** and **height**.
        """
        posSize = self.getPosSize()
        if posSize == "auto":
            return
        l, t, w, h = posSize
        self.setPosSize((l, t, width, height))


class VanillaBaseControl(VanillaBaseObject):

    def _setSizeStyle(self, value):
        value = _sizeStyleMap[value]
        self._nsObject.cell().setControlSize_(value)
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(value))
        self._nsObject.setFont_(font)

    def setTitle(self, title):
        """
        Set the control title.

        **title** A string representing the title.
        """
        self._nsObject.setTitle_(title)

    def getTitle(self):
        """
        Get the control title.
        """
        return self._nsObject.title()

    def isEnabled(self):
        """
        Return a bool indicating if the object is enable or not.
        """
        return self._nsObject.isEnabled()

    def set(self, value):
        raise NotImplementedError

    def get(self):
        raise NotImplementedError

    def bind(self, key, callback):
        raise NotImplementedError


class VanillaCallbackWrapper(NSObject):

    def __new__(cls, callback):
        return cls.alloc().initWithCallback_(callback)

    def initWithCallback_(self, callback):
        self = self.init()
        self.callback = callback
        return self

    def action_(self, sender):
        if hasattr(sender, "vanillaWrapper"):
            sender = sender.vanillaWrapper()
        if self.callback is not None:
            self.callback(sender)



_sizeStyleMap = {
    "regular": NSRegularControlSize,
    "small": NSSmallControlSize,
    "mini": NSMiniControlSize
}

_reverseSizeStyleMap = {
    NSRegularControlSize: "regular",
    NSSmallControlSize: "small",
    NSMiniControlSize: "mini"
}


def _calcFrame(parentFrame, posSize, absolutePositioning=False):
    """Convert a vanilla posSize rect to a Cocoa frame."""
    (pL, pB), (pW, pH) = parentFrame
    (l, t), (w, h) = posSize
    if not absolutePositioning:
        if l < 0:
            l = pW + l
        if w <= 0:
            w = pW + w - l
        if t < 0:
            t = pH + t
        if h <= 0:
            h = pH + h - t
    b = pH - t - h  # flip it upside down
    return (l, b), (w, h)


def _flipFrame(parentFrame, objFrame):
    """Translate a Cocoa frame to vanilla coordinates"""
    (pL, pB), (pW, pH) = parentFrame
    (oL, oB), (oW, oH) =  objFrame
    oT = pH - oB - oH
    return oL, oT, oW, oH


def _breakCycles(view):
    """Break cyclic references by deleting _target attributes."""
    if hasattr(view, "vanillaWrapper"):
        obj = view.vanillaWrapper()
        if hasattr(obj, "_breakCycles"):
            obj._breakCycles()
    for view in view.subviews():
        _breakCycles(view)


def _recursiveSetFrame(view):
    for subview in view.subviews():
        if hasattr(subview, "vanillaWrapper"):
            obj = subview.vanillaWrapper()
            if obj is not None and hasattr(obj, "_posSize"):
                obj.setPosSize(obj.getPosSize())
        _recursiveSetFrame(subview)


def _setAttr(cls, obj, attr, value):
    if hasattr(value, "getPosSize") and value.getPosSize() == "auto":
        view = value._getContentView()
        view.setTranslatesAutoresizingMaskIntoConstraints_(False)
        obj._autoLayoutViews[attr] = view
    if isinstance(value, VanillaBaseObject) and hasattr(value, "_posSize"):
        assert not hasattr(obj, attr), "can't replace vanilla attribute"
        view = obj._getContentView()
        frame = view.frame()
        value._setFrame(frame)
        view.addSubview_(value._nsObject)
        _recursiveSetFrame(value._nsObject)
    #elif isinstance(value, NSView) and not attr.startswith("_"):
    #    assert not hasattr(obj, attr), "can't replace vanilla attribute"
    #    view = obj._getContentView()
    #    view.addSubview_(value)
    super(cls, obj).__setattr__(attr, value)


def _delAttr(cls, obj, attr):
    if hasattr(obj, "_autoLayoutViews"):
        if attr in obj._autoLayoutViews:
            del obj._autoLayoutViews[attr]
    value = getattr(obj, attr)
    if isinstance(value, VanillaBaseObject):
        value._nsObject.removeFromSuperview()
    #elif isinstance(value, NSView):
    #    value.removeFromSuperview()
    super(cls, obj).__delattr__(attr)


def _addConstraints(obj, constraints, metrics=None):
    view = obj._getContentView()
    if metrics is None:
        metrics = {}
    for constraint in constraints:
        constraint = NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(constraint, 0, metrics, obj._autoLayoutViews)
        view.addConstraints_(constraint)
