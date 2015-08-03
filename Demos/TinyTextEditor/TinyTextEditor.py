from AppKit import NSDocument
from PyObjCTools import AppHelper
from tinyTextEditorDocumentWindow import TinyTextEditorDocumentWindow


class TinyTextEditorDocument(NSDocument):
    
    def init(self):
        self = super(TinyTextEditorDocument, self).init()
        self.vanillaWindowController = TinyTextEditorDocumentWindow()
        self.vanillaWindowController.assignToDocument(self)
        return self        
    
    def readFromFile_ofType_(self, path, tp):
        # refer to the NSDocument reference for information about this method
        f = open(path, 'rb')
        text = f.read()
        f.close()
        self.vanillaWindowController.setText(text)
        return True
    
    def writeWithBackupToFile_ofType_saveOperation_(self, fileName, fileType, operation):
        # refer to the NSDocument reference for information about this method
        text = self.vanillaWindowController.getText()
        f = open(fileName, 'wb')
        f.write(text)
        f.close()
        return True


if __name__ == "__main__":
    AppHelper.runEventLoop()