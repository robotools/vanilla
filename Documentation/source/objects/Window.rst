.. highlight:: python

======
Window
======

.. module:: vanilla
.. autoclass:: Window

.. method:: Window.assignToDocument(document)

    Add this window to the list of windows associated with a document.

    **document** should be a *NSDocument* instance.


.. method:: Window.getNSWindow()

    Return the *NSWindow* that this Vanilla object wraps.


.. method:: Window.getNSWindowController()

    Return an *NSWindowController* for the *NSWindow* that this Vanilla
    object wraps, creating a one if needed.


.. method:: Window.open()

    Open the window.


.. method:: Window.close()

    Close the window.

    Once a window has been closed it can not be re-opened.


.. method:: Window.hide()

    Hide the window.


.. method:: Window.show()

    Show the window if it is hidden.


.. method:: Window.makeKey()

    Make the window the key window.


.. method:: Window.makeMain()

    Make the window the main window.


.. method:: Window.setTitle(title)

    Set the title in the window's title bar.

    **title** shoud be a string.


.. method:: Window.getTitle()

    The title in the window's title bar.


.. method:: Window.select()

    Select the window if it is not the currently selected window.


.. method:: Window.isVisible()

    A boolean value representing if the window is visible or not.


.. method:: Window.getPosSize()

    A tuple of form *(left, top, width, height)* representing the window's
    position and size.


.. method:: Window.setPosSize(posSize, animate=True)

    Set the position and size of the window.

    **posSize** A tuple of form *(left, top, width, height)*.


.. method:: Window.center()

    Center the window within the screen.


.. method:: Window.move(x, y, animate=True)

    Move the window by **x** units and **y** units.


.. method:: Window.resize(width, height, animate=True)

    Change the size of the window to **width** and **height**.


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
    | *"resize"*        | Caled immediately after the window is resized.                       |
    +-------------------+----------------------------------------------------------------------+
    | *"became main"*   | Called immediately after the window has become the main window.      |
    +-------------------+----------------------------------------------------------------------+
    | *"resigned main"* | Called immediately after the window has lost its main window status. |
    +-------------------+----------------------------------------------------------------------+
    | *"became key"*    | Called immediately after the window has become the key window.       |
    +-------------------+----------------------------------------------------------------------+
    | *"resigned key"*  | Called immediately after the window has lost its key window status.  |
    +-------------------+----------------------------------------------------------------------+

    *For more information about main and key windows, refer to the Cocoa
    `documentation <http://developer.apple.com/documentation/Cocoa/Conceptual/WinPanel/Concepts/ChangingMainKeyWindow.html>`_
    on the subject.*

    **callback** The callback that will be called when the event occurs. It should accept a *sender* argument which will
    be the Window that called the callback.::

        class WindowBindDemo(object):

            def __init__():
                self.w = Window((200, 200))
                self.w.bind("move", self.windowMoved)
                self.w.open()

            def windowMoved(sender):
                print "window moved!", sender

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
    | *imageNamed* (optional)       | The name of an image already loaded as a *NSImage* by the application.    |
    |                               | Defaults to *None*.                                                       |
    +-------------------------------+---------------------------------------------------------------------------+
    | *imageObject* (optional)      | A _NSImage_ object. Defaults to *None*.                                   |
    +-------------------------------+---------------------------------------------------------------------------+
    | *selectable* (optional)       | A boolean representing if the item is selectable or not. The default      |
    |                               | value is _False_. For more information on selectable toolbar items, refer |
    |                               | to Apple's `documentation <http://tinyurl.com/SelectableItems>`_          |
    +-------------------------------+---------------------------------------------------------------------------+
    | *view* (optional)             | A *NSView* object to be used instead of an image. Defaults to *None*.     |
    +-------------------------------+---------------------------------------------------------------------------+
    | *visibleByDefault* (optional) | If the item should be visible by default pass True to this argument.      |
    |                               | If the item should be added to the toolbar only through the customization |
    |                               | palette, use a value of _False_. Defaults to _True_. |                    |
    +-------------------------------+---------------------------------------------------------------------------+

    **addStandardItems** A boolean, specifying whether the standard Cocoa toolbar items
    should be added. Defaults to *True*. If you set it to *False*, you must specify any
    standard items manually in *toolbarItems*, by using the constants from the AppKit module:

    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarSeparatorItemIdentifier*        | The Separator item.                                            |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarSpaceItemIdentifier*            | The Space item.                                                |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarFlexibleSpaceItemIdentifier*    | The Flexible Space item.                                       |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarShowColorsItemIdentifier*       | The Colors item. Shows the color panel.                        |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarShowFontsItemIdentifier*        | The Fonts item. Shows the font panel.                          |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarCustomizeToolbarItemIdentifier* | The Customize item. Shows the customization palette.           |
    +-------------------------------------------+----------------------------------------------------------------+
    | *NSToolbarPrintItemIdentifier*            | The Print item. Refer to Apple's *NSToolbarItem* documentation |
    |                                           | for more information.                                          |
    +-------------------------------------------+----------------------------------------------------------------+

    Returns a dictionary containing the created toolbar items, mapped by itemIdentifier.
