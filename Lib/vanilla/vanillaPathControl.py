from AppKit import NSPathControl, NSPathStyleStandard, NSColor, NSFocusRingTypeNone, NSURL, NSPathStylePopUp, NSRoundedBezelStyle
import os
from vanilla.vanillaBase import VanillaBaseControl


_pathStylesMap = {
    "standard": NSPathStyleStandard,
    "popUp": NSPathStylePopUp,
}


class PathControl(VanillaBaseControl):

    """
    A path control.

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing the position
    and size of the control. The size of the control should match the appropriate value
    for the given *sizeStyle*.

    +-------------------------+
    | **Standard Dimensions** |
    +=========+===+===========+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 20        |
    +---------+---+-----------+
    | Mini    | H | 18        |
    +---------+---+-----------+

    **url** The url to be displayed in the control.

    **callback** The method to be called when the user presses the control.

    **pathStyle** A string representing the path style. The options are:

    +------------+
    | "standard" |
    +------------+
    | "popUp"    |
    +------------+

    **sizeStyle** A string representing the desired size style of the button. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsPathControlClass = NSPathControl

    def __init__(self, posSize, url, callback=None, pathStyle="standard", sizeStyle="regular"):
        self._setupView(self.nsPathControlClass, posSize, callback=callback)
        self._nsObject.setPathStyle_(_pathStylesMap[pathStyle])
        self._setSizeStyle(sizeStyle)
        self._nsObject.setBackgroundColor_(NSColor.clearColor())
        self._nsObject.setFocusRingType_(NSFocusRingTypeNone)
        self._nsObject.cell().setBordered_(True)
        self._nsObject.cell().setBezelStyle_(NSRoundedBezelStyle)
        self.set(url)

    def set(self, url):
        if url is not None:
            url = NSURL.URLWithString_(url)
        self._nsObject.setURL_(url)

    def get(self):
        url = self._nsObject.URL()
        if url is not None:
            return url.path()
        return None

    def getSelected(self):
        path = []
        for item in self._nsObject.pathItems():
            cell = item.pathComponentCell()
            path.append(item.title())
            if cell == self._nsObject.clickedPathComponentCell():
                break
        return os.sep.join(path)
