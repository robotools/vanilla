import time
import objc
from Foundation import NSKeyValueObservingOptionNew, NSKeyValueObservingOptionOld, NSNotFound
from AppKit import *
from nsSubclasses import getNSSubclass
from vanillaBase import VanillaBaseObject, VanillaError, VanillaCallbackWrapper, osVersion


class VanillaTableViewSubclass(NSTableView):

    def textDidEndEditing_(self, notification):
        info = notification.userInfo()
        if info["NSTextMovement"] in [NSReturnTextMovement, NSTabTextMovement, NSBacktabTextMovement]:
            # This is ugly, but just about the only way to do it.
            # NSTableView is determined to select and edit something else,
            # even the text field that it just finished editing, unless we
            # mislead it about what key was pressed to end editing.
            info = dict(info)  # make a copy
            info["NSTextMovement"] = NSIllegalTextMovement
            newNotification = NSNotification.notificationWithName_object_userInfo_(
                    notification.name(),
                    notification.object(),
                    info)
            super(VanillaTableViewSubclass, self).textDidEndEditing_(newNotification)
            self.window().makeFirstResponder_(self)
        else:
            super(VanillaTableViewSubclass, self).textDidEndEditing_(notification)


class VanillaArrayControllerObserver(NSObject):

    def observeValueForKeyPath_ofObject_change_context_(self, keyPath, obj, change, context):
        if hasattr(self, "_targetMethod") and self._targetMethod is not None:
            self._targetMethod()


class VanillaArrayController(NSArrayController):

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        content = self.content()
        columnID = column.identifier()
        item = content[row]
        if isinstance(item, NSDictionary):
            if columnID not in item:
                return
            else:
                return item[columnID]
        else:
            return getattr(item, columnID)()

    def numberOfRowsInTableView_(self, view):
        return len(self.content())

    # drag and drop

    def tableView_writeRowsWithIndexes_toPasteboard_(self,
        tableView, indexes, pboard):
        vanillaWrapper = tableView.vanillaWrapper()
        settings = vanillaWrapper._dragSettings
        if settings is None:
            return False
        indexes = list(vanillaWrapper._iterIndexSet(indexes))
        indexes = vanillaWrapper._getUnsortedIndexesFromSortedIndexes(indexes)
        packCallback = settings["callback"]
        if packCallback is not None:
            objects = packCallback(vanillaWrapper, indexes)
            if not isinstance(objects, NSArray):
                objects = NSArray.arrayWithArray_(objects)
        else:
            objects = NSMutableArray.array()
            for index in indexes:
                obj = vanillaWrapper[index]
                objects.addObject_(obj)
        dragType = settings["type"]
        pboard.declareTypes_owner_([dragType], self)
        pboard.setPropertyList_forType_(objects.description(), dragType)
        return True

    def _handleDrop(self, isProposal, tableView, draggingInfo, row, dropOperation):
        vanillaWrapper = tableView.vanillaWrapper()
        draggingSource = draggingInfo.draggingSource()
        sourceForCallback = draggingSource
        if hasattr(draggingSource, "vanillaWrapper") and getattr(draggingSource, "vanillaWrapper") is not None:
            sourceForCallback = getattr(draggingSource, "vanillaWrapper")()
        # make the info dict
        dropOnRow = dropOperation == NSTableViewDropOn
        dropInformation = dict(isProposal=isProposal, dropOnRow=dropOnRow, rowIndex=row, data=None, source=sourceForCallback)
        # drag from self
        if draggingSource == tableView:
            if vanillaWrapper._selfDropSettings is None:
                return NSDragOperationNone
            settings = vanillaWrapper._selfDropSettings
            return self._handleDropBasedOnSettings(settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation)
        # drag from same window
        window = tableView.window()
        if window is not None and draggingSource is not None and window == draggingSource.window() and vanillaWrapper._selfWindowDropSettings is not None:
            if vanillaWrapper._selfWindowDropSettings is None:
                return NSDragOperationNone
            settings = vanillaWrapper._selfWindowDropSettings
            return self._handleDropBasedOnSettings(settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation)
        # drag from same document
        document = tableView.window().document()
        if document is not None and draggingSource is not None and document == draggingSource.window().document():
            if vanillaWrapper._selfDocumentDropSettings is None:
                return NSDragOperationNone
            settings = vanillaWrapper._selfDocumentDropSettings
            return self._handleDropBasedOnSettings(settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation)
        # drag from same application
        applicationWindows = NSApp().windows()
        if draggingSource is not None and draggingSource is not None and draggingSource.window() in applicationWindows:
            if vanillaWrapper._selfApplicationDropSettings is None:
                return NSDragOperationNone
            settings = vanillaWrapper._selfApplicationDropSettings
            return self._handleDropBasedOnSettings(settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation)
        # fall back to drag from other application
        if vanillaWrapper._otherApplicationDropSettings is None:
            return NSDragOperationNone
        settings = vanillaWrapper._otherApplicationDropSettings
        return self._handleDropBasedOnSettings(settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation)

    def _handleDropBasedOnSettings(self, settings, vanillaWrapper, dropOnRow, draggingInfo, dropInformation):
        # handle drop position
        validDropPosition = self._validateDropPosition(settings, dropOnRow)
        if not validDropPosition:
            return NSDragOperationNone
        # unpack data
        dropInformation["data"] = self._unpackPboard(settings, draggingInfo)
        # call the callback
        result = settings["callback"](vanillaWrapper, dropInformation)
        if result:
            return settings.get("operation", NSDragOperationCopy)
        return NSDragOperationNone

    def _validateDropPosition(self, settings, dropOnRow):
        if dropOnRow and not settings.get("allowsDropOnRows", False):
            return False
        if not dropOnRow and not settings.get("allowsDropBetweenRows", True):
            return False
        return True

    def _unpackPboard(self, settings, draggingInfo):
        pboard = draggingInfo.draggingPasteboard()
        data = pboard.propertyListForType_(settings["type"])
        if isinstance(data, (NSString, objc.pyobjc_unicode)):
            data = data.propertyList()
        return data

    def tableView_validateDrop_proposedRow_proposedDropOperation_(self,
        tableView, draggingInfo, row, dropOperation):
        return self._handleDrop(True, tableView, draggingInfo, row, dropOperation)

    def tableView_acceptDrop_row_dropOperation_(self,
        tableView, draggingInfo, row, dropOperation):
        return self._handleDrop(False, tableView, draggingInfo, row, dropOperation)


