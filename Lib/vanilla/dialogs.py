from objc import selector
from objc import python_method
from objc import super
from Foundation import NSObject
from AppKit import NSAlert, NSSavePanel, NSOpenPanel, NSAlertStyleCritical, NSAlertStyleInformational, NSAlertStyleWarning, NSAlertFirstButtonReturn, NSAlertSecondButtonReturn, NSAlertThirdButtonReturn, NSOKButton, NSURL, NSImage


__all__ = ["message", "askYesNoCancel", "askYesNo", "getFile", "getFolder", "getFileOrFolder", "putFile"]


alertStyleMap = {
    None : NSAlertStyleInformational,
    "informational" : NSAlertStyleInformational,
    "critical" : NSAlertStyleCritical,
    # "warning" : NSAlertStyleWarning,  # no difference with
    # backwards compatible keys
    NSAlertStyleInformational : NSAlertStyleInformational,
    NSAlertStyleCritical : NSAlertStyleCritical,
    NSAlertStyleWarning : NSAlertStyleWarning
}


class BasePanel(NSObject):

    def initWithWindow_resultCallback_cancelCallback_(cls, parentWindow=None, resultCallback=None, cancelCallback=None):
        self = cls.init()
        self.retain()
        self._parentWindow = parentWindow
        self._resultCallback = resultCallback
        self._cancelCallback = cancelCallback
        return self

    def initWithWindow_resultCallback_(cls, parentWindow=None, resultCallback=None):
        return cls.initWithWindow_resultCallback_cancelCallback_(
            parentWindow=parentWindow,
            resultCallback=resultCallback,
            cancelCallback=None
        )

    def windowWillClose_(self, notification):
        self.autorelease()


class BaseMessageDialog(BasePanel):

    def initWithWindow_resultCallback_(cls, parentWindow=None, resultCallback=None):
        self = super().initWithWindow_resultCallback_(parentWindow, resultCallback)
        self.messageText = ""
        self.informativeText = ""
        self.alertStyle = NSAlertStyleInformational
        self.buttonTitlesValues = []
        self.accessoryView = None
        self.icon = None
        self.showsHelpCallback = None
        return self

    def initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_(self,
            messageText="", informativeText="", alertStyle=NSAlertStyleInformational, buttonTitlesValues=[], parentWindow=None, resultCallback=None):
        # make it backwards compatible
        import warnings
        warnings.warn(
            "'BaseMessageDiaglog.alloc().initWithMessageText_informativeText_alertStyle_buttonTitlesValues_window_resultCallback_' has been deprecated and will be removed."
            "Please update your code.",
            DeprecationWarning
        )
        self = self.initWithWindow_resultCallback_(parentWindow, resultCallback)
        self.messageText = messageText
        self.informativeText = informativeText
        self.alertStyle = alertStyle
        self.buttonTitlesValues = _mapButtonTitles(buttonTitlesValues)
        self.run()
        return self

    def run(self):
        self.alert = NSAlert.alloc().init()
        self.alert.setDelegate_(self)
        self.alert.setMessageText_(self.messageText)
        self.alert.setInformativeText_(self.informativeText)
        self.alert.setAlertStyle_(self.alertStyle)

        if self.accessoryView:
            self.alert.setAccessoryView_(self.accessoryView)
        if self.icon:
            self.alert.setIcon_(self.icon)
        if self.showsHelpCallback:
            self.alert.setShowsHelp_(True)

        for buttonTitle in self.buttonTitlesValues:
            self.alert.addButtonWithTitle_(buttonTitle["title"])
        self._value = None
        if self._parentWindow is None:
            code = self.alert.runModal()
            self._translateValue(code)
            if self._resultCallback is not None:
                self._resultCallback(self._value)
        else:
            self.alert.beginSheetModalForWindow_completionHandler_(self._parentWindow, self.completionHandler_)

    def completionHandler_(self, returnCode):
        self.alert.window().close()
        self._translateValue(returnCode)
        if self._resultCallback is not None:
            self._resultCallback(self._value)

    @python_method
    def _translateValue(self, code):
        if code == NSAlertFirstButtonReturn:
            value = 1
        elif code == NSAlertSecondButtonReturn:
            value = 2
        elif code == NSAlertThirdButtonReturn:
            value = 3
        else:
            value = code - NSAlertThirdButtonReturn + 3
        if self.buttonTitlesValues:
            result = self.buttonTitlesValues[value - 1]
            if "callback" in result:
                result["callback"]()
            self._value = result.get("returnCode")

    # delegate method

    def alertShowHelp_(self, sender):
        self.showsHelpCallback()


