from Foundation import NSObject
from AppKit import NSApplication, NSMenu, NSMenuItem, NSBundle
from PyObjCTools import AppHelper
import asyncio

try:
    from corefoundationasyncio import CoreFoundationEventLoop
    hasCorefoundationasyncio = True
except ImportError:
    hasCorefoundationasyncio = False


class _VanillaMiniApp(NSApplication):
    pass


class _VanillaMiniAppDelegate(NSObject):

    def applicationShouldTerminateAfterLastWindowClosed_(self, notification):
        return True


def executeVanillaTest(cls, nibPath=None, calls=None, **kwargs):
    """
    Execute a Vanilla UI class in a mini application.
    """
    app = _VanillaMiniApp.sharedApplication()
    delegate = _VanillaMiniAppDelegate.alloc().init()
    app.setDelegate_(delegate)

    if nibPath:
        NSBundle.loadNibFile_externalNameTable_withZone_(nibPath, {}, None)
    else:
        mainMenu = NSMenu.alloc().initWithTitle_("Vanilla Test")

        fileMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("File", None, "")
        fileMenu = NSMenu.alloc().initWithTitle_("File")
        fileMenuItem.setSubmenu_(fileMenu)
        mainMenu.addItem_(fileMenuItem)

        editMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Edit", None, "")
        editMenu = NSMenu.alloc().initWithTitle_("Edit")
        editMenu.addItemWithTitle_action_keyEquivalent_("Cut", "cut:", "x")
        editMenu.addItemWithTitle_action_keyEquivalent_("Copy", "copy:", "c")
        editMenu.addItemWithTitle_action_keyEquivalent_("Paste", "paste:", "v")
        editMenu.addItem_(NSMenuItem.separatorItem())
        editMenu.addItemWithTitle_action_keyEquivalent_("Select All", "selectAll:", "a")
        editMenuItem.setSubmenu_(editMenu)
        mainMenu.addItem_(editMenuItem)

        helpMenuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_("Help", None, "")
        helpMenu = NSMenu.alloc().initWithTitle_("Help")
        helpMenuItem.setSubmenu_(helpMenu)
        mainMenu.addItem_(helpMenuItem)

        app.setMainMenu_(mainMenu)

    if cls is not None:
        cls(**kwargs)

    if calls is not None:
        for call, kwargs in calls:
            call(**kwargs)

    app.activateIgnoringOtherApps_(True)

    if hasCorefoundationasyncio:
        loop = CoreFoundationEventLoop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_forever()
        finally:
            loop.close()
    else:
        AppHelper.runEventLoop()
