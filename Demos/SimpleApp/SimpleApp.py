from __future__ import print_function
import sys
from AppKit import NSObject
from PyObjCTools import AppHelper
import vanilla


class SimpleAppAppDelegate(NSObject):

    def applicationDidFinishLaunching_(self, notification):
        SimpleAppWindow()


class SimpleAppWindow(object):

    def __init__(self):
        self.w = vanilla.Window((250, 120), "Simple App Window", closable=False)
        self.w.text = vanilla.TextBox((10, 10, -10, 70), "This is a simple window. It doesn't do much. You see that button? Press it and some text will be printed in Console.app.")
        self.w.button = vanilla.Button((10, 90, -10, 20), "Press me", callback=self.buttonCallback)
        self.w.open()

    def buttonCallback(self, sender):
        print("You pressed the button!")
        sys.stdout.flush()


if __name__ == "__main__":
    AppHelper.runEventLoop()