class BasePutGetPanel(BasePanel):

    def completionHandler_(self, returnCode):
        self.panel.close()
        if returnCode:
            self._result = self.panel.filenames()
            if self._resultCallback is not None:
                self._resultCallback(self._result)
        else:
            if self._cancelCallback is not None:
                self._cancelCallback()


class PutFilePanel(BasePutGetPanel):

    def initWithWindow_resultCallback_cancelCallback_(self, parentWindow=None, resultCallback=None, cancelCallback=None):
        self = super().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
        self.messageText = None
        self.title = None
        self.fileTypes = None
        self.directory = None
        self.fileName = None
        self.canCreateDirectories = True
        self.accessoryView = None
        self._result = None
        return self

    def run(self):
        self.panel = NSSavePanel.alloc().init()
        if self.messageText:
            self.panel.setMessage_(self.messageText)
        if self.title:
            self.panel.setTitle_(self.title)
        if self.fileName:
            self.panel.setNameFieldStringValue_(self.fileName)
        if self.directory:
            self.panel.setDirectoryURL_(NSURL.fileURLWithPath_(self.directory))
        if self.fileTypes:
            self.panel.setAllowedFileTypes_(self.fileTypes)
        self.panel.setCanCreateDirectories_(self.canCreateDirectories)
        self.panel.setCanSelectHiddenExtension_(True)
        self.panel.setAccessoryView_(self.accessoryView)
        if self._parentWindow is not None:
            self.panel.beginSheetModalForWindow_completionHandler_(self._parentWindow, self.completionHandler_)
        else:
            isOK = self.panel.runModalForDirectory_file_(self.directory, self.fileName)
            if isOK == NSOKButton:
                self._result = self.panel.filename()

    def completionHandler_(self, returnCode):
        self.panel.close()
        if returnCode:
            self._result = self.panel.filename()
            if self._resultCallback is not None:
                self._resultCallback(self._result)
        else:
            if self._cancelCallback is not None:
                self._cancelCallback()


class GetFileOrFolderPanel(BasePutGetPanel):

    def initWithWindow_resultCallback_cancelCallback_(self, parentWindow=None, resultCallback=None, cancelCallback=None):
        self = super().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
        self.messageText = None
        self.title = None
        self.directory = None
        self.fileName = None
        self.fileTypes = None
        self.allowsMultipleSelection = False
        self.canChooseDirectories = True
        self.canChooseFiles = True
        self.resolvesAliases = True
        self.accessoryView = None
        self._result = None
        return self

    def run(self):
        self.panel = NSOpenPanel.alloc().init()
        if self.messageText:
            self.panel.setMessage_(self.messageText)
        if self.title:
            self.panel.setTitle_(self.title)
        if self.fileName:
            self.panel.setNameFieldLabel_(self.fileName)
        if self.directory:
            self.panel.setDirectoryURL_(NSURL.fileURLWithPath_(self.directory))
        if self.fileTypes:
            self.panel.setAllowedFileTypes_(self.fileTypes)
        self.panel.setCanChooseDirectories_(self.canChooseDirectories)
        self.panel.setCanChooseFiles_(self.canChooseFiles)
        self.panel.setAllowsMultipleSelection_(self.allowsMultipleSelection)
        self.panel.setResolvesAliases_(self.resolvesAliases)
        self.panel.setAccessoryView_(self.accessoryView)
        if self._parentWindow is not None:
            self.panel.beginSheetModalForWindow_completionHandler_(self._parentWindow, self.completionHandler_)
        else:
            isOK = self.panel.runModalForDirectory_file_types_(self.directory, self.fileName, self.fileTypes)
            if isOK == NSOKButton:
                self._result = self.panel.filenames()


def _unwrapWindow(window):
    from vanilla.vanillaWindows import Window
    if window is None:
        return window
    if isinstance(window, Window):
        window = window.getNSWindow()
    return window


def _unwrapView(view):
    from vanilla.vanillaBase import VanillaBaseObject
    if view is None:
        return view
    if isinstance(view, VanillaBaseObject):
        l, t, w, h = view.getPosSize()
        view = view._getContentView()
        view.setFrame_(((0, 0), (w, h)))
    return view


def _mapButtonTitles(titles):
    """
    Convert key
    """
    buttonTitles = []
    for buttonTitle in titles:
        if isinstance(buttonTitle, tuple):
            title, returnCode = buttonTitle
            buttonTitle = dict(title=title, returnCode=returnCode)
        buttonTitles.append(buttonTitle)
    return buttonTitles


