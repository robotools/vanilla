from AppKit import NSView
from vanilla.vanillaBase import VanillaBaseObject, osVersionCurrent, osVersion10_10

try:
    NSVisualEffectMaterialAppearanceBased
    NSVisualEffectMaterialLight
    NSVisualEffectMaterialDark
    NSVisualEffectMaterialTitlebar
    NSVisualEffectBlendingModeBehindWindow
    NSVisualEffectBlendingModeWithinWindow
except NameError:
    NSVisualEffectMaterialAppearanceBased = 0
    NSVisualEffectMaterialLight = 1
    NSVisualEffectMaterialDark = 2
    NSVisualEffectMaterialTitlebar = 3
    NSVisualEffectBlendingModeBehindWindow = 0
    NSVisualEffectBlendingModeWithinWindow = 1

if osVersionCurrent >= osVersion10_10:
    from AppKit import NSVisualEffectView, CALayer
    _blendingModeMap = {
        "behindWindow" : NSVisualEffectBlendingModeBehindWindow,
        "withinWindow" : NSVisualEffectBlendingModeWithinWindow
    }
else:
    NSVisualEffectView = None


class Group(VanillaBaseObject):

    """
    An invisible container for controls.

    To add a control to a group, simply set it as an attribute of the group.::

        from vanilla import *

        class GroupDemo(object):

            def __init__(self):
                self.w = Window((150, 50))
                self.w.group = Group((10, 10, -10, -10))
                self.w.group.text = TextBox((0, 0, -0, -0),
                                        "This is a group")
                self.w.open()

        GroupDemo()

    No special naming is required for the attributes. However, each attribute must have a unique name.

    **posSize** Tuple of form *(left, top, width, height)* representing the position and size of the group.

    **blendingMode** The blending mode for the window. These are the possible options:

    +----------------+-------------------------------------------+
    | None           | No special blending.                      |
    +----------------+-------------------------------------------+
    | "behindWindow" | Blend with the content behind the window. |
    +----------------+-------------------------------------------+
    | "withinWindow" | Blend with the content within the window. |
    +----------------+-------------------------------------------+
    """

    nsViewClass = NSView
    nsVisualEffectViewClass = NSVisualEffectView

    def __init__(self, posSize, blendingMode=None):
        self._setupView(self.nsViewClass, posSize)
        if blendingMode is not None and osVersionCurrent >= osVersion10_10:
            # the visual effect view is defined as a subview
            # of the basic NSView. this is necessary because
            # within window blending requires a CA layer and
            # we may as well do it for behind window blending
            # as well to make the code in here clear.
            self._visualEffectGroup = _VisualEffectGroup(self.nsVisualEffectViewClass)
            if blendingMode == "withinWindow":
                self._visualAppearanceLayer = CALayer.layer()
                self._nsObject.setLayer_(self._visualAppearanceLayer)
                self._nsObject.setWantsLayer_(True)
            blendingMode = _blendingModeMap[blendingMode]
            self._visualEffectGroup.getNSVisualEffectView().setBlendingMode_(blendingMode)

    def __setattr__(self, attr, value):
        # __init__
        if not hasattr(self, "_visualEffectGroup") or attr == "_visualEffectGroup":
            super(Group, self).__setattr__(attr, value)
        # adding a vanilla subview: add to the visual effect view
        elif hasattr(self, "_visualEffectGroup") and isinstance(value, VanillaBaseObject) and hasattr(value, "_posSize"):
            setattr(self._visualEffectGroup, attr, value)
        # fallback: add to the main view
        else:
            super(Group, self).__setattr__(attr, value)

    def __delattr__(self, attr):
        if hasattr(self, attr):
            super(Group, self).__delattr__(attr)
        elif hasattr(self, "_visualEffectView"):
            delattr(self._visualEffectView, attr)

    def getNSView(self):
        """
        Return the *NSView* that this object wraps.
        """
        return self._nsObject

    def getNSVisualEffectView(self):
        """
        Return the *NSVisualEffectView* that this object wraps.
        """


class _VisualEffectGroup(VanillaBaseObject):

    def __init__(self, cls):
        self._setupView(cls, (0, 0, 0, 0))

    def getNSVisualEffectView(self):
        return self._nsObject
