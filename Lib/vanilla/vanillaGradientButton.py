from AppKit import NSSmallSquareBezelStyle
from vanilla.vanillaButton import ImageButton


class GradientButton(ImageButton):

    """
    An image button that initiates an immediate action related to a view.

    .. image:: /_images/GradientButton.png

    ::

        import AppKit
        from vanilla import GradientButton, Window


        class GradientButtonExample:
            def __init__(self):
                self.w = Window((80, 80))
                self.w.gradientButton = GradientButton(
                    (10, 10, 40, 40),
                    imageNamed=AppKit.NSImageNameRefreshTemplate,
                    imagePosition="top",
                    callback=self.gradientButtonCallback,
                    sizeStyle="regular",
                )

                self.w.open()

            def gradientButtonCallback(self, sender):
                print("gradient button hit!")


        GradientButtonExample()


    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the button.

    **title** The text to be displayed on the button. Pass *None* if no title is desired.

    **bordered** Boolean representing if the button should be bordered.

    **imagePath** A file path to an image.

    **imageNamed** The name of an image already loaded as a `NSImage`_ by the application.

    **imageObject** A `NSImage`_ object.

    .. note:: Only one of *imagePath*, *imageNamed*, *imageObject* should be set.

    **imagePosition** The position of the image relative to the title.
    The options are:

    +----------+
    | "top"    |
    +----------+
    | "bottom" |
    +----------+
    | "left"   |
    +----------+
    | "right"  |
    +----------+

    **callback** The method to be called when the user presses the button.

    **sizeStyle** A string representing the desired size style of the button.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    .. _NSImage: https://developer.apple.com/documentation/appkit/nsimage?language=objc
    """

    nsBezelStyle = NSSmallSquareBezelStyle