class VanillaTableViewDelegate(NSObject):

    def tableView_viewForTableColumn_row_(self, tableView, column, row):
        identifier = column.identifier()
        view = tableView.makeViewWithIdentifier_owner_(identifier, self)
        if view is None:
            wrapper = tableView.vanillaWrapper()
            view = wrapper._makeCellViewForIdentifier(identifier)
        return view


class List(VanillaBaseObject):

    """
    A control that shows a list of items. These lists can contain one or more columns.

    A single column example::

        from vanilla import *

        class ListDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0), ["A", "B", "C"],
                             selectionCallback=self.selectionCallback)
                self.w.open()

            def selectionCallback(self, sender):
                print sender.getSelection()

        ListDemo()

    A mutliple column example::

        from vanilla import *

        class ListDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0),
                             [{"One": "A", "Two": "a"}, {"One": "B", "Two": "b"}],
                             columnDescriptions=[{"title": "One"}, {"title": "Two"}],
                             selectionCallback=self.selectionCallback)
                self.w.open()

            def selectionCallback(self, sender):
                print sender.getSelection()

        ListDemo()

    List objects behave like standard Python lists. For xample, given this List:::

        self.w.myList = List((10, 10, 200, 100), ["A", "B", "C"])

    The following Python list methods work:::

        # Getting the length of the List.
        >>> len(self.w.myList)
        3

        # Retrieving an item or items from a List.
        >>> self.w.myList[1]
        "B"
        >>> self.w.myList[:2]
        ["A", "B"]

        # Setting an item in a List.
        >>> self.w.myList[1] = "XYZ"
        >>> self.w.myList.get()
        ["A", "XYZ", "C"]

        # Deleting an item at an index in a List.
        >>> del self.w.myList[1]
        >>> self.w.myList.get()
        ["A", "C"]

        # Appending an item to a List.
        >>> self.w.myList.append("Z")
        >>> self.w.myList.get()
        ["A", "B", "C", "Z"]

        # Removing the first occurance of an item in a List.
        >>> self.w.myList.remove("A")
        >>> self.w.myList.get()
        ["B", "C"]

        # Getting the index for the first occurance of an item in a List.
        >>> self.w.myList.index("B")
        1

        # Inserting an item into a List.
        >>> self.w.myList.insert(1, "XYZ")
        >>> self.w.myList.get()
        ["A", "XYZ", "B", "C"]

        # Extending a List.
        >>> self.w.myList.extend(["X", "Y", "Z"])
        >>> self.w.myList.get()
        ["A", "B", "C", "X", "Y", "Z"]

        # Iterating over a List.
        >>> for i in self.w.myList:
        >>>     i
        "A"
        "B"
        "C"

    **posSize** Tuple of form *(left, top, width, height)* representing the
    position and size of the list.

    **items** The items to be displayed in the list. In the case of multiple
    column lists, this should be a list of dictionaries with the data for
    each column keyed by the column key as defined in columnDescriptions.

    **columnDescriptions** An ordered list of dictionaries describing the
    columns. This is only necessary for multiple column lists.

    +--------------------------------+--------------------------------------------------------------------------------+
    | *"title"*                      | The title to appear in the column header.                                      |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"key"* (optional)             | The key from which this column should get                                      |
    |                                | its data from each dictionary in *items*. If                                   |
    |                                | nothing is given, the key will be the string                                   |
    |                                | given in *title*.                                                              |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"formatter"* (optional)       | An `NSFormatter` <http://tinyurl.com/NSFormatter>`_                            |
    |                                | for cntrolling the display and input of the                                    |
    |                                | column's cells.                                                                |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"cell"* (optional)            | A cell type to be displayed in the column.                                     |
    |                                | If nothing is given, a text cell is used.                                      |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"editable"* (optional)        | Enable or disable editing in the column. If                                    |
    |                                | nothing is given, it will follow the                                           |
    |                                | editability of the rest of the list.                                           |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"width"* (optional)           | The width of the column.                                                       |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"minWidth"* (optional)        | The minimum width of the column. The fallback is `width`.                      |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"maxWidth"* (optional)        | The maximum width of the column. The fallback is `width`.                      |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *"allowsSorting"* (optional)   | A boolean representing that this column allows the user                        |
    |                                | to sort the table by clicking the column's header.                             |
    |                                | The fallback is `True`. If a List is set to disallow                           |
    |                                | sorting the column level settings will be ignored                              |
    +--------------------------------+--------------------------------------------------------------------------------+
    | *binding* (optional)           | A string indicating which `binding object <http://tinyurl.com/CocoaBindings>`_ |
    |                                | the column's cell should be bound to. By                                       |
    |                                | default, this is "value." You should only                                      |
    |                                | override this in very specific cases.                                          |
    +--------------------------------+--------------------------------------------------------------------------------+

    **showColumnTitles** Boolean representing if the column titles should be shown or not.
    Column titles will not be shown in single column lists.

    **selectionCallback** Callback to be called when the selection in the list changes.

    **doubleClickCallback** Callback to be called when an item is double clicked.

    **editCallback** Callback to be called after an item has been edited.

    **enableDelete** A boolean representing if items in the list can be deleted via the interface.

    **allowsMultipleSelection** A boolean representing if the list allows more than one item to be selected.

    **allowsEmptySelection** A boolean representing if the list allows zero items to be selected.

    **allowsSorting** A boolean indicating if the list allows user sorting by clicking column headers.

    **drawVerticalLines** Boolean representing if vertical lines should be drawn in the list.

    **drawHorizontalLines** Boolean representing if horizontal lines should be drawn in the list.

    **drawFocusRing** Boolean representing if the standard focus ring should be drawn when the list is selected.

    **rowHeight** The height of the rows in the list.

    **autohidesScrollers** Boolean representing if scrollbars should automatically be hidden if possible.

    **selfDropSettings** A dictionary defining the drop settings when the source of the drop
    is this list. The dictionary form is described below.

    **selfWindowDropSettings** A dictionary defining the drop settings when the source of the drop
    is contained the same document as this list. The dictionary form is described below.

    **selfDocumentDropSettings** A dictionary defining the drop settings when the source of the drop
    is contained the same window as this list. The dictionary form is described below.

    **selfApplicationDropSettings** A dictionary defining the drop settings when the source of the drop
    is contained the same application as this list. The dictionary form is described below.

    **otherApplicationDropSettings** A dictionary defining the drop settings when the source of the drop
    is contained an application other than the one that contains this list. The dictionary form is described below.

    The drop settings dictionaries should be of this form:

    +-----------------------------------+--------------------------------------------------------------------+
    | *type*                            | A single drop type indicating what drop types the list accepts.    |
    |                                   | For example, NSFilenamesPboardType or "MyCustomPboardType".        |
    +-----------------------------------+--------------------------------------------------------------------+
    | *operation* (optional)            | A "drag operation <http://tinyurl.com/NSDraggingIn>`_ that         |
    |                                   | the list accepts. The default is *NSDragOperationCopy*.            |
    +-----------------------------------+--------------------------------------------------------------------+
    | *allowDropBetweenRows* (optional) | A boolean indicating if the list accepts drops between rows.       |
    |                                   | The default is True.                                               |
    +-----------------------------------+--------------------------------------------------------------------+
    | *allowDropOnRow* (optional)       | A boolean indicating if the list accepts drops on rows.            |
    |                                   | The default is False.                                              |
    +-----------------------------------+--------------------------------------------------------------------+
    | *callback*                        | Callback to be called when a drop is proposed and when a drop      |
    |                                   | is to occur. This method should return a boolean representing      |
    |                                   | if the drop is acceptable or not. This method must accept *sender* |
    |                                   | and *dropInfo* arguments. The _dropInfo_ will be a dictionary as   |
    |                                   | described below.                                                   |
    +-----------------------------------+--------------------------------------------------------------------+

    The dropInfo dictionary passed to drop callbacks will be of this form:

    +--------------+--------------------------------------------------------------------------------------------+
    | *data*       | The data proposed for the drop. This data will be of the type specified by dropDataFormat. |
    +--------------+--------------------------------------------------------------------------------------------+
    | *rowIndex*   | The row where the drop is proposed.                                                        |
    +--------------+--------------------------------------------------------------------------------------------+
    | *source*     | The source from which items are being dragged. If this object is wrapped by Vanilla, the   |
    |              | Vanilla object will be passed as the source.                                               |
    +--------------+--------------------------------------------------------------------------------------------+
    | *dropOnRow*  | A boolean representing if the row is being dropped on. If this is False, the drop should   |
    |              | occur between rows.                                                                        |
    +--------------+--------------------------------------------------------------------------------------------+
    | *isProposal* | A boolean representing if this call is simply proposing the drop or if it is time to       |
    |              | accept the drop.                                                                           |
    +--------------+--------------------------------------------------------------------------------------------+
    """

    nsScrollViewClass = NSScrollView
    nsTableViewClass = VanillaTableViewSubclass
    nsArrayControllerClass = VanillaArrayController
    nsArrayControllerObserverClass = VanillaArrayControllerObserver
    nsTableViewDelegateClass = VanillaTableViewDelegate

    def __init__(self, posSize, items, columnDescriptions=None, showColumnTitles=True,
                selectionCallback=None, doubleClickCallback=None, editCallback=None,
                enableDelete=False,
                allowsMultipleSelection=True, allowsEmptySelection=True,
                allowsSorting=True,
                drawVerticalLines=False, drawHorizontalLines=False,
                autohidesScrollers=True, drawFocusRing=True, rowHeight=17.0,
                selfDropSettings=None,
                selfWindowDropSettings=None,
                selfDocumentDropSettings=None,
                selfApplicationDropSettings=None,
                otherApplicationDropSettings=None,
                dragSettings=None,
                # deprecated kwargs
                enableTypingSensitivity=False
                ):

        # deduce the table view mode. default to cell mode < OS 10.10.
        cells = 0
        views = 0
        if columnDescriptions:
            for item in columnDescriptions:
                cell = item.get("cell")
                if cell is not None:
                    if isinstance(cell, NSCell):
                        cells += 1
                    else:
                        views += 1
        if cells and views:
            raise VanillaError("The column descriptions contain a mixture of cells and views. This is not allowed.")
        if views and osVersion < "10.10":
            raise VanillaError("The column descriptions contain views. This is not supported by vanilla in OS %s." % osVersion)
        if cells:
            self._mode = "cell"
        elif osVersion < "10.10":
            self._mode = "cell"
        else:
            self._mode = "view"
            self._cellViewFactories = {}
        # basic construction
        self._posSize = posSize
        self._enableDelete = enableDelete
        self._nsObject = getNSSubclass(self.nsScrollViewClass)(self)
        self._nsObject.setAutohidesScrollers_(autohidesScrollers)
        self._nsObject.setHasHorizontalScroller_(True)
        self._nsObject.setHasVerticalScroller_(True)
        self._nsObject.setBorderType_(NSBezelBorder)
        self._nsObject.setDrawsBackground_(True)
        self._setAutosizingFromPosSize(posSize)
        self._allowsSorting = allowsSorting
        # add a table view to the scroll view
        self._tableView = getNSSubclass(self.nsTableViewClass)(self)
        self._nsObject.setDocumentView_(self._tableView)
        # set up the delegate
        if self._mode == "view":
            self._delegate = VanillaTableViewDelegate.alloc().init()
            self._tableView.setDelegate_(self._delegate)
        # set up an observer that will be called by the bindings when a cell is edited
        self._editCallback = editCallback
        self._editObserver = self.nsArrayControllerObserverClass.alloc().init()
        if editCallback is not None:
            self._editObserver._targetMethod = self._edit # circular reference to be killed in _breakCycles
        # wrap all the items
        items = [self._wrapItem(item) for item in items]
        items = NSMutableArray.arrayWithArray_(items)
        # set up an array controller
        self._arrayController = self.nsArrayControllerClass.alloc().initWithContent_(items)
        self._arrayController.setSelectsInsertedObjects_(False)
        self._arrayController.setAvoidsEmptySelection_(not allowsEmptySelection)
        self._tableView.setDataSource_(self._arrayController)
        # hide the header
        if not showColumnTitles or not columnDescriptions:
            self._tableView.setHeaderView_(None)
            self._tableView.setCornerView_(None)
        # set the table attributes
        self._tableView.setUsesAlternatingRowBackgroundColors_(True)
        if not drawFocusRing:
            self._tableView.setFocusRingType_(NSFocusRingTypeNone)
        self._tableView.setRowHeight_(rowHeight)
        self._tableView.setAllowsEmptySelection_(allowsEmptySelection)
        self._tableView.setAllowsMultipleSelection_(allowsMultipleSelection)
        if drawVerticalLines or drawHorizontalLines:
            if drawVerticalLines and drawHorizontalLines:
                lineType = NSTableViewSolidVerticalGridLineMask | NSTableViewSolidHorizontalGridLineMask
            elif drawVerticalLines:
                lineType = NSTableViewSolidVerticalGridLineMask
            else:
                lineType = NSTableViewSolidHorizontalGridLineMask
            self._tableView.setGridStyleMask_(lineType)
        # set up the columns. also make a flag that will be used
        # when unwrapping items.
        self._orderedColumnIdentifiers = []
        if not columnDescriptions:
            self._makeColumnWithoutColumnDescriptions()
            self._itemsWereDict = False
        else:
            self._makeColumnsWithColumnDescriptions(columnDescriptions)
            self._itemsWereDict = True
        # set up an observer that will be called by the bindings when the selection changes.
        # this needs to be done ater the items have been added to the table. otherwise,
        # the selection method will be called when the items are added to the table view.
        if selectionCallback is not None:
            self._selectionCallback = selectionCallback
            self._selectionObserver = self.nsArrayControllerObserverClass.alloc().init()
            self._arrayController.addObserver_forKeyPath_options_context_(self._selectionObserver, "selectionIndexes", NSKeyValueObservingOptionNew, 0)
            self._selectionObserver._targetMethod = self._selection # circular reference to be killed in _breakCycles
        # set the double click callback the standard way
        if doubleClickCallback is not None:
            self._doubleClickTarget = VanillaCallbackWrapper(doubleClickCallback)
            self._tableView.setTarget_(self._doubleClickTarget)
            self._tableView.setDoubleAction_("action:")
        # set the drop data
        self._selfDropSettings = selfDropSettings
        self._selfWindowDropSettings = selfWindowDropSettings
        self._selfDocumentDropSettings = selfDocumentDropSettings
        self._selfApplicationDropSettings = selfApplicationDropSettings
        self._otherApplicationDropSettings = otherApplicationDropSettings
        allDropTypes = []
        for settings in (selfDropSettings, selfWindowDropSettings, selfDocumentDropSettings, selfApplicationDropSettings, otherApplicationDropSettings):
            if settings is None:
                continue
            dropType = settings["type"]
            allDropTypes.append(dropType)
        self._tableView.registerForDraggedTypes_(allDropTypes)
        # set the default drop operation masks
        notLocal = NSDragOperationNone
        if otherApplicationDropSettings is not None:
            notLocal = otherApplicationDropSettings.get("operation", NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(notLocal, False)
        local = NSDragOperationNone
        for settings in (selfDropSettings, selfDocumentDropSettings, selfApplicationDropSettings):
            if settings is None:
                continue
            local = settings.get("operation", NSDragOperationCopy)
        self._tableView.setDraggingSourceOperationMask_forLocal_(local, True)
        # set the drag data
        self._dragSettings = dragSettings

    def getNSScrollView(self):
        """
        Return the *NSScrollView* that this object wraps.
        """
        return self._nsObject

    def getNSTableView(self):
        """
        Return the *NSTableView* that this object wraps.
        """
        return self._tableView

    def _breakCycles(self):
        super(List, self)._breakCycles()
        if hasattr(self, "_editCallback") and self._editObserver is not None:
            self._editObserver._targetMethod = None
        if hasattr(self, "_selectionCallback") and self._selectionCallback is not None:
            self._selectionObserver._targetMethod = None
        if hasattr(self, "_doubleClickTarget") and self._doubleClickTarget is not None:
            self._doubleClickTarget.callback = None
        self._selfDropSettings = None
        self._selfWindowDropSettings = None
        self._selfDocumentDropSettings = None
        self._otherApplicationDropSettings = None
        self._otherApplicationDropSettings = None

    def _handleColumnWidths(self, columnDescriptions):
        # we also use this opportunity to determine if
        # autoresizing should be set for the table.
        autoResize = True
        for column in columnDescriptions:
            if column.get("width") is not None:
                autoResize = False
                break
        if autoResize:
            self._setColumnAutoresizing()

    def _setColumnAutoresizing(self):
        self._tableView.setColumnAutoresizingStyle_(NSTableViewUniformColumnAutoresizingStyle)

    def _makeCellViewForIdentifier(self, identifier):
        factory, kwargs = self._cellViewFactories[identifier]
        view = factory(**kwargs)
        view.setIdentifier_(identifier)
        return view

    def _makeColumnWithoutColumnDescriptions(self):
        self._setColumnAutoresizing()
        column = NSTableColumn.alloc().initWithIdentifier_("item")
        self._orderedColumnIdentifiers.append("item")
        if self._mode == "cell":
            column.dataCell().setDrawsBackground_(False)
        else:
            self._cellViewFactories["item"] = (TextFieldCellView, {})
        if self._arrayController is not None:
            # assign the key to the binding
            keyPath = "arrangedObjects.item"
            column.bind_toObject_withKeyPath_options_("value", self._arrayController, keyPath, None)
            # set the column as editable if we have a callback
            if self._editCallback is not None:
                self._arrayController.addObserver_forKeyPath_options_context_(self._editObserver, keyPath, NSKeyValueObservingOptionNew, 0)
            else:
                column.setEditable_(False)
        # finally, add the column to the table view
        self._tableView.addTableColumn_(column)
        # force the columns to adjust their widths if possible. (needed in 10.10)
        self._tableView.sizeToFit()

    def _makeColumnsWithColumnDescriptions(self, columnDescriptions):
        # make sure that the column widths are in the correct format.
        self._handleColumnWidths(columnDescriptions)
        # create each column.
        tableAllowsSorting = self._allowsSorting
        for columnIndex, data in enumerate(columnDescriptions):
            title = data["title"]
            key = data.get("key", title)
            width = data.get("width")
            minWidth = data.get("minWidth", width)
            maxWidth = data.get("maxWidth", width)
            formatter = data.get("formatter")
            cell = data.get("cell")
            editable = data.get("editable")
            allowsSorting = data.get("allowsSorting", True)
            binding = data.get("binding", "value")
            keyPath = "arrangedObjects.%s" % key
            # instantiate the column.
            column = NSTableColumn.alloc().initWithIdentifier_(key)
            self._orderedColumnIdentifiers.append(key)
            # set the width resizing mask
            if width is not None:
                if width == minWidth and width == maxWidth:
                    mask = NSTableColumnNoResizing
                else:
                    mask = NSTableColumnUserResizingMask | NSTableColumnAutoresizingMask
            else:
                mask = NSTableColumnUserResizingMask | NSTableColumnAutoresizingMask
            column.setResizingMask_(mask)
            # set the header cell
            column.headerCell().setTitle_(title)
            # set the data cell
            if self._mode == "cell":
                if cell is None:
                    cell = column.dataCell()
                    cell.setDrawsBackground_(False)
                    cell.setStringValue_("")  # cells have weird default values
                else:
                    column.setDataCell_(cell)
                if formatter is not None:
                    cell.setFormatter_(formatter)
            else:
                if cell is None:
                    view = TextFieldCellView
                    kwargs = {}
                else:
                    view = cell["view"]
                    kwargs = cell.get("settings", {})
                if formatter is not None:
                    kwargs["formatter"] = formatter
                cell = (view, kwargs)
                self._cellViewFactories[key] = cell
            if self._arrayController is not None:
                bindingOptions = None
                if not tableAllowsSorting or not allowsSorting:
                    bindingOptions = {NSCreatesSortDescriptorBindingOption : False}
                # assign the key to the binding
                column.bind_toObject_withKeyPath_options_(binding, self._arrayController, keyPath, bindingOptions)
            # set the editability of the column.
            # if no value was defined in the column data,
            # base the editability on the presence of
            # an edit callback.
            if editable is None and self._editCallback is None:
                editable = False
            elif editable is None and self._editCallback is not None:
                editable = True
            if editable:
                if self._arrayController is not None:
                    self._arrayController.addObserver_forKeyPath_options_context_(self._editObserver, keyPath, NSKeyValueObservingOptionNew, 0)
            else:
                column.setEditable_(False)
            # finally, add the column to the table view
            self._tableView.addTableColumn_(column)
            if width is not None:
                # do this *after* adding the column to the table, or the first column
                # will have the wrong width (at least on 10.3)
                column.setWidth_(width)
                column.setMinWidth_(minWidth)
                column.setMaxWidth_(maxWidth)
        # force the columns to adjust their widths if possible. (needed in 10.10)
        self._tableView.sizeToFit()

    def _wrapItem(self, item):
        # if the item is an instance of NSObject, assume that
        # it is KVC compliant and return it.
        if isinstance(item, NSObject):
            return item
        # this is where we ensure key-value coding compliance.
        # in order to do this, each item must be a NSDictionary
        # or, in the case of editable Lists, NSMutableDictionary.
        if self._editCallback is None:
            dictClass = NSDictionary
        else:
            dictClass = NSMutableDictionary
        # if the item is already in the proper class, pass.
        if isinstance(item, dictClass):
            pass
        # convert a dictionary to the proper dictionary class.
        elif isinstance(item, dict) or isinstance(item, NSDictionary):
            item = NSMutableDictionary.dictionaryWithDictionary_(item)
        # the item is not a dictionary, so wrap it inside of a dictionary.
        else:
            item = NSMutableDictionary.dictionaryWithDictionary_({"item": item})
        return item

    def _edit(self):
        if self._editCallback is not None:
            self._editCallback(self)

    def _selection(self):
        if self._selectionCallback is not None: 
            self._selectionCallback(self)

    # -------------
    # list behavior
    # -------------

    def __len__(self):
        return len(self._arrayController.content())

    def __getitem__(self, index):
        item = self._arrayController.content()[index]
        if not self._itemsWereDict:
            item = item["item"]
        return item

    def __setitem__(self, index, value):
        # rather than inserting a new item, replace the
        # content of the existing item at the index.
        # this will call the editCallback if assigned
        # so temporarily suspend it.
        editCallback = self._editCallback
        self._editCallback = None
        item = self._arrayController.content()[index]
        if self._itemsWereDict:
            for key, value in value.items():
                item[key] = value
        else:
            item["item"] = value
        self._editCallback = editCallback

    def __delitem__(self, index):
        index = self._getSortedIndexesFromUnsortedIndexes([index])[0]
        self._arrayController.removeObjectAtArrangedObjectIndex_(index)

    def __contains__(self, item):
        item = self._wrapItem(item)
        return self._arrayController.content().containsObject_(item)

    def append(self, item):
        item = self._wrapItem(item)
        self._arrayController.addObject_(item)

    def remove(self, item):
        index = self.index(item)
        del self[index]

    def index(self, item):
        item = self._wrapItem(item)
        return self._arrayController.content().index(item)

    def insert(self, index, item):
        item = self._wrapItem(item)
        if index < len(self._arrayController.content()):
            index = self._getSortedIndexesFromUnsortedIndexes([index])[0]
        self._arrayController.insertObject_atArrangedObjectIndex_(item, index)

    def extend(self, items):
        items = [self._wrapItem(item) for item in items]
        self._arrayController.addObjects_(items)

    # ----------------
    # vanilla behavior
    # ----------------

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        self._tableView.setEnabled_(onOff)

    def set(self, items):
        """
        Set the items in the list.

        **items** should follow the same format as described in the constructor.
        """
        items = [self._wrapItem(item) for item in items]
        items = NSMutableArray.arrayWithArray_(items)
        self._arrayController.setContent_(items)

    def get(self):
        """
        Get the list of items in the list.
        """
        items = list(self._arrayController.content())
        if not self._itemsWereDict:
            items = [item["item"] for item in items]
        return items

    def _iterIndexSet(self, s):
        i = s.firstIndex()
        while i != NSNotFound:
            yield i
            i = s.indexGreaterThanIndex_(i)

    def getEditedColumnAndRow(self):
        # get the column and unsort
        columnIndex = self._tableView.editedColumn()
        if columnIndex != -1:
            column = self._tableView.tableColumns()[columnIndex]
            identifier = column.identifier()
            columnIndex = self._orderedColumnIdentifiers.index(identifier)
        # get the row and unsort
        rowIndex = self._tableView.editedRow()
        if rowIndex != -1:
            rowIndex = self._getUnsortedIndexesFromSortedIndexes([rowIndex])[0]
        return columnIndex, rowIndex

    def getSelection(self):
        """
        Get a list of indexes of selected items in the list.
        """
        selectedRowIndexes = self._tableView.selectedRowIndexes()
        # if nothing is selected return an empty list
        if not selectedRowIndexes:
            return []
        # create a list containing only the selected indexes.
        selectedRowIndexes = list(self._iterIndexSet(selectedRowIndexes))
        return self._getUnsortedIndexesFromSortedIndexes(selectedRowIndexes)

    def setSelection(self, selection):
        """
        Set the selected items in the list.

        **selection** should be a list of indexes.
        """
        indexes = self._getSortedIndexesFromUnsortedIndexes(selection)
        indexSet = NSMutableIndexSet.indexSet()
        for index in selection:
            indexSet.addIndex_(index)
        self._arrayController.setSelectionIndexes_(indexSet)
        self.scrollToSelection()

    def _removeSelection(self):
        selection = self.getSelection()
        selection = self._getSortedIndexesFromUnsortedIndexes(selection)
        indexSet = NSMutableIndexSet.indexSet()
        for index in selection:
            indexSet.addIndex_(index)
        self._arrayController.removeObjectsAtArrangedObjectIndexes_(indexSet)

    def scrollToSelection(self):
        """Scroll the selected rows to visible."""
        selection = self.getSelection()
        if not selection:
            return
        indexes = self._getSortedIndexesFromUnsortedIndexes(selection)
        index = min(indexes)
        self._tableView.scrollRowToVisible_(index)

    # methods for handling sorted/unsorted index conversion

    def _getUnsortedIndexesFromSortedIndexes(self, indexes):
        arrayController = self._arrayController
        sortDescriptors = arrayController.sortDescriptors()
        # no sorting has been done. therefore, no unsorting
        # needs to be done.
        if not sortDescriptors:
            return indexes
        unsortedArray = arrayController.content()
        sortedArray = unsortedArray.sortedArrayUsingDescriptors_(sortDescriptors)
        # create a dict of (address, obj) for the sorted
        # objects at the requested indexes.
        sortedObjects = [(id(sortedArray[index]), sortedArray[index]) for index in indexes]
        sortedObjects = dict.fromkeys(sortedObjects)
        # find the indexes of the ubsorted objects matching
        # the sorted objects
        unsortedIndexes = []
        for index in xrange(len(unsortedArray)):
            obj = unsortedArray[index]
            test = (id(obj), obj)
            if test in sortedObjects:
                unsortedIndexes.append(index)
                del sortedObjects[test]
            if not sortedObjects:
                break
        return unsortedIndexes

    def _getSortedIndexesFromUnsortedIndexes(self, indexes):
        arrayController = self._arrayController
        sortDescriptors = arrayController.sortDescriptors()
        # no sorting has been done. therefore, no unsorting
        # needs to be done.
        if not sortDescriptors:
            return indexes
        unsortedArray = arrayController.content()
        sortedArray = unsortedArray.sortedArrayUsingDescriptors_(sortDescriptors)
        # create a dict of (address, obj) for the unsorted
        # objects at the requested indexes.
        unsortedObjects = [(id(unsortedArray[index]), unsortedArray[index]) for index in indexes]
        unsortedObjects = dict.fromkeys(unsortedObjects)
        # find the indexes of the sorted objects matching
        # the unsorted objects
        sortedIndexes = []
        for index in xrange(len(sortedArray)):
            obj = sortedArray[index]
            test = (id(obj), obj)
            if test in unsortedObjects:
                sortedIndexes.append(index)
                del unsortedObjects[test]
            if not unsortedObjects:
                break
        return sortedIndexes


# -------------------
# Cell View Factories
# -------------------

def TextFieldCellView(formatter=None):
    view = NSTextField.alloc().init()
    view.setBordered_(False)
    view.setDrawsBackground_(False)
    view.setEditable_(True)
    if formatter is not None:
        view.setFormatter_(formatter)
    return view

def CheckBoxListCell(title=None):
    """
    An object that displays a check box in a List column.

    **This object should only be used in the *columnDescriptions*
    argument during the construction of a List.**

    **title** The title to be set in *all* items in the List column.

    Example::

        from vanilla import *

        class CheckBoxListCellDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0),
                             [{"value": True}, {"value": False}],
                             columnDescriptions=[{"title": "value", "cell": CheckBoxListCell()}],
                             editCallback=self.editCallback)
                self.w.open()

            def editCallback(self, sender):
                print sender.get()

        CheckBoxListCellDemo()
    """
    cell = NSButtonCell.alloc().init()
    cell.setButtonType_(NSSwitchButton)
    cell.setControlSize_(NSSmallControlSize)
    font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize))
    cell.setFont_(font)
    if title is None:
        title = ""
    cell.setTitle_(title)
    return cell

