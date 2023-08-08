from AppKit import NSMenuItem, NSMenu

from vanilla.vanillaBase import VanillaCallbackWrapper


def VanillaMenuBuilder(sender, items, menu, resetCallbackWrapper=True):
    """
    Build a menu from a given set of items
    Each items must be a dict with the following keys:

    * **title** title of the menu item (required)
    * **callback** callback when the menu item is clicked (optional)
    * **items** a list of sub menu items, this will build a sub menu for the given menu item.
    * **image** an image placed inside the menu item, must be a NSImage.
    * **state** a menu item state: must be either 0, 1 or -1 (on, off or mixed).
    * **enabled** enable the menu item, must be a bool.
    """
    if resetCallbackWrapper:
        sender._menuItemCallbackWrappers = []
    for item in items:
        if isinstance(item, NSMenuItem):
            menu.addItem_(item)
        elif item == "----":
            item = NSMenuItem.separatorItem()
            menu.addItem_(item)
        else:
            title = item["title"]
            callback = item.get("callback")
            subItems = item.get("items")
            image = item.get("image")
            state = item.get("state")
            enabled = item.get("enabled")

            menuItem = NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, "", "")
            if callback:
                wrapper = VanillaCallbackWrapper(callback)
                sender._menuItemCallbackWrappers.append(wrapper)
                menuItem.setTarget_(wrapper)
                menuItem.setAction_("action:")
            if subItems:
                subMenu = NSMenu.alloc().init()
                VanillaMenuBuilder(sender, subItems, subMenu, resetCallbackWrapper=False)
                menuItem.setSubmenu_(subMenu)

            if image is not None:
                menuItem.setImage_(image)
            if state is not None:
                menuItem.setState_(state)
            if enabled is not None:
                menuItem.setEnabled_(enabled)

            menu.addItem_(menuItem)
