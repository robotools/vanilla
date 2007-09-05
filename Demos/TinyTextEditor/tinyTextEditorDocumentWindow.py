from vanilla import *

class TinyTextEditorDocumentWindow(object):
    
    def __init__(self):
        self.w = Window((400, 400), minSize=(100, 100))
        self.w.textEditor = TextEditor((0, 0, -0, -0), checksSpelling=True)
        self.w.open()
    
    def getText(self):
        return self.w.textEditor.get()
    
    def setText(self, text):
        self.w.textEditor.set(text)
    
    def assignToDocument(self, nsDocument):
        self.w.assignToDocument(nsDocument)