def SliderListCellView(minValue=0, maxValue=100, tickMarkCount=None, stopOnTickMarks=False):
    slider = NSSlider.alloc().init()
    slider.setControlSize_(NSSmallControlSize)
    slider.setMinValue_(minValue)
    slider.setMaxValue_(maxValue)
    if tickMarkCount:
        slider.setNumberOfTickMarks_(tickMarkCount)
        if stopOnTickMarks:
            slider.setAllowsTickMarkValuesOnly_(True)
    return slider


def SliderListCell(minValue=0, maxValue=100, tickMarkCount=None, stopOnTickMarks=False):
    """
    An object that displays a slider in a List column.

    **This object should only be used in the *columnDescriptions*
    argument during the construction of a List.**

    **minValue** The minimum value for the slider.

    **maxValue** The maximum value for the slider.

    **tickMarkCount** The number of tick marcks to be displayed on the slider.
    If *None* is given, no tick marks will be displayed.

    **stopOnTickMarks** Boolean representing if the slider knob should only
    stop on the tick marks.

    Example::

        from vanilla import *

        class SliderListCellDemo(object):

            def __init__(self):
                self.w = Window((200, 100))
                self.w.myList = List((0, 0, -0, -0),
                            [{"value1": 30, "value2": 70}],
                            columnDescriptions=[
                                {"title": "value1", "cell": SliderListCell()},
                                {"title": "value2", "cell": SliderListCell(tickMarkCount=10)},
                            ],
                            editCallback=self.editCallback)
                self.w.open()

            def editCallback(self, sender):
                print sender.get()

        SliderListCellDemo()
    """
    cell = NSSliderCell.alloc().init()
    cell.setControlSize_(NSSmallControlSize)
    cell.setMinValue_(minValue)
    cell.setMaxValue_(maxValue)
    if tickMarkCount:
        cell.setNumberOfTickMarks_(tickMarkCount)
        if stopOnTickMarks:
            cell.setAllowsTickMarkValuesOnly_(True)
    return cell