def message(messageText="", informativeText="", alertStyle="informational", parentWindow=None, resultCallback=None, icon=None, accessoryView=None, showsHelpCallback=None):
    assert icon is None or isinstance(icon, NSImage)

    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)

    alert = BaseMessageDialog.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    alert.messageText = messageText
    alert.informativeText = informativeText
    alert.alertStyle = alertStyleMap[alertStyle]
    alert.accessoryView = accessoryView
    alert.icon = icon
    alert.showsHelpCallback = showsHelpCallback
    alert.run()

    if resultCallback is None:
        return 1


def ask(messageText="", informativeText="", alertStyle="informational", buttonTitles=[],
        parentWindow=None, resultCallback=None, icon=None, accessoryView=None, showsHelpCallback=None):
    assert buttonTitles, "Button titles are required"
    assert icon is None or isinstance(icon, NSImage)

    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)
    buttonTitles = _mapButtonTitles(buttonTitles)

    alert = BaseMessageDialog.alloc().initWithWindow_resultCallback_(parentWindow, resultCallback)
    alert.messageText = messageText
    alert.informativeText = informativeText
    alert.alertStyle = alertStyleMap[alertStyle]
    alert.buttonTitlesValues = buttonTitles
    alert.accessoryView = accessoryView
    alert.icon = icon
    alert.showsHelpCallback = showsHelpCallback
    alert.run()

    if resultCallback is None:
        return alert._value


def askYesNoCancel(messageText="", informativeText="", alertStyle="informational",
        parentWindow=None, resultCallback=None, icon=None, accessoryView=None, showsHelpCallback=None):
    return ask(
        messageText=messageText,
        informativeText=informativeText,
        alertStyle=alertStyle,
        buttonTitles=[
            dict(title="Cancel", returnCode=-1),
            dict(title="Yes", returnCode=1),
            dict(title="No", returnCode=0)
        ],
        parentWindow=parentWindow,
        resultCallback=resultCallback,
        icon=icon,
        accessoryView=accessoryView,
        showsHelpCallback=showsHelpCallback
    )


def askYesNo(messageText="", informativeText="", alertStyle="informational",
        parentWindow=None, resultCallback=None, icon=None, accessoryView=None, showsHelpCallback=None):
    return ask(
        messageText=messageText,
        informativeText=informativeText,
        alertStyle=alertStyle,
        buttonTitles=[
            dict(title="Yes", returnCode=1),
            dict(title="No", returnCode=0)
        ],
        parentWindow=parentWindow,
        resultCallback=resultCallback,
        icon=icon,
        accessoryView=accessoryView,
        showsHelpCallback=showsHelpCallback
    )


def getFile(messageText=None, title=None, directory=None, fileName=None,
        allowsMultipleSelection=False, fileTypes=None, parentWindow=None, resultCallback=None,
        cancelCallback=None, accessoryView=None):
    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)

    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
    basePanel.messageText = messageText
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = False
    basePanel.canChooseFiles = True
    basePanel.accessoryView = accessoryView
    basePanel.run()

    if resultCallback is None:
        return basePanel._result


def getFolder(messageText=None, title=None, directory=None, allowsMultipleSelection=False,
        parentWindow=None, resultCallback=None, cancelCallback=None, accessoryView=None):
    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)

    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
    basePanel.messageText = messageText
    basePanel.title = title
    basePanel.directory = directory
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = True
    basePanel.canChooseFiles = False
    basePanel.accessoryView = accessoryView
    basePanel.run()

    if resultCallback is None:
        return basePanel._result


def getFileOrFolder(messageText=None, title=None, directory=None, fileName=None,
        allowsMultipleSelection=False, fileTypes=None, parentWindow=None, resultCallback=None,
        cancelCallback=None, accessoryView=None):
    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)

    basePanel = GetFileOrFolderPanel.alloc().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
    basePanel.messageText = messageText
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.allowsMultipleSelection = allowsMultipleSelection
    basePanel.canChooseDirectories = True
    basePanel.canChooseFiles = True
    basePanel.accessoryView = accessoryView
    basePanel.run()

    if resultCallback is None:
        return basePanel._result


def putFile(messageText=None, title=None, directory=None, fileName=None, canCreateDirectories=True,
        fileTypes=None, parentWindow=None, resultCallback=None, cancelCallback=None, accessoryView=None):
    parentWindow = _unwrapWindow(parentWindow)
    accessoryView = _unwrapView(accessoryView)

    basePanel = PutFilePanel.alloc().initWithWindow_resultCallback_cancelCallback_(parentWindow, resultCallback, cancelCallback)
    basePanel.messageText = messageText
    basePanel.title = title
    basePanel.directory = directory
    basePanel.fileName = fileName
    basePanel.fileTypes = fileTypes
    basePanel.canCreateDirectories = canCreateDirectories
    basePanel.accessoryView = accessoryView
    basePanel.run()

    if resultCallback is None:
        return basePanel._result
