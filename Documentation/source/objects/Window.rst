.. highlight:: python

======
Window
======

.. module:: vanilla
.. autoclass:: Window
   :inherited-members:
   :members:


.. method:: Window.assignToDocument(document)

    Add this window to the list of windows associated with a document.

    **document** should be a *NSDocument* instance.


.. method:: Window.setTitle(title)

    Set the title in the window's title bar.

    **title** should be a string.


.. method:: Window.setPosSize(posSize, animate=True)

    Set the position and size of the window.

    **posSize** A tuple of form *(left, top, width, height)*.


.. method:: Window.move(x, y, animate=True)

    Move the window by *x* units and *y* units.


.. method:: Window.resize(width, height, animate=True)

    Change the size of the window to *width* and *height*.


.. method:: Window.setDefaultButton(button)

    Set the default button in the window.

    **button** will be bound to the Return and Enter keys.


.. method:: Window.bind(event, callback)

    Bind a callback to an event.

    **event** A string representing the desired event. The options are:

    +-------------------+----------------------------------------------------------------------+
    | *"should close"*  | Called when the user attempts to close the window. This must return  |
    |                   | a bool indicating if the window should be closed or not.             |
    +-------------------+----------------------------------------------------------------------+
    | *"close"*         | Called immediately before the window closes.                         |
    +-------------------+----------------------------------------------------------------------+
    | *"move"*          | Called immediately after the window is moved.                        |
    +-------------------+----------------------------------------------------------------------+
    | *"resize"*        | Called immediately after the window is resized.                      |
    +-------------------+----------------------------------------------------------------------+
    | *"became main"*   | Called immediately after the window has become the main window.      |
    +-------------------+----------------------------------------------------------------------+
    | *"resigned main"* | Called immediately after the window has lost its main window status. |
    +-------------------+----------------------------------------------------------------------+
    | *"became key"*    | Called immediately after the window has become the key window.       |
    +-------------------+----------------------------------------------------------------------+
    | *"resigned key"*  | Called immediately after the window has lost its key window status.  |
    +-------------------+----------------------------------------------------------------------+

    For more information about main and key windows, refer to the Cocoa `documentation`_ on the subject.

    .. _documentation: http://developer.apple.com/library/archive/documentation/Cocoa/Conceptual/WinPanel/Concepts/ChangingMainKeyWindow.html

    **callback** The callback that will be called when the event occurs. It should accept a *sender* argument which will
    be the Window that called the callback.::

        from vanilla import Window

        class WindowBindDemo(object):

            def __init__(self):
                self.w = Window((200, 200))
                self.w.bind("move", self.windowMoved)
                self.w.open()

            def windowMoved(self, sender):
                print("window moved!", sender)

        WindowBindDemo()


.. method:: Window.unbind(event, callback)

    Unbind a callback from an event.

    **event** A string representing the desired event.
    Refer to *bind* for the options.

    **callback** The callback that has been bound to the event.


.. method:: Window.addToolbar(toolbarIdentifier, toolbarItems, addStandardItems=True)

        Add a toolbar to the window.

        **toolbarIdentifier** A string representing a unique name for the toolbar.

        **toolbarItems** An ordered list of dictionaries containing the following items:

        +-------------------------------+---------------------------------------------------------------------------+
        | *itemIdentifier*              | A unique string identifier for the item. This is only used internally.    |
        +-------------------------------+---------------------------------------------------------------------------+
        | *label* (optional)            | The text label for the item. Defaults to *None*.                          |
        +-------------------------------+---------------------------------------------------------------------------+
        | *paletteLabel* (optional)     | The text label shown in the customization palette. Defaults to *label*.   |
        +-------------------------------+---------------------------------------------------------------------------+
        | *toolTip* (optional)          | The tool tip for the item. Defaults to *label*.                           |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imagePath* (optional)        | A file path to an image. Defaults to *None*.                              |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageNamed* (optional)       | The name of an image already loaded as a `NSImage`_ by the application.   |
        |                               | Defaults to *None*.                                                       |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageObject* (optional)      | A `NSImage`_ object. Defaults to *None*.                                  |
        +-------------------------------+---------------------------------------------------------------------------+
        | *imageTemplate* (optional)    | A boolean representing if the image should converted to a template image. |
        +-------------------------------+---------------------------------------------------------------------------+
        | *selectable* (optional)       | A boolean representing if the item is selectable or not. The default      |
        |                               | value is *False*. For more information on selectable toolbar items, refer |
        |                               | to Apple's documentation.                                                 |
        +-------------------------------+---------------------------------------------------------------------------+
        | *view* (optional)             | A *NSView* object to be used instead of an image. Defaults to *None*.     |
        +-------------------------------+---------------------------------------------------------------------------+
        | *visibleByDefault* (optional) | If the item should be visible by default pass *True* to this argument.    |
        |                               | If the item should be added to the toolbar only through the customization |
        |                               | palette, use a value of *False*. Defaults to *True*.                      |
        +-------------------------------+---------------------------------------------------------------------------+

        .. _NSImage: http://developer.apple.com/documentation/appkit/nsimage?language=objc

        **addStandardItems** A boolean, specifying whether the standard Cocoa toolbar items
        should be added. Defaults to *True*. If you set it to *False*, you must specify any
        standard items manually in *toolbarItems*, by using the constants from the AppKit module:

        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarSeparatorItemIdentifier*        | The Separator item.                                  |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarSpaceItemIdentifier*            | The Space item.                                      |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarFlexibleSpaceItemIdentifier*    | The Flexible Space item.                             |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarShowColorsItemIdentifier*       | The Colors item. Shows the color panel.              |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarShowFontsItemIdentifier*        | The Fonts item. Shows the font panel.                |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarCustomizeToolbarItemIdentifier* | The Customize item. Shows the customization palette. |
        +-------------------------------------------+------------------------------------------------------+
        | *NSToolbarPrintItemIdentifier*            | The Print item. Refer to Apple's `NSToolbarItem`_    |
        |                                           | documentation for more information.                  |
        +-------------------------------------------+------------------------------------------------------+

        .. _NSToolbarItem: https://developer.apple.com/documentation/appkit/nstoolbaritem?language=objc

        **displayMode** A string representing the desired display mode for the toolbar.

        +-------------+
        | "default"   |
        +-------------+
        | "iconLabel" |
        +-------------+
        | "icon"      |
        +-------------+
        | "label"     |
        +-------------+

        **sizeStyle** A string representing the desired size for the toolbar

        +-----------+
        | "default" |
        +-----------+
        | "regular" |
        +-----------+
        | "small"   |
        +-----------+

        Returns a dictionary containing the created toolbar items, mapped by itemIdentifier.


.. method:: Window.removeToolbarItem(itemIdentifier)

    Remove a toolbar item by his identifier.

    **itemIdentifier** A unique string identifier for the removed item.
