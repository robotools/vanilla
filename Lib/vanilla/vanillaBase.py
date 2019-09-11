import platform
from distutils.version import StrictVersion
from Foundation import NSObject
from AppKit import NSFont, NSRegularControlSize, NSSmallControlSize, NSMiniControlSize, \
    NSViewMinXMargin, NSViewMaxXMargin, NSViewMaxYMargin, NSViewMinYMargin, \
    NSViewWidthSizable, NSViewHeightSizable, \
    NSLayoutConstraint, NSLayoutFormatAlignAllLeft, \
    NSLayoutAttributeLeft, NSLayoutAttributeRight, NSLayoutAttributeTop, NSLayoutAttributeBottom, NSLayoutAttributeLeading, NSLayoutAttributeTrailing, \
    NSLayoutAttributeWidth, NSLayoutAttributeHeight, NSLayoutAttributeCenterX, NSLayoutAttributeCenterY, NSLayoutAttributeBaseline, \
    NSLayoutRelationLessThanOrEqual, NSLayoutRelationEqual, NSLayoutRelationGreaterThanOrEqual

try:
    from AppKit import NSLayoutAttributeLastBaseline, NSLayoutAttributeFirstBaseline
except ImportError:
    NSLayoutAttributeLastBaseline = 11
    NSLayoutAttributeFirstBaseline = 12

from vanilla.nsSubclasses import getNSSubclass


class VanillaError(Exception): pass

# --------------------
# OS Version Constants
# --------------------

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


# ---------
# Base View
# ---------

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

    def addAutoPosSizeRules(self, rules, metrics=None):
        """
        Add auto layout rules for controls/view in this view.

        **rules** must by a list of rule definitions.
        Rule definitions may take two forms:

        * strings that follow the `Visual Format Language <https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/VisualFormatLanguage.html#//apple_ref/doc/uid/TP40010853-CH27-SW1>`_.
        * dictionaries with the following key/value pairs:

        +---------------------------+-------------------------------------------------------------------------+
        | key                       | value                                                                   |
        +===========================+=========================================================================+
        | *"view1"*                 | The vanilla wrapped view for the left side of the rule.                 |
        +---------------------------+-------------------------------------------------------------------------+
        | *"attribute1"*            | The attribute of the view for the left side of the rule.                |
        |                           | See below for options.                                                  |
        +---------------------------+-------------------------------------------------------------------------+
        | *"relation"* (optional)   | The relationship between the left side of the rule                      |
        |                           | and the right side of the rule. See below for options.                  |
        |                           | The default value is `"=="`.                                            |
        +---------------------------+-------------------------------------------------------------------------+
        | *"view2"*                 | The vanilla wrapped view for the right side of the rule.                |
        +---------------------------+-------------------------------------------------------------------------+
        | *"attribute2"*            | The attribute of the view for the right side of the rule.               |
        |                           | See below for options.                                                  |
        +---------------------------+-------------------------------------------------------------------------+
        | *"multiplier"* (optional) | The constant multiplied with the attribute on the right side of         |
        |                           | the rule as part of getting the modified attribute.               |
        |                           | The default value is `1`.                                               |
        +---------------------------+-------------------------------------------------------------------------+
        | *"constant"* (optional)   | The constant added to the multiplied attribute value on the right       |
        |                           | side of the rule to yield the final modified attribute.           |
        |                           | The default value is `0`.                                               |
        +---------------------------+-------------------------------------------------------------------------+

        The `attribute1` and `attribute2` options are:

        +-------------------+--------------------------------+
        | value             | AppKit equivalent              |
        +===================+================================+
        | *"left"*          | NSLayoutAttributeLeft          |
        +-------------------+--------------------------------+
        | *"right"*         | NSLayoutAttributeRight         |
        +-------------------+--------------------------------+
        | *"top"*           | NSLayoutAttributeTop           |
        +-------------------+--------------------------------+
        | *"bottom"*        | NSLayoutAttributeBottom        |
        +-------------------+--------------------------------+
        | *"leading"*       | NSLayoutAttributeLeading       |
        +-------------------+--------------------------------+
        | *"trailing"*      | NSLayoutAttributeTrailing      |
        +-------------------+--------------------------------+
        | *"width"*         | NSLayoutAttributeWidth         |
        +-------------------+--------------------------------+
        | *"height"*        | NSLayoutAttributeHeight        |
        +-------------------+--------------------------------+
        | *"centerX"*       | NSLayoutAttributeCenterX       |
        +-------------------+--------------------------------+
        | *"centerY"*       | NSLayoutAttributeCenterY       |
        +-------------------+--------------------------------+
        | *"baseline"*      | NSLayoutAttributeBaseline      |
        +-------------------+--------------------------------+
        | *"lastBaseline"*  | NSLayoutAttributeLastBaseline  |
        +-------------------+--------------------------------+
        | *"firstBaseline"* | NSLayoutAttributeFirstBaseline |
        +-------------------+--------------------------------+

        Refer to the `NSLayoutAttribute documentation <https://developer.apple.com/documentation/uikit/nslayoutattribute>`_
        for the information about what each of these do.

        The `relation` options are:

        +--------+------------------------------------+
        | value  | AppKit equivalent                  |
        +========+====================================+
        | *"<="* | NSLayoutRelationLessThanOrEqual    |
        +--------+------------------------------------+
        | *"=="* | NSLayoutRelationEqual              |
        +--------+------------------------------------+
        | *">="* | NSLayoutRelationGreaterThanOrEqual |
        +--------+------------------------------------+        

        Refer to the `NSLayoutRelation documentation <https://developer.apple.com/documentation/uikit/nslayoutrelation?language=objc>`_
        for the information about what each of these do.

        **metrics** may be either **None** or a dict containing
        key value pairs representing metrics keywords used in the
        rules defined with strings.
        """
        _addAutoLayoutRules(self, rules, metrics)

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


