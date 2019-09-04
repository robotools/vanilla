import vanilla
from vanilla import dialogs


class Test(object):

    def __init__(self):

        self.w = vanilla.Window((200, 400))

        buttons = [
            "message",
            "messageSheet",
            "askYesNo",
            "askYesNoCallback",
            "askYesNoSheet",
            "askYesNoCancel",
            "askYesNoCancelCallback",
            "askYesNoCancelSheet",
            "getFile",
            "getFileSheet",
            "getFolder",
            "getFolderSheet",
            "getFileOrFolder",
            "getFileOrFolderSheet",
        ]

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

if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)