from AppKit import NSObject
from PyObjCTools import NibClassBuilder, AppHelper
from simpleAppWindow import SimpleAppWindow


NibClassBuilder.extractClasses("MainMenu")


class SimpleAppAppDelegate(NSObject):
    
    def applicationDidFinishLaunching_(self, notification):
        SimpleAppWindow()


if __name__ == "__main__":
    AppHelper.runEventLoop()