def PopUpButtonListCell(items):
    """
    An object that displays a pop up list in a List column.

    **This object should only be used in the *columnDescriptions*
    argument during the construction of a List.**

    **items** The items that should appear in the pop up list.

    Note: when using this cell in a List, the `binding` in the
    column description must be set to `selectedValue`.

    Example::

        from vanilla import *

        class PopUpButtonListCellDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0),
                            [{"value": "A"}, {"value": "B"}],
                            columnDescriptions=[
                                {"title": "value", "cell": PopUpButtonListCell(["A", "B", "C"]), "binding": "selectedValue"}
                            ],
                            editCallback=self.editCallback)
                self.w.open()

            def editCallback(self, sender):
                print sender.get()

        PopUpButtonListCellDemo()
    """
    cell = NSPopUpButtonCell.alloc().init()
    cell.setBordered_(False)
    # add the basic items
    titles = []
    for title in items:
        if isinstance(title, (NSString, NSAttributedString)):
            title = title.string()
        titles.append(title)
    cell.addItemsWithTitles_(titles)
    # add attributed titles
    for index, title in enumerate(items):
        if not isinstance(title, NSAttributedString):
            continue
        item = cell.itemAtIndex_(index)
        item.setAttributedTitle_(title)
    return cell


def ImageListCell(horizontalAlignment="center", verticalAlignment="center", scale="proportional"):
    """
    **horizontalAlignment** A string representing the desired horizontal
    alignment of the image in the view. The options are:

    +-------------+-------------------------+
    | "left"      | Image is aligned left.  |
    +-------------+-------------------------+
    | "right"     | Image is aligned right. |
    +-------------+-------------------------+
    | "center"    | Image is centered.      |
    +-------------+-------------------------+

    **verticalAlignment** A string representing the desired vertical alignment
    of the image in the view. The options are:

    +-------------+--------------------------+
    | "top"       | Image is aligned top.    |
    +-------------+--------------------------+
    | "bottom"    | Image is aligned bottom. |
    +-------------+--------------------------+
    | "center"    | Image is centered.       |
    +-------------+--------------------------+

    **scale** A string representing the desired scale style of the image in the
    view. The options are:

    +----------------+----------------------------------------------+
    | "porportional" | Proportionally scale the image to fit in the |
    |                | view if it is larger than the view.          |
    +----------------+----------------------------------------------+
    | "fit"          | Distort the proportions of the image until   |
    |                | it fits exactly in the view.                 |
    +----------------+----------------------------------------------+
    | "none"         | Do not scale the image.                      |
    +----------------+----------------------------------------------+

    Example::

        from AppKit import *
        from vanilla import *

        class ImageListCellDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0),
                            [
                                {"image": NSImage.imageNamed_("NSActionTemplate")},
                                {"image": NSImage.imageNamed_("NSRefreshTemplate")}
                            ],
                            columnDescriptions=[
                                {"title": "image", "cell": ImageListCell()}
                            ])
                self.w.open()

        ImageListCellDemo()
    """
    from vanillaImageView import _imageAlignmentMap, _imageScaleMap
    cell = NSImageCell.alloc().init()
    align = _imageAlignmentMap[(horizontalAlignment, verticalAlignment)]
    cell.setImageAlignment_(align)
    scale = _imageScaleMap[scale]
    cell.setImageScaling_(scale)
    return cell


