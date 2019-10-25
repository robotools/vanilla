from Foundation import NSDate
from AppKit import NSRunLoop, NSProgressIndicator, NSProgressIndicatorBarStyle, NSProgressIndicatorSpinningStyle
from vanilla.vanillaBase import VanillaBaseObject, _sizeStyleMap, osVersion10_11, osVersionCurrent

class ProgressBar(VanillaBaseObject):

    """
    A standard progress bar.

    .. image:: /_images/ProgressBar.png

    ::

        from vanilla import Window, ProgressBar, Button

        class ProgressBarDemo:

            def __init__(self):
                self.w = Window((200, 65))
                self.w.bar = ProgressBar((10, 10, -10, 16))
                self.w.button = Button((10, 35, -10, 20), "Go!",
                                    callback=self.showProgress)
                self.w.open()

            def showProgress(self, sender):
                import time
                self.w.bar.set(0)
                for i in range(10):
                    self.w.bar.increment(10)
                    time.sleep(.2)

        ProgressBarDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the progress bar. The height of the
    progress bar should match the appropriate value for the given *sizeStyle*.

    +---------------------------+
    | **Standard Dimensions**   |
    +-----------+---+-----------+
    | *Regular* | H | 16        |
    +-----------+---+-----------+
    | *Small*   | H | 10        |
    +-----------+---+-----------+

    **minValue** The minimum value of the progress bar.

    **maxValue** The maximum value of the progress bar.

    **isIndeterminate** Boolean representing if the progress bar is
    indeterminate. Determinate progress bars show how much of the task
    has been completed. Indeterminate progress bars simply show that
    the application is busy.

    **sizeStyle** A string representing the desired size style of the
    pregress bar. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    """

    nsProgressIndicatorClass = NSProgressIndicator

    allFrameAdjustments = {
        "small": (-1, -0, 2, 0),
        "regular": (-2, -0, 4, 0),
    }

    progressStyleMap = {
        "bar" : NSProgressIndicatorBarStyle,
        "spinning" : NSProgressIndicatorSpinningStyle
    }

    def __init__(self, posSize, minValue=0, maxValue=100, isIndeterminate=False, sizeStyle="regular", progressStyle="bar"):
        self._setupView(self.nsProgressIndicatorClass, posSize)
        self.frameAdjustments = self.allFrameAdjustments[sizeStyle]
        self._nsObject.setControlSize_(_sizeStyleMap[sizeStyle])
        self._nsObject.setStyle_(self.progressStyleMap[progressStyle])
        self._nsObject.setMinValue_(minValue)
        self._nsObject.setMaxValue_(maxValue)
        self._nsObject.setIndeterminate_(isIndeterminate)
        if isIndeterminate:
            self._nsObject.setUsesThreadedAnimation_(True)

    def getNSProgressIndicator(self):
        """
        Return the `NSProgressIndicator`_ that this object wraps.

        .. _NSProgressIndicator: https://developer.apple.com/documentation/appkit/nsprogressindicator?language=objc
        """
        return self._nsObject

    # implementation note:
    # display is called manually to ensure that the animation happens.
    # otherwise if it is called during an expensive python function,
    # it will not animate until the function is complete.

    def set(self, value):
        """
        Set the value of the progress bar to **value**.

        *Only available in determinate progress bars.*
        """
        self._nsObject.setDoubleValue_(value)
        self._nsObject.display()
        if osVersionCurrent >= osVersion10_11:
            NSRunLoop.mainRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.0001))

    def get(self):
        """
        Get the current value of the progress bar.

        *Only available in determinate progress bars.*
        """
        return self._nsObject.doubleValue()

    def increment(self, value=1):
        """
        Increment the progress bar by **value**.

        *Only available in determinate progress bars.*
        """
        self._nsObject.incrementBy_(value)
        self._nsObject.display()
        if osVersionCurrent >= osVersion10_11:
            NSRunLoop.mainRunLoop().runUntilDate_(NSDate.dateWithTimeIntervalSinceNow_(0.0001))

    def start(self):
        """
        Start the animation.

        *Only available in indeterminate progress bars.*
        """
        self._nsObject.startAnimation_(None)

    def stop(self):
        """
        Stop the animation.

        *Only available in indeterminate progress bars.*
        """
        self._nsObject.stopAnimation_(None)
