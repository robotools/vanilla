from AppKit import NSSegmentedControl, NSSegmentedCell, NSImage, NSSegmentSwitchTrackingSelectOne, NSSegmentSwitchTrackingSelectAny, NSSegmentSwitchTrackingMomentary

from vanilla.vanillaBase import VanillaBaseControl


_trackingModeMap = {
    "one": NSSegmentSwitchTrackingSelectOne,
    "any": NSSegmentSwitchTrackingSelectAny,
    "momentary": NSSegmentSwitchTrackingMomentary,
}


class SegmentedButton(VanillaBaseControl):

    """
    A standard segmented button.

    .. image:: /_images/SegmentedButton.png

    ::

        from vanilla import Window, SegmentedButton

        class SegmentedButtonDemo:

             def __init__(self):
                 self.w = Window((120, 40))
                 self.w.button = SegmentedButton((10, 10, -10, 20),
                     [dict(title="A"), dict(title="B"), dict(title="C")],
                    callback=self.buttonCallback)
                 self.w.open()

             def buttonCallback(self, sender):
                 print("button hit!")

        SegmentedButtonDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the segmented button. The size of the segmented button
    should match the appropriate value for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +=========+===+===========+
    | Regular | H | 21        |
    +---------+---+-----------+
    | Small   | H | 18        |
    +---------+---+-----------+
    | Mini    | H | 15        |
    +---------+---+-----------+

    **segmentDescriptions** An ordered list of dictionaries describing the segments.

    +----------------------------+----------------------------------------------------------+
    | width (optional)           | The desired width of the segment.                        |
    +----------------------------+----------------------------------------------------------+
    | title (optional)           | The title of the segment.                                |
    +----------------------------+----------------------------------------------------------+
    | enabled (optional)         | The enabled state of the segment. The default is `True`. |
    +----------------------------+----------------------------------------------------------+
    | imagePath (optional)       | A file path to an image to display in the segment.       |
    +----------------------------+----------------------------------------------------------+
    | imageNamed (optional)      | The name of an image already loaded as a `NSImage`_ by   |
    |                            | the application to display in the segment.               |
    +----------------------------+----------------------------------------------------------+
    | imageObject (optional)     | A `NSImage`_ object to display in the segment.           |
    +----------------------------+----------------------------------------------------------+
    | *imageTemplate* (optional) | A boolean representing if the image should converted     |
    |                            | to a template image.                                     |
    +----------------------------+----------------------------------------------------------+

    **callback** The method to be called when the user presses the segmented button.

    **selectionStyle** The selection style in the segmented button.

    +-----------+---------------------------------------------+
    | one       | Only one segment may be selected.           |
    +-----------+---------------------------------------------+
    | any       | Any number of segments may be selected.     |
    +-----------+---------------------------------------------+
    | momentary | A segmented is only selected when tracking. |
    +-----------+---------------------------------------------+

    **sizeStyle** A string representing the desired size style of the segmented button.
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

    nsSegmentedControlClass = NSSegmentedControl
    nsSegmentedCellClass = NSSegmentedCell

    frameAdjustments = {
        "mini": (0, -1, 0, 1), #15
        "small": (-2, -4, 2, 5), #20
        "regular": (0, -4, 0, 5), #24
        }

    def __init__(self, posSize, segmentDescriptions, callback=None, selectionStyle="one", sizeStyle="small"):
        self._setupView(self.nsSegmentedControlClass, posSize)
        if self.nsSegmentedCellClass != NSSegmentedCell:
            self._nsObject.setCell_(self.nsSegmentedCellClass.alloc().init())
        if callback is not None:
            self._setCallback(callback)
        self._setSizeStyle(sizeStyle)
        nsObject = self._nsObject
        nsObject.setSegmentCount_(len(segmentDescriptions))
        nsObject.cell().setTrackingMode_(_trackingModeMap[selectionStyle])
        for segmentIndex, segmentDescription in enumerate(segmentDescriptions):
            width = segmentDescription.get("width", 0)
            title = segmentDescription.get("title", "")
            enabled = segmentDescription.get("enabled", True)
            imagePath = segmentDescription.get("imagePath")
            imageNamed = segmentDescription.get("imageNamed")
            imageTemplate = segmentDescription.get("imageTemplate")
            imageObject = segmentDescription.get("imageObject")
            # create the NSImage if needed
            if imagePath is not None:
                image = NSImage.alloc().initWithContentsOfFile_(imagePath)
            elif imageNamed is not None:
                image = NSImage.imageNamed_(imageNamed)
            elif imageObject is not None:
                image = imageObject
            else:
                image = None
            nsObject.setWidth_forSegment_(width, segmentIndex)
            nsObject.setLabel_forSegment_(title, segmentIndex)
            nsObject.setEnabled_forSegment_(enabled, segmentIndex)
            if image is not None:
                if imageTemplate is not None:
                    # only change the image template setting if its either True or False
                    image.setTemplate_(imageTemplate)
                nsObject.setImage_forSegment_(image, segmentIndex)

    def getNSSegmentedButton(self):
        """
        Return the `NSSegmentedControl`_ that this object wraps.

        .. _NSSegmentedControl: https://developer.apple.com/documentation/appkit/nssegmentedcontrol?language=objc
        """
        return self._nsObject

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        for index in range(self._nsObject.segmentCount()):
            self._nsObject.setEnabled_forSegment_(onOff, index)

    def set(self, value):
        """
        Set the selected segment. If this control is set to
        `any` mode, `value` should be a list of integers.
        Otherwise `value` should be a single integer.
        """
        # value should be an int unless we are in "any" mode
        if self._nsObject.cell().trackingMode() != _trackingModeMap["any"]:
            value = [value]
        for index in range(self._nsObject.segmentCount()):
            state = index in value
            self._nsObject.setSelected_forSegment_(state, index)

    def get(self):
        """
        Get the selected segment. If this control is set to
        `any` mode, the returned value will be a list of integers.
        Otherwise the returned value will be a single integer or
        `None` if no segment is selected.
        """
        states = []
        for index in range(self._nsObject.segmentCount()):
            state = self._nsObject.isSelectedForSegment_(index)
            if state:
                states.append(index)
        if self._nsObject.cell().trackingMode() != _trackingModeMap["any"]:
            if states:
                return states[0]
            return None
        return states

