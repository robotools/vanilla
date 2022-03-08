from AppKit import NSImageView, NSImage, NSImageAlignCenter, NSImageAlignLeft, NSImageAlignRight, NSImageAlignTop, NSImageAlignTopLeft, NSImageAlignTopRight, NSImageAlignBottom, NSImageAlignBottomLeft, NSImageAlignBottomRight, NSScaleProportionally, NSScaleNone, NSScaleToFit
from vanilla.vanillaBase import VanillaBaseObject

_imageAlignmentMap = {
    ("center", "center") : NSImageAlignCenter,
    ("left", "center") : NSImageAlignLeft,
    ("right", "center") : NSImageAlignRight,
    ("center", "top") : NSImageAlignTop,
    ("left", "top") : NSImageAlignTopLeft,
    ("right", "top") : NSImageAlignTopRight,
    ("center", "bottom") : NSImageAlignBottom,
    ("left", "bottom") : NSImageAlignBottomLeft,
    ("right", "bottom") : NSImageAlignBottomRight
}

_imageScaleMap = {
    "proportional" : NSScaleProportionally,
    "none" : NSScaleNone,
    "fit" : NSScaleToFit
}


class ImageView(VanillaBaseObject):

    """
    A view that displays an image.

    .. image:: /_images/ImageView.png

    ::

        import AppKit
        from vanilla import ImageView, Window

        class ImageViewExample:
            def __init__(self):
                self.w = Window((80, 80))
                self.w.imageView = ImageView(
                    (10, 10, 40, 40),
                    horizontalAlignment="center",
                    verticalAlignment="center",
                    scale="proportional"
                )
                image = AppKit.NSImage.imageWithSystemSymbolName_accessibilityDescription_("pencil.and.outline", "")
                self.w.imageView.setImage(imageObject=image)
                self.w.open()


        ImageViewExample()


    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the view.

    **horizontalAlignment** A string representing the desired horizontal
    alignment of the image in the view. The options are:

    +-------------+-------------------------+
    | "left"      | Image is aligned left.  |
    +-------------+-------------------------+
    | "right"     | Image is aligned right. |
    +-------------+-------------------------+
    | "center"    | Image is centered.      |
    +-------------+-------------------------+

    **verticalAlignment** A string representing the desired vertical alignment
    of the image in the view. The options are:

    +-------------+--------------------------+
    | "top"       | Image is aligned top.    |
    +-------------+--------------------------+
    | "bottom"    | Image is aligned bottom. |
    +-------------+--------------------------+
    | "center"    | Image is centered.       |
    +-------------+--------------------------+

    **scale** A string representing the desired scale style of the image in the
    view. The options are:

    +----------------+----------------------------------------------+
    | "proportional" | Proportionally scale the image to fit in the |
    |                | view if it is larger than the view.          |
    +----------------+----------------------------------------------+
    | "fit"          | Distort the proportions of the image until   |
    |                | it fits exactly in the view.                 |
    +----------------+----------------------------------------------+
    | "none"         | Do not scale the image.                      |
    +----------------+----------------------------------------------+
    """

    nsImageViewClass = NSImageView

    def __init__(self, posSize, horizontalAlignment="center", verticalAlignment="center", scale="proportional"):
        self._setupView(self.nsImageViewClass, posSize)
        align = _imageAlignmentMap[(horizontalAlignment, verticalAlignment)]
        self._nsObject.setImageAlignment_(align)
        scale = _imageScaleMap[scale]
        self._nsObject.setImageScaling_(scale)

    def getNSImageView(self):
        """
        Return the `NSImageView`_ that this object wraps.

        .. _NSImageView: https://developer.apple.com/documentation/appkit/nsimageview?language=objc
        """
        return self._nsObject

    def setImage(self, imagePath=None, imageNamed=None, imageObject=None):
        """
        Set the image in the view.

        **imagePath** A file path to an image.

        **imageNamed** The name of an image already load as a `NSImage`_
        by the application.

        **imageObject** A `NSImage`_ object.

        .. note::
           Only one of *imagePath*, *imageNamed*, *imageObject* should be set.

        .. _NSImage: https://developer.apple.com/documentation/appkit/nsimage?language=objc
        """
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        else:
            raise ValueError("no image source defined")
        self._nsObject.setImage_(image)