def SegmentedButtonListCell(segmentDescriptions):
    """
    **segmentDescriptions** An ordered list of dictionaries describing the segments.

    +------------------------+--------------------------------------------------------------------------------------------------+
    | title (optional)       | The title of the segment.                                                                        |
    +------------------------+--------------------------------------------------------------------------------------------------+
    | imagePath (optional)   | A file path to an image to display in the segment.                                               |
    +------------------------+--------------------------------------------------------------------------------------------------+
    | imageNamed (optional)  | The name of an image already loaded as a *NSImage* by the application to display in the segment. |
    +------------------------+--------------------------------------------------------------------------------------------------+
    | imageObject (optional) | A *NSImage* object to display in the segment.                                                    |
    +------------------------+--------------------------------------------------------------------------------------------------+

    Note: when using this cell in a List, the `binding` in the
    column description must be set to `selectedIndex`.

    Example::

        from vanilla import *

        class SegmentedButtonListCellDemo(object):

            def __init__(self):
                self.w = Window((100, 100))
                self.w.myList = List((0, 0, -0, -0),
                            [{"value": 0}, {"value": 1}],
                            columnDescriptions=[
                                {
                                    "title": "value",
                                    "cell": SegmentedButtonListCell([dict(title="0"), dict(title="1")]),
                                    "binding": "selectedIndex"
                                }
                            ],
                            editCallback=self.editCallback)
                self.w.open()

            def editCallback(self, sender):
                print sender.get()

        SegmentedButtonListCellDemo()
    """
    cell = NSSegmentedCell.alloc().init()
    cell.setControlSize_(NSMiniControlSize)
    cell.setSegmentCount_(len(segmentDescriptions))
    cell.setTrackingMode_(NSSegmentSwitchTrackingSelectOne)
    for segmentIndex, segmentDescription in enumerate(segmentDescriptions):
        title = segmentDescription.get("title", "")
        imagePath = segmentDescription.get("imagePath")
        imageNamed = segmentDescription.get("imageNamed")
        imageObject = segmentDescription.get("imageObject")
        # create the NSImage if needed
        if imagePath is not None:
            image = NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        else:
            image = None
        cell.setLabel_forSegment_(title, segmentIndex)
        if image is not None:
            cell.setImage_forSegment_(image, segmentIndex)
    return cell

