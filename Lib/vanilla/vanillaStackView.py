from vanilla.vanillaBase import VanillaBaseObject
import AppKit

NSUserInterfaceLayoutOrientationHorizontal = 0
NSUserInterfaceLayoutOrientationVertical = 1

NSStackViewGravityTop = 1
NSStackViewGravityLeading = 1
NSStackViewGravityCenter = 2
NSStackViewGravityBottom = 3
NSStackViewGravityTrailing = 3

distributions = dict(
    equalCentering=AppKit.NSStackViewDistributionEqualCentering,
    equalSpacing=AppKit.NSStackViewDistributionEqualSpacing,
    fill=AppKit.NSStackViewDistributionFill,
    fillEqually=AppKit.NSStackViewDistributionFillEqually,
    fillProportionally=AppKit.NSStackViewDistributionFillProportionally,
    gravityAreas=AppKit.NSStackViewDistributionGravityAreas
)


_doc = """
A view that allows the creation of a stack of views.

**posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
the position and size of the stack view.

**views** The views to display in the stack. See below for structure.

**spacing** Space to insert between views.

**alignment** The alignment of the views. Options:

* "leading"
* "center"
* "trailing"
* One of the `NSLayoutAttribute`_ options.

**distribution** The distribution of the views. Options:

* "equalCentering"
* "equalSpacing"
* "fill"
* "fillEqually"
* "fillProportionally"
* "gravityAreas"

**edgeInsets** Tuple of four numbers indicating the amount to inset the views.

**View Definition Structure**

Views are defined with either a Vanilla object, a NSView
(or NSView subclass) object or a dictionary with this structure:

* **view** A vanilla object or an instance of `NSView`_.
* **width** A  number, string (using the size syntax below)
  or None (indicating auto width) defining the width.
* **height** A  number, string (using the size syntax below)
  or None (indicating auto height) defining the height.
* **gravity** The gravity that this view should be attracted to.
* **padding** A tuple of two numbers defining (before, after)
  padding between the view and surrounding views.

Size Syntax:

* "==value" where value can be coerced to an integer or float
* "<=value" where value can be coerced to an integer or float
* ">=value" where value can be coerced to an integer or float

Up to two are allowed. Separate with ``,`` (comma).

Horizontal Gravity Options:

* "leading"
* "center"
* "trailing"
* One of the `NSStackViewGravity`_ options.

Vertical Gravity Options:

* "top"
* "center"
* "bottom"
* One of the `NSStackViewGravity`_ options.

.. _NSLayoutAttribute: https://developer.apple.com/documentation/uikit/nslayoutattribute?language=objc
.. _NSView: https://developer.apple.com/documentation/appkit/nsview?language=objc
.. _NSStackViewGravity: https://developer.apple.com/documentation/appkit/nsstackviewgravity?language=occ
"""

class _StackView(VanillaBaseObject):

    __doc__ = _doc

    nsStackViewClass = AppKit.NSStackView
    _orientation = None
    _gravities = None
    _alignments = None

    def __init__(self, posSize, views, spacing=0, alignment="center", distribution="fillEqually", edgeInsets=(0, 0, 0, 0)):
        self._setupView(self.nsStackViewClass, posSize)
        alignment = self._alignments.get(alignment, alignment)
        distribution = distributions[distribution]
        stackView = self._getContentView()
        stackView.setOrientation_(self._orientation)
        stackView.setSpacing_(spacing)
        stackView.setAlignment_(alignment)
        stackView.setDistribution_(distribution)
        stackView.setEdgeInsets_(edgeInsets)
        for view in views:
            if not isinstance(view, dict):
                view = dict(view=view)
            self.appendView(**view)

    def getNSStackView(self):
        return self._nsObject

    def appendView(self, view, width=None, height=None, padding=(0, 0), gravity="center"):
        """
        Append a view.
        """
        index = len(self._nsObject.viewsInGravity_(self._gravities.get(gravity, gravity)))
        self.insertView(index, view=view, width=width, height=height, padding=padding, gravity=gravity)

    def insertView(self, index, view, width=None, height=None, padding=(0, 0), gravity="center"):
        """
        Insert a view.
        """
        gravity = self._gravities.get(gravity, gravity)
        if isinstance(view, VanillaBaseObject):
            view = view._nsObject
        if width is not None:
            _applyStackViewConstantToAnchor(view.widthAnchor(), width)
        if height is not None:
            _applyStackViewConstantToAnchor(view.heightAnchor(), height)
        stackView = self.getNSStackView()
        stackView.insertView_atIndex_inGravity_(view, index, gravity)
        before, after = padding
        if before:
            stackView.setCustomSpacing_beforeView_(before, view)
        if after:
            stackView.setCustomSpacing_afterView_(after, view)

    def removeView(self, view):
        """
        Remove a view.
        """
        if isinstance(view, VanillaBaseObject):
            view = view._nsObject
        self.getNSStackView().removeView_(view)


class HorizontalStackView(_StackView):

    __doc__ = _doc

    _orientation = NSUserInterfaceLayoutOrientationHorizontal
    _gravities = dict(
        leading=NSStackViewGravityLeading,
        center=NSStackViewGravityCenter,
        trailing=NSStackViewGravityTrailing
    )
    _alignments = dict(
        center=AppKit.NSLayoutAttributeCenterY,
        leading=AppKit.NSLayoutAttributeLeading,
        trailing=AppKit.NSLayoutAttributeTrailing
    )

class VerticalStackView(_StackView):

    __doc__ = _doc

    _orientation = NSUserInterfaceLayoutOrientationVertical
    _gravities = dict(
        top=NSStackViewGravityTop,
        center=NSStackViewGravityCenter,
        bottom=NSStackViewGravityBottom
    )
    _alignments = dict(
        center=AppKit.NSLayoutAttributeCenterX,
        leading=AppKit.NSLayoutAttributeLeading,
        trailing=AppKit.NSLayoutAttributeTrailing
    )


def _applyStackViewConstantToAnchor(anchor, value):
    if isinstance(value, str) and "," in value:
        for v in value.split(","):
            v = v.strip()
            _applyStackViewConstantToAnchor(anchor, v)
        return
    methods = {
        "==" : anchor.constraintEqualToConstant_,
        ">=" : anchor.constraintGreaterThanOrEqualToConstant_,
        "<=" : anchor.constraintLessThanOrEqualToConstant_,
    }
    if isinstance(value, (int, float)):
        method = methods["=="]
    else:
        relation = value[:2]
        value = float(value[2:])
        method = methods[relation]
    method(value).setActive_(True)
