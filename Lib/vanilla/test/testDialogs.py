import vanilla
from vanilla import dialogs


class Test(object):

    def __init__(self):
        buttons = [
            "message",
            "messageSheet",
            "messageIcon",
            "messageAccessoryView",
            "messageShowHelp",
            "messageCritical",

            "askYesNo",
            "askYesNoCallback",
            "askYesNoSheet",
            "askYesNoCancel",
            "askYesNoCancelCallback",
            "askYesNoCancelSheet",
            "askVanillaStrawberry",
            "askCustomCallback",

            "getFile",
            "getFileSheet",
            "getFolder",
            "getFolderSheet",
            "getFileOrFolder",
            "getFileOrFolderSheet",
            "getFileAccessoryView"
        ]

        self.w = vanilla.Window((200, (len(buttons) + 1) * 20))

        y = 10
        for b in buttons:
            obj = vanilla.Button((10, y, -10, 16), b, callback=getattr(self, b), sizeStyle="mini")
            setattr(self.w, "button_%s" % b, obj)
            y += 20

        self.w.open()

    def dummyCallback(self, value):
        print(value)

    def message(self, sender):
        dialogs.message("Hello world", "foo bar")

    def messageSheet(self, sender):
        dialogs.message("Hello world", "foo bar", parentWindow=self.w)

    def messageIcon(self, sender):
        import AppKit
        dialogs.message("Hello world", "Show folder icon", icon=AppKit.NSImage.imageNamed_(AppKit.NSImageNameFolder))

    def messageAccessoryView(self, sender):
        import vanilla
        view = vanilla.Box((0, 0, 200, 75))
        view.checkBox = vanilla.CheckBox((10, 10, 100, 22), "checked")
        dialogs.message("Hello world", "foo bar", accessoryView=view)

    def messageShowHelp(self, sender):
        def help():
            print("help")
        dialogs.message("Hello world", "foo bar", showsHelpCallback=help)

    def messageCritical(self, sender):
        dialogs.message("Hello world", "foo bar", alertStyle="critical")

    def askYesNo(self, sender):
        print("result", dialogs.askYesNo("Hello world", "foo bar"))

    def askYesNoCallback(self, sender):
        dialogs.askYesNo("Hello world", "foo bar", resultCallback=self.dummyCallback)

    def askYesNoSheet(self, sender):
        dialogs.askYesNo("Hello world", "foo bar", parentWindow=self.w, resultCallback=self.dummyCallback)

    def askYesNoCancel(self, sender):
        print("result", dialogs.askYesNoCancel("Hello world", "foo bar"))

    def askYesNoCancelCallback(self, sender):
        dialogs.askYesNoCancel("Hello world", "foo bar", resultCallback=self.dummyCallback)

    def askYesNoCancelSheet(self, sender):
        dialogs.askYesNoCancel("Hello world", "foo bar", parentWindow=self.w, resultCallback=self.dummyCallback)

    def askVanillaStrawberry(self, sender):
        dialogs.ask("Hello world", "foo bar", buttonTitles=[("vanilla", 1), ("Strawberry", 0)], parentWindow=self.w, resultCallback=self.dummyCallback)

    def askCustomCallback(self, sender):

        def go():
            print("go")
        def stop():
            print("stop")

        dialogs.ask("Hello world", "foo bar", buttonTitles=[dict(title="go", callback=go), dict(title="stop", callback=stop)], parentWindow=self.w, resultCallback=self.dummyCallback)

    def getFile(self, sender):
        print("result", dialogs.getFile())

    def getFileSheet(self, sender):
        dialogs.getFile(parentWindow=self.w, resultCallback=self.dummyCallback)

    def getFolder(self, sender):
        print("result", dialogs.getFolder())

    def getFolderSheet(self, sender):
        dialogs.getFolder(parentWindow=self.w, resultCallback=self.dummyCallback)

    def getFileOrFolder(self, sender):
        print("result", dialogs.getFileOrFolder())

    def getFileOrFolderSheet(self, sender):
        dialogs.getFileOrFolder(parentWindow=self.w, resultCallback=self.dummyCallback)

    def getFileAccessoryView(self, sender):
        import vanilla
        view = vanilla.Box((0, 0, 200, 75))
        view.checkBox = vanilla.CheckBox((10, 10, 100, 22), "checked")
        print("result", dialogs.getFile(accessoryView=view))


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)