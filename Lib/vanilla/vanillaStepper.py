from vanilla.vanillaBase import VanillaBaseControl
from AppKit import NSStepper

class Stepper(VanillaBaseControl):

    """
    A stepper control.

    ::

        from vanilla import Window, TextBox, Stepper

        class StepperDemo:

            def __init__(self):
                self.w = Window((100, 40))
                self.w.stepper = Stepper((10, 10, 20, 20),
                      value=50,
                      minValue=25,
                      maxValue=75,
                      callback=self.stepperCallback)
                self.w.open()

            def stepperCallback(self, sender):
                print("stepper", sender.get())

        StepperDemo()()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the stepper.

    **value** The initial value.

    **minValue** The minimum value.

    **maxValue** The maximum value.

    **increment** The value to increment by.

    **autoRepeat** If the control auto repeats.

    **callback** The method to be called when the user presses the stepper.

    **sizeStyle** A string representing the desired size style of the stepper.
    The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+
    """

    nsStepperClass = NSStepper

    def __init__(self, posSize, value=None, minValue=0, maxValue=10**3, increment=1, autoRepeat=True, callback=None, sizeStyle="regular"):
        self._setupView(self.nsStepperClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)

        if minValue is not None:
            self._nsObject.setMinValue_(minValue)
        self._nsObject.setMaxValue_(maxValue)
        if increment is not None:
            self._nsObject.setIncrement_(increment)
        self._nsObject.setAutorepeat_(autoRepeat)
        if value is not None:
            self.set(value)

    def get(self):
        """
        Get the value from the stepper.
        """
        return round(self._nsObject.floatValue(), 2)

    def set(self, value):
        """
        Set a value into the stepper.
        """
        multiple = self._nsObject.increment()
        value = int(round(value / float(multiple))) * multiple
        self._nsObject.setFloatValue_(value)
