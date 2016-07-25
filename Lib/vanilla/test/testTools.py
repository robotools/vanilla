from AppKit import *
from PyObjCTools import AppHelper


class _VanillaMiniAppDelegate(NSObject):

    def applicationShouldTerminateAfterLastWindowClosed_(self, notification):
        return True


def executeVanillaTest(cls, **kwargs):
    """
    Execute a Vanilla UI class in a mini application.
    """
    app = NSApplication.sharedApplication()
    delegate = _VanillaMiniAppDelegate.alloc().init()
    app.setDelegate_(delegate)

    mainMenu = NSMenu.alloc().initWithTitle_("Vanilla Test")

    fileMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("File", None, "")
    fileMenu = NSMenu.alloc().initWithTitle_("File")
    fileMenuItem.setSubmenu_(fileMenu)
    mainMenu.addItem_(fileMenuItem)

    editMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Edit", None, "")
    editMenu = NSMenu.alloc().initWithTitle_("Edit")
    editMenuItem.setSubmenu_(editMenu)
    mainMenu.addItem_(editMenuItem)

    helpMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Help", None, "")
    helpMenu = NSMenu.alloc().initWithTitle_("Help")
    helpMenuItem.setSubmenu_(helpMenu)
    mainMenu.addItem_(helpMenuItem)

    app.setMainMenu_(mainMenu)

    cls(**kwargs)
    app.activateIgnoringOtherApps_(True)
    AppHelper.runEventLoop()
