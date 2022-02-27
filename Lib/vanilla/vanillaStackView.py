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
    gravity=AppKit.NSStackViewDistributionGravityAreas,
    # deprecated
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
* "gravity"

**edgeInsets** Tuple of four numbers (left, top, right, bottom) indicating the amount to inset the views.

**View Definition Structure**

Views are defined with either a Vanilla object, a NSView
(or NSView subclass) object or a dictionary with this structure:

* **view** A vanilla object or an instance of `NSView`_.
* **width** A  number, string (using the size syntax below)
  or None (indicating auto width) defining the width.
* **height** A  number, string (using the size syntax below)
  or None (indicating auto height) defining the height.
* **gravity** The gravity that this view should be attracted to.
* **spacing** A number defining custom spacing after the view.

Size Constants:

* "fill" Stretch the view to fit the width or height of
  the stack view.
* "fit" Fit the view to the size needed to contain its contents.

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
        for view in views:
            if not isinstance(view, dict):
                view = dict(view=view)
            self.appendView(**view)
        self.setEdgeInsets(edgeInsets)

    def getNSStackView(self):
        return self._nsObject

    def setEdgeInsets(self, value):
        """
        Set the edge insets.
        """
        stackView = self.getNSStackView()
        stackView.setEdgeInsets_(value)

    def appendView(self, view, width=None, height=None, spacing=None, gravity="center"):
        """
        Append a view.
        """
        index = len(self._nsObject.viewsInGravity_(self._gravities.get(gravity, gravity)))
        self.insertView(index, view=view, width=width, height=height, spacing=spacing, gravity=gravity)

    def insertView(self, index, view, width=None, height=None, spacing=None, gravity="center"):
        """
        Insert a view.
        """
        gravity = self._gravities.get(gravity, gravity)
        if isinstance(view, VanillaBaseObject):
            view = view._nsObject
        stackView = self.getNSStackView()
        stackView.insertView_atIndex_inGravity_(view, index, gravity)
        if isinstance(view, VanillaBaseObject):
            view = view._nsObject
        stackView = self.getNSStackView()
        # size shortcuts
        # - when "fill" if used in the direction of the main axis,
        #   it means "use a flexible space"
        if width == "fit":
            width = view.fittingSize()[0]
        elif width == "fill" and self._orientation == NSUserInterfaceLayoutOrientationHorizontal:
            width = None
        if height == "fit":
            height = view.fittingSize()[1]
        elif height == "fill" and self._orientation == NSUserInterfaceLayoutOrientationVertical:
            height = None
        # hugging and compression
        widthHuggingPriority = AppKit.NSLayoutPriorityRequired
        widthCompressionPriority = AppKit.NSLayoutPriorityRequired
        if width is None:
            intrinsicWidth = view.intrinsicContentSize()[0]
            if intrinsicWidth == AppKit.NSViewNoInstrinsicMetric:
                widthHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
                widthCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
        elif isinstance(width, (float, int)):
            pass
        elif isinstance(width, str):
            if width == "fill":
                widthHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
                widthCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
            elif width.startswith("=="):
                pass
            elif width.startswith(">="):
                widthHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
            elif width.startswith("<="):
                widthCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
        view.setContentHuggingPriority_forOrientation_(
            widthHuggingPriority,
            AppKit.NSLayoutConstraintOrientationHorizontal
        )
        view.setContentCompressionResistancePriority_forOrientation_(
            widthCompressionPriority,
            AppKit.NSLayoutConstraintOrientationHorizontal
        )
        heightHuggingPriority = AppKit.NSLayoutPriorityRequired
        heightCompressionPriority = AppKit.NSLayoutPriorityRequired
        if height is None:
            intrinsicHeight = view.intrinsicContentSize()[1]
            if intrinsicHeight == AppKit.NSViewNoInstrinsicMetric:
                heightHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
                heightCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
        elif isinstance(height, (float, int)):
            pass
        elif isinstance(height, str):
            if height == "fill":
                heightHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
                heightCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
            elif height.startswith("=="):
                pass
            elif height.startswith(">="):
                heightHuggingPriority = AppKit.NSLayoutPriorityDefaultLow
            elif height.startswith("<="):
                heightCompressionPriority = AppKit.NSLayoutPriorityDefaultLow
        view.setContentHuggingPriority_forOrientation_(
            heightHuggingPriority,
            AppKit.NSLayoutConstraintOrientationVertical
        )
        view.setContentCompressionResistancePriority_forOrientation_(
            heightCompressionPriority,
            AppKit.NSLayoutConstraintOrientationVertical
        )
        # constraints
        if width is not None:
            if width == "fill":
                width = stackView.widthAnchor()
            _setAnchorContraint(
                view.widthAnchor(),
                width
            )
        if height is not None:
            if height == "fill":
                height = stackView.heightAnchor()
            _setAnchorContraint(
                view.heightAnchor(),
                height
            )
        # spacing
        if spacing is not None:
            stackView.setCustomSpacing_afterView_(spacing, view)

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
        leading=AppKit.NSLayoutAttributeTop,
        trailing=AppKit.NSLayoutAttributeBottom,
        height=AppKit.NSLayoutAttributeHeight
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
        trailing=AppKit.NSLayoutAttributeTrailing,
        width=AppKit.NSLayoutAttributeWidth
    )

def _setAnchorContraint(anchor, value):
    for existing in anchor.constraintsAffectingLayout():
        existing.setActive_(False)
    if isinstance(value, str) and "," in value:
        for v in value.split(","):
            v = v.strip()
            _setAnchorContraint(anchor, v)
        return
    methods = {
        "==" : anchor.constraintEqualToConstant_,
        ">=" : anchor.constraintGreaterThanOrEqualToConstant_,
        "<=" : anchor.constraintLessThanOrEqualToConstant_,
    }
    if isinstance(value, AppKit.NSLayoutAnchor):
        method = anchor.constraintEqualToAnchor_
    elif isinstance(value, (int, float)):
        method = methods["=="]
    else:
        relation = value[:2]
        value = float(value[2:])
        method = methods[relation]
    constraint = method(value)
    constraint.setActive_(True)
