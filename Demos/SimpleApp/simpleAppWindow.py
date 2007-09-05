from vanilla import *

class SimpleAppWindow(object):
    
    def __init__(self):
        self.w = Window((250, 120), 'Simple App Window', closable=False)
        self.w.text = TextBox((10, 10, -10, 70), "This is a simple window. It doesn't do much. You see that button? Press it and some text will be printed in Console.app.")
        self.w.button = Button((10, 90, -10, 20), 'Press me', callback=self.buttonCallback)
        self.w.open()
    
    def buttonCallback(self, sender):
        print 'You pressed the button!'