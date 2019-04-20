from vanilla.vanillaBase import VanillaBaseObject
from AppKit import NSStackView, NSLayoutAttributeCenterY, NSLayoutAttributeCenterX, NSLayoutAttributeLeading, NSLayoutAttributeTrailing

NSUserInterfaceLayoutOrientationHorizontal = 0
NSUserInterfaceLayoutOrientationVertical = 1

NSStackViewGravityTop = 1
NSStackViewGravityLeading = 1
NSStackViewGravityCenter = 2
NSStackViewGravityBottom = 3
NSStackViewGravityTrailing = 3


class _StackGroup(VanillaBaseObject):

    """
    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing the
    position and size of the group.

    **spacing** Space to insert between views in points.

    **alignment** The alignment of the views. Options:

    * "leading"
    * "center"
    * "trailing"
    * One of the NSLayoutAttribute options.

    **edgeInsets** Tuple of four numbers indicating the amount to inset the views.
    """

    nsStackViewClass = NSStackView
    _orientation = None
    _gravities = None
    _alignments = None

    def __init__(self, posSize, spacing=0, alignment="center", edgeInsets=(0, 0, 0, 0)):
        self._setupView(self.nsStackViewClass, posSize)
        alignment = self._alignments.get(alignment, alignment)
        stackView = self._getContentView()
        stackView.setOrientation_(self._orientation)
        stackView.setSpacing_(spacing)
        stackView.setAlignment_(alignment)
        stackView.setEdgeInsets_(edgeInsets)

    def addView(self, view, width=None, height=None, gravity="center"):
        """
        Add a view.

        **view** A vanilla object or an instance of NSView.

        **width** and **height** are None, numbers or strings:

        * value as integer or float
        * "==value" where value can be coerced to an integer or float
        * "<=value" where value can be coerced to an integer or float
        * ">=value" where value can be coerced to an integer or float

        Up to two are allowed. Separate with *,*.

        **gravity** The gravity that this view should be attracted to.

        HorizontalStackGroup Options:

        * "leading"
        * "center"
        * "trailing"
        * One of the NSStackViewGravity options.

        VerticalStackGroup Options:

        * "top"
        * "center"
        * "bottom"
        * One of the NSStackViewGravity options.
        """

        index = len(self._getContentView().views())
        self.insertView(index, view, width=width, height=height, gravity=gravity)

    def insertView(self, index, view, width=None, height=None, gravity="center"):
        """
        Insert a view.

        See addView documentation.
        """
        gravity = self._gravities.get(gravity, gravity)
        if isinstance(view, VanillaBaseObject):
            view = view._getContentView()
        if width is not None:
            _applyStackViewConstantToAnchor(view.widthAnchor(), width)
        if height is not None:
            _applyStackViewConstantToAnchor(view.heightAnchor(), height)
        self._getContentView().insertView_atIndex_inGravity_(view, index, gravity)

    def removeView(self, view):
        """
        Remove a view.

        **view** A vanilla object or an instance of NSView.
        """
        if isinstance(view, VanillaBaseObject):
            view = view._getContentView()
        self._getContentView().removeView_(view)


class HorizontalStackGroup(_StackGroup):

    _orientation = NSUserInterfaceLayoutOrientationHorizontal
    _gravities = dict(
        leading=NSStackViewGravityLeading,
        center=NSStackViewGravityCenter,
        trailing=NSStackViewGravityTrailing
    )
    _alignments = dict(
        center=NSLayoutAttributeCenterY,
        leading=NSLayoutAttributeLeading,
        trailing=NSLayoutAttributeTrailing
    )

class VerticalStackGroup(_StackGroup):

    _orientation = NSUserInterfaceLayoutOrientationVertical
    _gravities = dict(
        top=NSStackViewGravityTop,
        center=NSStackViewGravityCenter,
        bottom=NSStackViewGravityBottom
    )
    _alignments = dict(
        center=NSLayoutAttributeCenterX,
        leading=NSLayoutAttributeLeading,
        trailing=NSLayoutAttributeTrailing
    )


def _applyStackViewConstantToAnchor(anchor, value):
    if isinstance(value, str) and "," in value:
        for v in value.split(","):
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
