from AppKit import NSTextField, NSSecureTextField
from vanilla.vanillaBase import VanillaBaseControl, VanillaCallbackWrapper


class VanillaEditTextDelegate(VanillaCallbackWrapper):

    _continuous = True

    def controlTextDidChange_(self, notification):
        if self._continuous:
            self.action_(notification.object())

    def controlTextDidEndEditing_(self, notification):
        if not self._continuous:
            self.action_(notification.object())


class EditText(VanillaBaseControl):

    """
    Standard short text entry control.

    .. image:: /_images/EditText.png

    ::

        from vanilla import Window, EditText

        class EditTextDemo:

            def __init__(self):
                self.w = Window((120, 42))
                self.w.editText = EditText((10, 10, -10, 22),
                                    text='some text',
                                    callback=self.editTextCallback)
                self.w.open()

            def editTextCallback(self, sender):
                print("text entry!", sender.get())

        EditTextDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the text entry control.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 19        |
    +---------+---+-----------+
    | Mini    | H | 16        |
    +---------+---+-----------+

    **text** An object representing the contents of the text entry control.
    If no formatter has been assigned to the control, this should be a string.
    If a formatter has been assigned, this should be an object of the type
    that the formatter expects.

    **callback** The method to be called when the user enters text.

    **continuous** If *True*, the callback (if any) will be called upon each
    keystroke, if *False*, only call the callback when editing finishes.
    Default is *True*.

    **readOnly** Boolean representing if the text can be edited or not.

    **formatter** A `NSFormatter`_ for controlling the display and input of
    the text entry.

    **placeholder** A placeholder string to be shown when the text entry
    control is empty.

    **sizeStyle** A string representing the desired size style of the text
    entry control. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    .. _NSFormatter: https://developer.apple.com/documentation/foundation/nsformatter?language=objc
    """

    nsTextFieldClass = NSTextField
    nsTextFieldDelegateClass = VanillaEditTextDelegate

    def __init__(self, posSize, text="", callback=None, continuous=True, readOnly=False, formatter=None, placeholder=None, sizeStyle="regular"):
        self._continuous = continuous
        self._setupView(self.nsTextFieldClass, posSize, callback)
        self._posSize = posSize
        self._setSizeStyle(sizeStyle)
        self._nsObject.setObjectValue_(text)
        self._nsObject.setDrawsBackground_(True)
        self._nsObject.setBezeled_(True)
        self._nsObject.setEditable_(not readOnly)
        self._nsObject.setSelectable_(True)
        self._nsObject.setFormatter_(formatter)
        if placeholder:
            self._nsObject.cell().setPlaceholderString_(placeholder)

    def _testForDeprecatedAttributes(self):
        super()._testForDeprecatedAttributes()
        from warnings import warn
        if hasattr(self, "_textFieldClass"):
            warn(DeprecationWarning("The _textFieldClass attribute is deprecated. Use the nsTextFieldClass attribute."))
            self.nsTextFieldClass = self._textFieldClass

    def getNSTextField(self):
        """
        Return the `NSTextField`_ that this object wraps.

        .. _NSTextField: https://developer.apple.com/documentation/appkit/nstextfield?language=objc
        """
        return self._nsObject

    def _setCallback(self, callback):
        if callback is not None:
            self._target = self.nsTextFieldDelegateClass(callback)
            self._target._continuous = self._continuous
            self._nsObject.setDelegate_(self._target)

    def get(self):
        """
        Get the contents of the text entry control.

        If no formatter has been assigned to the control, this returns a string.
        If a formatter has been assigned, this returns an object which has been
        translated by the formatter.
        """
        return self._nsObject.objectValue()

    def set(self, value):
        """
        Set the contents of the text entry control.

        **value** An object representing the contents of the text entry control.
        If no formatter has been assigned to the control, this should be a string.
        If a formatter has been assigned, this should be an object of the type
        that the formatter expects.
        """
        self._nsObject.setObjectValue_(value)

    def getPlaceholder(self):
        """
        Get the placeholder string displayed in the control.
        """
        return self._nsObject.cell().placeholderString()

    def setPlaceholder(self, value):
        """
        Set *value* as the placeholder string to be displayed in the control.
        *value* must be a string.
        """
        self._nsObject.cell().setPlaceholderString_(value)

    def selectAll(self):
        """
        Select all text in the text entry control.
        """
        self._nsObject.selectText_(None)


class SecureEditText(EditText):

    """
    Standard secure text entry control.

    .. image:: /_images/SecureEditText.png

    ::

        from vanilla import Window, SecureEditText

        class SecureEditTextDemo:

            def __init__(self):
                self.w = Window((120, 42))
                self.w.secureEditText = SecureEditText((10, 10, -10, 22),
                                    text='abc123',
                                    callback=self.secureEditTextCallback)
                self.w.open()

            def secureEditTextCallback(self, sender):
                print("text entry!", sender.get())

        SecureEditTextDemo()

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the text entry control.

    +-------------------------+
    | **Standard Dimensions** |
    +---------+---+-----------+
    | Regular | H | 22        |
    +---------+---+-----------+
    | Small   | H | 19        |
    +---------+---+-----------+
    | Mini    | H | 16        |
    +---------+---+-----------+

    **text** An object representing the contents of the text entry control.
    If no formatter has been assigned to the control, this should be a string.
    If a formatter has been assigned, this should be an object of the type
    that the formatter expects.

    **callback** The method to be called when the user enters text.

    **continuous** If *True*, the callback (if any) will be called upon each
    keystroke, if *False*, only call the callback when editing finishes.
    Default is *True*.

    **readOnly** Boolean representing if the text can be edited or not.

    **formatter** A `NSFormatter`_ for controlling the display and input
    of the text entry.

    **placeholder** A placeholder string to be shown when the text  entry
    control is empty.

    **sizeStyle** A string representing the desired size style of the text
    entry control. The options are:

    +-----------+
    | "regular" |
    +-----------+
    | "small"   |
    +-----------+
    | "mini"    |
    +-----------+

    .. _NSFormatter: https://developer.apple.com/documentation/foundation/nsformatter?language=objc
    """

    nsTextFieldClass = NSSecureTextField

    def getNSSecureTextField(self):
        """
        Return the `NSSecureTextField`_ that this object wraps.

        .. _NSSecureTextField: https://developer.apple.com/documentation/appkit/nssecuretextfield?language=objc
        """
        return self._nsObject
