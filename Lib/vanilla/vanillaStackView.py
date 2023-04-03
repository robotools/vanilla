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

_doc = """A view that allows the creation of a stack of views.

{image}
{example}

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
        self.setEdgeInsets(edgeInsets)
        for view in views:
            if not isinstance(view, dict):
                view = dict(view=view)
            self.appendView(**view)

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
        # - when "fit" is used, let AppKit figure out the width.
        #   (note: this previously used view.fittingSize()
        #   to get an absolute size, but it was unreliable.)
        if width == "fit":
            width = None
        elif width == "fill" and self._orientation == NSUserInterfaceLayoutOrientationHorizontal:
            width = None
        if height == "fit":
            height = None
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
        bottomInset, leftInset, topInset, rightInset = self._nsObject.edgeInsets()
        if width is not None:
            if width == "fill":
                _setAnchorConstraint(
                    anchor=view.leftAnchor(),
                    otherAnchor=stackView.leftAnchor(),
                    constant=leftInset
                )
                _setAnchorConstraint(
                    anchor=view.rightAnchor(),
                    otherAnchor=stackView.rightAnchor(),
                    constant=-rightInset
                )
            else:
                _setAnchorConstraint(
                    view.widthAnchor(),
                    width
                )
        if height is not None:
            if height == "fill":
                _setAnchorConstraint(
                    anchor=view.topAnchor(),
                    otherAnchor=stackView.topAnchor(),
                    constant=topInset
                )
                _setAnchorConstraint(
                    anchor=view.bottomAnchor(),
                    otherAnchor=stackView.bottomAnchor(),
                    constant=-bottomInset
                )
            else:
                _setAnchorConstraint(
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

    _imageDocStr = """
    .. image:: /_images/HorizontalStackView.png
    """

    _exampleDocStr = """
    ::

        from vanilla import Button, HorizontalStackView, Window

        class HorizontalStackViewExample:
            def __init__(self):
                self.w = Window((300, 40))

                self.button1 = Button("auto", "One")
                self.button2 = Button("auto", "Two")
                self.button3 = Button("auto", "Three")
                self.button4 = Button("auto", "Four")

                self.w.horizontalStack = HorizontalStackView(
                    (0, 0, 0, 0),
                    views=[
                        dict(view=self.button1),
                        dict(view=self.button2),
                        dict(view=self.button3),
                        dict(view=self.button4)
                    ],
                    spacing=4,
                    edgeInsets=(4, 4, 4, 4),
                )

                self.w.open()


        HorizontalStackViewExample()
    """

    __doc__ = _doc.format(image=_imageDocStr, example=_exampleDocStr)

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

    _imageDocStr = """
    .. image:: /_images/VerticalStackView.png
    """

    _exampleDocStr = """
    ::

        from vanilla import Button, VerticalStackView, Window


        class VerticalStackViewExample:
            def __init__(self):
                self.w = Window((80, 300))

                self.button1 = Button("auto", "One")
                self.button2 = Button("auto", "Two")
                self.button3 = Button("auto", "Three")
                self.button4 = Button("auto", "Four")

                self.w.horizontalStack = VerticalStackView(
                    (0, 0, 0, 0),
                    views=[
                        dict(view=self.button1),
                        dict(view=self.button2),
                        dict(view=self.button3),
                        dict(view=self.button4)
                    ],
                    spacing=4,
                    edgeInsets=(4, 4, 4, 4),
                )

                self.w.open()


        VerticalStackViewExample()
    """

    __doc__ = _doc.format(image=_imageDocStr, example=_exampleDocStr)

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

def _setAnchorConstraint(
        anchor,
        value=None,
        otherAnchor=None,
        constant=0
    ):
    if isinstance(value, str) and "," in value:
        for v in value.split(","):
            v = v.strip()
            _setAnchorConstraint(
                anchor,
                value=v,
                otherAnchor=otherAnchor,
                constant=constant
            )
        return
    for existing in anchor.constraintsAffectingLayout():
        existing.setActive_(False)
    if otherAnchor is not None:
        anchorMethods = {
            "==" : anchor.constraintEqualToAnchor_constant_,
            ">=" : anchor.constraintGreaterThanOrEqualToAnchor_constant_,
            "<=" : anchor.constraintLessThanOrEqualToAnchor_constant_,
        }
        args = [otherAnchor, constant]
        if not isinstance(value, str):
            value = "=="
        relation = value[:2]
        method = anchorMethods[relation]
    else:
        assert value is not None, "A value must be given if otherAnchor is None."
        valueMethods = {
            "==" : anchor.constraintEqualToConstant_,
            ">=" : anchor.constraintGreaterThanOrEqualToConstant_,
            "<=" : anchor.constraintLessThanOrEqualToConstant_,
        }
        if isinstance(value, (int, float)):
            method = valueMethods["=="]
        else:
            relation = value[:2]
            value = float(value[2:])
            method = valueMethods[relation]
        args = [value]
    constraint = method(*args)
    constraint.setActive_(True)