# ------------
# Base Control
# ------------

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


# -------------------
# Sub-View Management
# -------------------

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


# -------------------
# Auto Layout Support
# -------------------

_layoutAttributeMap = dict(
   left=NSLayoutAttributeLeft,
   right=NSLayoutAttributeRight,
   top=NSLayoutAttributeTop,
   bottom=NSLayoutAttributeBottom,
   leading=NSLayoutAttributeLeading,
   trailing=NSLayoutAttributeTrailing,
   width=NSLayoutAttributeWidth,
   height=NSLayoutAttributeHeight,
   centerX=NSLayoutAttributeCenterX,
   centerY=NSLayoutAttributeCenterY,
   baseline=NSLayoutAttributeBaseline,
   lastBaseline=NSLayoutAttributeLastBaseline,
   firstBaseline=NSLayoutAttributeFirstBaseline,
)

_layoutRelationMap = {
    "<=" : NSLayoutRelationLessThanOrEqual,
    "==" : NSLayoutRelationEqual,
    ">=" : NSLayoutRelationGreaterThanOrEqual
}

def _addAutoLayoutRules(obj, rules, metrics=None):
    view = obj._getContentView()
    if metrics is None:
        metrics = {}
    for rule in rules:
        if isinstance(rule, dict):
            view1 = rule["view1"]._getContentView()
            attribute1 = _layoutAttributeMap[rule["attribute1"]]
            relation = _layoutRelationMap[rule.get("relation", "==")]
            view2 = rule["view2"]._getContentView()
            attribute2 = _layoutAttributeMap[rule["attribute2"]]
            multiplier = rule.get("multiplier", 1)
            constant = rule.get("constant", 0)
            constraints = NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                view1,
                attribute1,
                relation,
                view2,
                attribute2,
                multiplier,
                constant
            )
        else:
            constraints = NSLayoutConstraint.constraintsWithVisualFormat_options_metrics_views_(
                rule,
                0,
                metrics,
                obj._autoLayoutViews
            )
        view.addConstraints_(constraints)


# --------------------------
# Frame-Based Layout Support
# --------------------------

def _calcFrame(parentFrame, posSize, absolutePositioning=False):
    """
    Convert a vanilla posSize rect to a Cocoa frame.
    """
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
    """
    Translate a Cocoa frame to vanilla coordinates.
    """
    (pL, pB), (pW, pH) = parentFrame
    (oL, oB), (oW, oH) =  objFrame
    oT = pH - oB - oH
    return oL, oT, oW, oH


# ----------------
# Callback Support
# ----------------

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


def _breakCycles(view):
    """
    Break cyclic references by deleting _target attributes.
    """
    if hasattr(view, "vanillaWrapper"):
        obj = view.vanillaWrapper()
        if hasattr(obj, "_breakCycles"):
            obj._breakCycles()
    for view in view.subviews():
        _breakCycles(view)
