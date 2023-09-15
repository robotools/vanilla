import operator
import weakref
import types
import objc
from objc import python_method
from objc import super
import AppKit
from vanilla.nsSubclasses import getNSSubclass
from vanilla.vanillaBase import VanillaBaseObject, VanillaCallbackWrapper, osVersionCurrent, osVersion10_16
from vanilla.vanillaScrollView import ScrollView
from vanilla.dragAndDrop import DropTargetProtocolMixIn, dropOperationMap, makePasteboardItem
from vanilla.vanillaMenuBuilder import VanillaMenuBuilder


simpleDataTypes = (
    str,
    int,
    float,
    complex,
    bool,
    type(None)
)

class VanillaList2DataSourceAndDelegate(AppKit.NSObject):

    def initWithTableView_(self, tableView):
        self = VanillaList2DataSourceAndDelegate.alloc().init()
        self._items = []
        self._arrangedIndexes = []
        self._groupRowIndexes = []
        self._tableView = tableView
        self._cellClasses = {} # { identifier : (class, kwargs) }
        self._valueToCellConverters = {} # { identifier : function }
        self._cellToValueConverters = {} # { identifier : function }
        self._groupRowCellClass = None
        self._groupRowCellClassKwargs = {}
        self._cellWrappers = {} # { nsView : vanilla wrapper } for view + wrapper reuse purposes
        self._valueGetters = {} # { identifier : options (see below) }
        self._valueSetters = {} # { identifier : options (see below) }
        # {
        #     property : str
        #     method : str
        #     function : func
        # }
        return self

    @python_method
    def setCellClassWithKwargsForColumn(self, cls, kwargs, identifier):
        if "callback" in kwargs:
            kwargs["callback"] = self.cellEditCallback
        self._cellClasses[identifier] = (cls, kwargs)

    @python_method
    def setGroupCellClassWithKwargs(self, cls, kwargs):
        self._groupRowCellClass = cls
        self._groupRowCellClassKwargs = kwargs

    @python_method
    def setGetters(self, getters):
        self._valueGetters = getters

    @python_method
    def setSetters(self, setters):
        self._valueSetters = setters

    @python_method
    def setValueToCellConverters(self, converters):
        self._valueToCellConverters = converters

    @python_method
    def setCellToValueConverters(self, converters):
        self._cellToValueConverters = converters

    @python_method
    def vanillaWrapper(self):
        return self._tableView.vanillaWrapper()

    @python_method
    def items(self):
        return self._items

    @python_method
    def setItems(self, items):
        self._items = items
        self._groupRowIndexes = []
        for index, item in enumerate(items):
            if isinstance(item, List2GroupRow):
                self._groupRowIndexes.append(index)
        self._updateArrangedIndexes()

    @python_method
    def arrangedIndexes(self):
        return self._arrangedIndexes

    @python_method
    def arrangedItems(self):
        items = [
            self._items[index]
            for index in self._arrangedIndexes
        ]
        return items

    @python_method
    def _updateArrangedIndexes(self):
        tableView = self._tableView
        sortDescriptors = tableView.sortDescriptors()
        items = self._items
        indexes = range(len(items))
        for sortDescriptor in reversed(sortDescriptors):
            identifier = sortDescriptor.key()
            ascending = sortDescriptor.ascending()
            reverse = not ascending
            getters = self._valueGetters.get(identifier, {})
            property = getters.get("property")
            method = getters.get("method")
            function = getters.get("function")
            if property is not None:
                key = operator.attrgetter(property)
            elif method is not None:
                key = operator.methodcaller(method)
            elif function is not None:
                key = function
            else:
                key = operator.itemgetter(identifier)

            def valueGetter(index):
                return key(items[index])

            indexes = sorted(indexes, key=valueGetter, reverse=reverse)
        self._arrangedIndexes = list(indexes)
        tableView.reloadData()

    @python_method
    def _getItemForRow(self, index):
        itemIndex = self._arrangedIndexes[index]
        return self._items[itemIndex]

    @python_method
    def getGroupValueForRow(self, index):
        itemIndex = self._arrangedIndexes[index]
        return self._items[itemIndex].value

    # Data Editing Via Cells

    @python_method
    def getItemValueForColumnAndRow(self, identifier, row):
        item = self._getItemForRow(row)
        getters = self._valueGetters.get(identifier, {})
        property = getters.get("property")
        method = getters.get("method")
        function = getters.get("function")
        if property is not None:
            value = getattr(item, property)
        elif method is not None:
            value = getattr(item, method)()
        elif function is not None:
            value = function(item)
        else:
            value = item[identifier]
        if identifier in self._valueToCellConverters:
            value = self._valueToCellConverters[identifier](value)
        return value

    @python_method
    def setItemValueForColumnAndRow(self, value, identifier, row):
        if identifier in self._cellToValueConverters:
            value = self._cellToValueConverters[identifier](value)
        item = self._getItemForRow(row)
        setters = self._valueSetters.get(identifier, {})
        property = setters.get("property")
        method = setters.get("method")
        function = setters.get("function")
        if property is not None:
            return setattr(item, property, value)
        elif method is not None:
            return getattr(item, method)(value)
        elif function is not None:
            return function(item, value)
        elif isinstance(item, dict):
            item[identifier] = value

    # Data Source

    def numberOfRowsInTableView_(self, tableView):
        return len(self._arrangedIndexes)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        isGroupRow = column is None
        if isGroupRow:
            return self.getGroupValueForRow(row)
        identifier = column.identifier()
        value = self.getItemValueForColumnAndRow(identifier, row)
        return value

    def tableView_sortDescriptorsDidChange_(self, tableView, sortDescriptors):
        self._updateArrangedIndexes()

    # Delegate

    def tableView_viewForTableColumn_row_(self, tableView, column, row):
        isGroupRow = column is None
        if isGroupRow:
            view = self._groupRowCellClass(**self._groupRowCellClassKwargs)
            view.set(self.getGroupValueForRow(row))
            return view._nsObject
        identifier = column.identifier()
        value = self.getItemValueForColumnAndRow(identifier, row)
        nsView = tableView.makeViewWithIdentifier_owner_(
            column.identifier(),
            self
        )
        if nsView is not None:
            view = self._cellWrappers[nsView]
        else:
            cellClass, kwargs = self._cellClasses[identifier]
            view = cellClass(**kwargs)
            nsView = view._nsObject
            self._cellWrappers[nsView] = view
            nsView.setIdentifier_(identifier)
        view._representedColumnRow = (identifier, row)
        view.set(value)
        return nsView

    def tableViewSelectionDidChange_(self, notification):
        wrapper = self.vanillaWrapper()
        if wrapper._selectionCallback is not None:
            wrapper._selectionCallback(wrapper)

    def tableView_isGroupRow_(self, tableView, row):
        itemIndex = self._arrangedIndexes[row]
        return itemIndex in self._groupRowIndexes

    def tableView_shouldSelectRow_(self, tableView, row):
        wrapper = self.vanillaWrapper()
        if not wrapper._allowsSelection:
            return False
        if self.tableView_isGroupRow_(tableView, row):
            return False
        return True

    # Editing

    @python_method
    def cellEditCallback(self, sender):
        identifier, row = sender._representedColumnRow
        value = sender.get()
        self.setItemValueForColumnAndRow(value, identifier, row)
        wrapper = self.vanillaWrapper()
        if wrapper._editCallback is not None:
            wrapper._editCallback(wrapper)

    # Drag

    def tableView_pasteboardWriterForRow_(
            self,
            tableView,
            row
        ):
        index = self._arrangedIndexes[row]
        return self.vanillaWrapper()._getPasteboardDataForIndex(index)

    # Drop

    def tableView_validateDrop_proposedRow_proposedDropOperation_(
            self,
            tableView,
            draggingInfo,
            row,
            operation
        ):
        if not self._arrangedIndexes:
            index = None
        elif row == len(self._arrangedIndexes):
            index = row
        else:
            index = self._arrangedIndexes[row]
        return self.vanillaWrapper()._dropCandidateUpdated(draggingInfo, index, operation)

    def tableView_acceptDrop_row_dropOperation_(
            self,
            tableView,
            draggingInfo,
            row,
            operation
        ):
        if not self._arrangedIndexes:
            index = None
        elif row == len(self._arrangedIndexes):
            index = row
        else:
            index = self._arrangedIndexes[row]
        return self.vanillaWrapper()._performDrop(draggingInfo, index, operation)


class VanillaList2TableViewSubclass(AppKit.NSTableView):

    def keyDown_(self, event):
        didSomething = self.vanillaWrapper()._keyDown(event)
        if not didSomething:
            super().keyDown_(event)

    def draggingEntered_(self, draggingInfo):
        super().draggingEntered_(draggingInfo)
        return self.vanillaWrapper()._dropCandidateEntered(draggingInfo)

    @objc.signature(b"Z@:@") # PyObjC bug? <- Found in the FontGoogles source.
    def draggingEnded_(self, draggingInfo):
        self.vanillaWrapper()._dropCandidateEnded(draggingInfo)
        # XXX
        # super().draggingEnded_(draggingInfo)
        # the super doesn't have this.
        # i'm not sure if it because of the
        # PyObjC bug mentioned above or
        # something else.

    def draggingExited_(self, draggingInfo):
        self.vanillaWrapper()._dropCandidateExited(draggingInfo)
        super().draggingExited_(draggingInfo)

    def canDragRowsWithIndexes_atPoint_(self, indexes, point):
        return self.vanillaWrapper()._validateRowsForDrag(indexes)

    # contextual menu support

    def menuForEvent_(self, event):
        wrapper = self.vanillaWrapper()
        return wrapper._menuForEvent(event)


class List2(ScrollView, DropTargetProtocolMixIn):

    """
    A control that shows a list of items. These lists can contain one or more columns.

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"*
    representing the position and size of the list.

    **items** The items to be displayed in the list. This can be a simple list of
    basic object types:

    - str
    - int
    - float
    - complex
    - bool
    - None

    It may also be a list of dictionaries or other Python objects. The values will
    be retrieved and set with the provided value and getter and setter defined in the
    column description. If no getter or setter is given, the column identifier will be
    used to get and set the value in the item as if the item were a dictionary::

        value = item[columnIdentifier]
        item[columnIdentifier] = value

    **columnDescriptions** An ordered list of dictionaries describing the
    columns. This is only necessary for multiple column lists.

    +-------------------------------------+-----------------------------------------------------------+
    | *"identifier"*                      | The unique identifier for this column.                    |
    +-------------------------------------+-----------------------------------------------------------+
    | *"title"* (optional)                | The title to appear in the column header.                 |
    +-------------------------------------+-----------------------------------------------------------+
    | *"cellClass"* (optional)            | A cell class to be displayed in the column.               |
    |                                     | If nothing is given, a text cell is used.                 |
    +-------------------------------------+-----------------------------------------------------------+
    | *"cellClassArguments"* (optional)   | A dictionary of keyword arguments to be used when         |
    |                                     | *cellClass* is instantiated.                              |
    +-------------------------------------+-----------------------------------------------------------+
    | *"valueToCellConverter"* (optional) | A function for converting the value for display in the    |
    |                                     | cell.                                                     |
    +-------------------------------------+-----------------------------------------------------------+
    | *"cellToValueConverter"* (optional) | A function for converting the value displayed in the cell |
    |                                     | value for storage.                                        |
    +-------------------------------------+-----------------------------------------------------------+
    | *"editable"* (optional)             | Enable or disable editing in the column. If               |
    |                                     | nothing is given, it will follow the                      |
    |                                     | editability of the rest of the list.                      |
    +-------------------------------------+-----------------------------------------------------------+
    | *"width"* (optional)                | The width of the column.                                  |
    +-------------------------------------+-----------------------------------------------------------+
    | *"minWidth"* (optional)             | The minimum width of the column. The fallback is `width`. |
    +-------------------------------------+-----------------------------------------------------------+
    | *"maxWidth"* (optional)             | The maximum width of the column. The fallback is `width`. |
    +-------------------------------------+-----------------------------------------------------------+
    | *"sortable"* (optional)             | A boolean representing that this column allows the user   |
    |                                     | to sort the table by clicking the column's header.        |
    |                                     | The fallback is `True`. If a List is set to disallow      |
    |                                     | sorting the column level settings will be ignored.        |
    +-------------------------------------+-----------------------------------------------------------+
    | property (optional)                 | A property name for getting and setting the item value.   |
    +-------------------------------------+-----------------------------------------------------------+
    | getMethod (optional)                | A method name for getting the item value.                 |
    +-------------------------------------+-----------------------------------------------------------+
    | setMethod (optional)                | A method name for setting the item value.                 |
    +-------------------------------------+-----------------------------------------------------------+
    | getFunction (optional)              | A function for getting the item value.                    |
    +-------------------------------------+-----------------------------------------------------------+
    | setFunction (optional)              | A function for getting the item value.                    |
    +-------------------------------------+-----------------------------------------------------------+

    **showColumnTitles** Boolean representing if the column titles should be shown or not.
    Column titles will not be shown in single column lists.

    **selectionCallback** Callback to be called when the selection in the list changes.

    **doubleClickCallback** Callback to be called when an item is double clicked.

    **editCallback** Callback to be called after an item has been edited.

    **menuCallback** Callback to be called when a contextual menu is requested.

    **enableDelete** A boolean representing if items in the list can be deleted via the interface.

    **enableTypingSensitivity** A boolean representing if typing in the list will jump to the
    closest match as the entered keystrokes.

    **allowsSelection** A boolean representing if items in the list can be selected.

    **allowsMultipleSelection** A boolean representing if the list allows more than one item to be selected.

    **allowsEmptySelection** A boolean representing if the list allows zero items to be selected.

    **allowsSorting** A boolean indicating if the list allows user sorting by clicking column headers.

    **allowsColumnReordering** A boolean indicating if the list allows the user to reorder columns.

    **drawVerticalLines** Boolean representing if vertical lines should be drawn in the list.

    **drawHorizontalLines** Boolean representing if horizontal lines should be drawn in the list.

    **drawFocusRing** Boolean representing if the standard focus ring should be drawn when the list is selected.

    **alternatingRowColors** Boolean representing if alternating row colors should be used.

    **autohidesScrollers** Boolean representing if scrollbars should automatically be hidden if possible.

    Group Rows:

    It is possible to have rows that act as headers for a group of rows. To do this,
    add an instance of `List2GroupRow` to your items.::

        class Demo:

            def __init__(self):
                self.w = vanilla.Window((300, 150))
                items = [
                    vanilla.List2GroupRow("Group 1"),
                    "A",
                    "B",
                    "C",
                    vanilla.List2GroupRow("Group 2"),
                    "D",
                    "E",
                    "F"
                ]
                self.w.list = vanilla.List2(
                    "auto",
                    items=items,
                    allowsGroupRows=True,
                    floatsGroupRows=True,
                    allowsSorting=False
                )
                rules = [
                    "H:|[list]|",
                    "V:|[list]|"
                ]
                self.w.addAutoPosSizeRules(rules)
                self.w.open()

    **allowsGroupRows** Boolean representing if the list allows allows group rows.

    **floatsGroupRows** Boolean representing if the list floats the group rows.

    **groupRowCellClass**  A cell class to be displayed in the column.
    If nothing is given, a text cell is used.

    **groupRowCellClassArguments** A dictionary of keyword arguments to be used
    when *groupRowCellClass* is instantiated.

    **autosaveName** A string representing a unique name for the list. If given,
    this name will be used to store the column states in the application preferences.

    **dropSettings** A drop settings dictionary.

    Differences from the standard vanilla drag and drop API:

    Only these callbacks will be used:

    - `dropCandidateCallback`
    - `performDropCallback`
    - `dropCandidateEnteredCallback`
    - `dropCandidateEndedCallback`
    - `dropCandidateExitedCallback`

    `dropCandidateCallback` should return a boolean indicating if the
    drop is acceptable instead of a drop operation.

    The dragging info dictionary will contain an `index` key that specifies
    where in the list the is proposed for insertion. If the list doesn't
    allow dropping on or between rows, index will be `None`.
    """

    nsTableViewClass = VanillaList2TableViewSubclass
    dataSourceAndDelegateClass = VanillaList2DataSourceAndDelegate

    def __init__(self,
            posSize,
            items=[],
            columnDescriptions=[],
            allowsSelection=True,
            allowsMultipleSelection=True,
            allowsEmptySelection=True,
            allowsSorting=True,
            allowColumnReordering=True,
            enableDelete=False,
            enableTypingSensitivity=False,
            showColumnTitles=True,
            drawFocusRing=True,
            drawVerticalLines=False,
            drawHorizontalLines=False,
            alternatingRowColors=True,
            autohidesScrollers=False,
            selectionCallback=None,
            doubleClickCallback=None,
            editCallback=None,
            menuCallback=None,
            allowsGroupRows=False,
            floatsGroupRows=False,
            groupRowCellClass=None,
            groupRowCellClassArguments={},
            autosaveName=None,
            dragSettings=None,
            dropSettings=None
        ):
        if not columnDescriptions:
            showColumnTitles = False
            columnDescriptions = [
                dict(
                    identifier="value",
                    cellClass=EditTextList2Cell
                )
            ]
        self._tableView = getNSSubclass(self.nsTableViewClass)(self)
        self._dataSourceAndDelegate = self.dataSourceAndDelegateClass.alloc().initWithTableView_(self._tableView)
        self._tableView.setDataSource_(self._dataSourceAndDelegate)
        self._tableView.setDelegate_(self._dataSourceAndDelegate)
        # group rows
        if allowsGroupRows:
            assert not allowsSorting, "Group rows are not allowed in sortable lists."
            if groupRowCellClass is None:
                groupRowCellClass = GroupTitleList2Cell
            self._dataSourceAndDelegate.setGroupCellClassWithKwargs(groupRowCellClass, groupRowCellClassArguments)
            self._tableView.setFloatsGroupRows_(floatsGroupRows)
        # callbacks
        self._selectionCallback = selectionCallback
        self._editCallback = editCallback
        if doubleClickCallback is not None:
            self._doubleClickTarget = VanillaCallbackWrapper(doubleClickCallback)
            self._tableView.setTarget_(self._doubleClickTarget)
            self._tableView.setDoubleAction_("action:")
        # contextual menu
        self._menuCallback = menuCallback
        # behavior attributes
        self._allowsSelection = allowsSelection
        self._tableView.setAllowsEmptySelection_(allowsEmptySelection)
        self._tableView.setAllowsMultipleSelection_(allowsMultipleSelection)
        self._tableView.setAllowsColumnReordering_(allowColumnReordering)
        self._allowsSorting = allowsSorting
        self._enableDelete = enableDelete
        self._tableView.setAllowsTypeSelect_(enableTypingSensitivity)
        # visual attributes
        if not showColumnTitles:
            self._tableView.setHeaderView_(None)
            self._tableView.setCornerView_(None)
        self._tableView.setUsesAlternatingRowBackgroundColors_(alternatingRowColors)
        if not drawFocusRing:
            self._tableView.setFocusRingType_(AppKit.NSFocusRingTypeNone)
        if drawVerticalLines or drawHorizontalLines:
            if drawVerticalLines and drawHorizontalLines:
                lineType = AppKit.NSTableViewSolidVerticalGridLineMask | AppKit.NSTableViewSolidHorizontalGridLineMask
            elif drawVerticalLines:
                lineType = AppKit.NSTableViewSolidVerticalGridLineMask
            else:
                lineType = AppKit.NSTableViewSolidHorizontalGridLineMask
            self._tableView.setGridStyleMask_(lineType)
        if osVersionCurrent >= osVersion10_16:
            self._tableView.setStyle_(AppKit.NSTableViewStyleInset)
        # auto save
        if autosaveName is not None:
            self._tableView.setAutosaveName_(autosaveName)
            self._tableView.setAutosaveTableColumns_(True)
        # columns
        self._buildColumns(columnDescriptions)
        # self._tableView.setRowSizeStyle_(AppKit.NSTableViewRowSizeStyleDefault)
        super().__init__(
            posSize,
            nsView=self._tableView,
            autohidesScrollers=autohidesScrollers
        )
        # drag and drop
        if dragSettings is not None:
            self._dragCandidateCallback = dragSettings.get("dragCandidateCallback")
            self._dragStartedCallback = dragSettings.get("dragStartedCallback")
            self._makeDragDataCallback = dragSettings.get("makeDragDataCallback")
            self._dragEndedCallback = dragSettings.get("dragEndedCallback")
        if dropSettings is not None:
            self.setDropSettings(dropSettings)
        # populate
        self._itemsWereDict = True
        self.set(items)

    def _breakCycles(self):
        self._menuItemCallbackWrappers = None
        super()._breakCycles()
        self._selectionCallback = None
        self._editCallback = None

    def _getDropView(self):
        return self._tableView

    def _buildColumns(self, columnDescriptions):
        getters = {}
        setters = {}
        cellToValueConverters = {}
        valueToCellConverters = {}
        rowHeights = []
        if osVersionCurrent >= osVersion10_16:
            rowHeights.append(24)
        else:
            rowHeights.append(17)
        for columnDescription in columnDescriptions:
            identifier = columnDescription["identifier"]
            title = columnDescription.get("title", "")
            width = columnDescription.get("width")
            minWidth = columnDescription.get("minWidth", width)
            maxWidth = columnDescription.get("maxWidth", width)
            sortable = columnDescription.get("sortable")
            cellClass = columnDescription.get("cellClass", EditTextList2Cell)
            cellKwargs = columnDescription.get("cellClassArguments", {})
            editable = columnDescription.get("editable", False)
            property = columnDescription.get("property")
            getMethod = columnDescription.get("getMethod")
            setMethod = columnDescription.get("setMethod")
            getFunction = columnDescription.get("getFunction")
            setFunction = columnDescription.get("setFunction")
            cellToValueConverter = columnDescription.get("cellToValueConverter")
            valueToCellConverter = columnDescription.get("valueToCellConverter")
            getters[identifier] = dict(
                property=property,
                method=getMethod,
                function=getFunction
            )
            setters[identifier] = dict(
                property=property,
                method=setMethod,
                function=setFunction
            )
            if cellToValueConverter is not None:
                cellToValueConverters[identifier] = cellToValueConverter
            if valueToCellConverter is not None:
                valueToCellConverters[identifier] = valueToCellConverter
            cellKwargs["editable"] = editable
            if editable:
                cellKwargs["callback"] = True
            self._dataSourceAndDelegate.setCellClassWithKwargsForColumn(
                cellClass, cellKwargs, identifier
            )
            if width is not None:
                if width == minWidth and width == maxWidth:
                    resizingMask = AppKit.NSTableColumnNoResizing
                else:
                    resizingMask = AppKit.NSTableColumnUserResizingMask | AppKit.NSTableColumnAutoresizingMask
            else:
                resizingMask = AppKit.NSTableColumnUserResizingMask | AppKit.NSTableColumnAutoresizingMask
            column = AppKit.NSTableColumn.alloc().initWithIdentifier_(identifier)
            column.setTitle_(title)
            column.setResizingMask_(resizingMask)
            if width is not None:
                column.setWidth_(width)
                column.setMinWidth_(minWidth)
                column.setMaxWidth_(maxWidth)
            if self._allowsSorting and sortable:
                sortDescriptor = AppKit.NSSortDescriptor.sortDescriptorWithKey_ascending_selector_(
                    identifier,
                    True,
                    "compare:"
                )
                column.setSortDescriptorPrototype_(sortDescriptor)
            self._tableView.addTableColumn_(column)
            # measure the cell to get the row height
            cell = cellClass(**cellKwargs)
            height = cell._nsObject.fittingSize().height
            del cell
            rowHeights.append(height)
        self._dataSourceAndDelegate.setGetters(getters)
        self._dataSourceAndDelegate.setSetters(setters)
        self._dataSourceAndDelegate.setCellToValueConverters(cellToValueConverters)
        self._dataSourceAndDelegate.setValueToCellConverters(valueToCellConverters)
        self._tableView.setRowHeight_(max(rowHeights))

    def _wrapItem(self, item):
        if isinstance(item, simpleDataTypes):
            self._itemsWereDict = False
            item = dict(value=item)
        return item

    def getNSTableView(self):
        """
        Return the `NSTableView`_ that this object wraps.

        .. _NSTableView: https://developer.apple.com/documentation/appkit/nstableview?language=objc
        """
        return self._tableView

    def getNSScrollView(self):
        """
        Return the `NSScrollView`_ that this object wraps.

        .. _NSScrollView: https://developer.apple.com/documentation/appkit/nsscrollview?language=objc
        """
        return self._nsObject

    def enable(self, onOff):
        """
        Enable or disable the object. **onOff** should be a boolean.
        """
        self._tableView.setEnabled_(onOff)

    # Data

    def set(self, items):
        """
        Set the items in the list.

        **items** should follow the same format as described in the constructor.
        """
        items = [self._wrapItem(item) for item in items]
        self._dataSourceAndDelegate.setItems(items)

    def get(self):
        """
        Get the list of items in the list.
        """
        items = list(self._dataSourceAndDelegate.items())
        if not self._itemsWereDict:
            items = [item["value"] for item in items]
        return items

    def getArrangedIndexes(self):
        """
        Get the indexes of the items as they appear
        to the user in the list.
        """
        return self._dataSourceAndDelegate.arrangedIndexes()

    def getArrangedItems(self):
        """
        Get the items as they appear to the user in the list.
        """
        return self._dataSourceAndDelegate.arrangedItems()

    def reloadData(self, indexes=None):
        """
        Reload the data on display. This is needed when
        the items have changed values and the presentation
        of the items in the list needs to be updated.

        **indexes** may be provided to indicate that only
        specific items need to be reloaded.
        """
        tableView = self._tableView
        if indexes is None:
            tableView.reloadData()
        else:
            rowIndexes = makeIndexSet(indexes)
            columnIndexes = range(len(tableView.tableColumns()))
            columnIndexes = makeIndexSet(columnIndexes)
            tableView.reloadDataForRowIndexes_columnIndexes_(
                rowIndexes,
                columnIndexes
            )

    # Selection

    def getSelectedItems(self):
        """
        Get a list of selected items in the list.
        """
        selectedIndexes = self._tableView.selectedRowIndexes()
        items = self.get()
        indexes = self.getArrangedIndexes()
        items = [
            items[i]
            for i in indexes
            if i in selectedIndexes
        ]
        return items

    def setSelectedItems(self, items):
        """
        Set the selected items in the list.

        .. note::
           `setSelectedIndexes` is the recommended method
           for setting selection. `setSelectedItems` is
           a convenience method that relies on iteration
           and comparing object ids to find the item indexes,
           which are then sent to `setSelectedIndexes`. If
           the list contains a large number of items this
           iteration can create a performance problem.
        """
        allItems = self.get()
        indexMapping = {
            id(item) : index
            for index, item in enumerate(allItems)
        }
        selectionIndexes = [
            indexMapping[id(item)]
            for item in items
        ]
        self.setSelectedIndexes(selectionIndexes)

    def getSelectedIndexes(self):
        """
        Get a list of indexes of selected items in the list.
        """
        rowIndexes = self._tableView.selectedRowIndexes()
        arrangedIndexes = self.getArrangedIndexes()
        itemIndexes = [
            arrangedIndexes[i]
            for i in rowIndexes
        ]
        return itemIndexes

    def setSelectedIndexes(self, indexes):
        """
        Set the selected indexes in the list.

        **indexes** should be a list of indexes.
        """
        itemIndexToRowIndexes = {
            itemIndex : rowIndex
            for rowIndex, itemIndex
            in enumerate(self.getArrangedIndexes())
        }
        rowIndexes = [
            itemIndexToRowIndexes[itemIndex]
            for itemIndex in indexes
        ]
        rowIndexes = makeIndexSet(rowIndexes)
        self._tableView.selectRowIndexes_byExtendingSelection_(rowIndexes, False)

    def scrollToSelection(self):
        """
        Scroll the selected rows to visible.
        """
        selection = self.getSelectedIndexes()
        if not selection:
            return
        index = min(selection)
        self.scrollToIndex(index)

    def scrollToIndex(self, row):
        """
        Scroll the row to visible.
        """
        self._tableView.scrollRowToVisible_(row)

    def removeSelection(self):
        """
        Remove selected items.
        """
        selection = self.getSelectedIndexes()
        if not selection:
            return
        items = self.get()
        for index in reversed(sorted(selection)):
            del items[index]
        self.set(items)

    # Drag

    _dragCandidateCallback = None
    _dragStartedCallback = None
    _makeDragDataCallback = None
    _dragEndedCallback = None

    def _validateRowsForDrag(self, indexes):
        if self._dragCandidateCallback is None:
            if self._makeDragDataCallback is None:
                return False
            return True
        return self._dragCandidateCallback(indexes)

    def _getPasteboardDataForIndex(self, index):
        if self._makeDragDataCallback is None:
            return None
        typesAndValues = self._makeDragDataCallback(index)
        if not typesAndValues:
            return None
        return makePasteboardItem(typesAndValues)

    # key down

    def _keyDown(self, event):
        # this method is called by the NSTableView subclass after a key down
        # has occurred. the subclass expects that a boolean will be returned
        # that indicates if this method has done something (delete an item or
        # select an item). if False is returned, the delegate calls the super
        # method to insure standard key down behavior.
        #
        # get the characters
        characters = event.characters()
        # get the field editor
        #
        deleteCharacters = [
            AppKit.NSBackspaceCharacter,
            AppKit.NSDeleteFunctionKey,
            AppKit.NSDeleteCharacter,
            chr(0x007F),
        ]
        if characters in deleteCharacters:
            if self._enableDelete:
                self.removeSelection()
                return True

        return False


    # contextual menu

    def _menuForEvent(self, event):
        # this method is called by the NSTableView subclass to request a contextual menu
        # if there is a menuCallack convert a the incomming items to an nsmenu
        if self._menuCallback is not None:
            items = self._menuCallback(self)
            # if the list is empty or None, dont do anything
            if items:
                menu = AppKit.NSMenu.alloc().init()
                VanillaMenuBuilder(self, items, menu)
                return menu
        # if a menu is been set by setMenu
        if self._menu is not None:
            return self._menu
        return None

    _menu = None

    def setMenu(self, items):
        self._menu = menu = AppKit.NSMenu.alloc().init()
        VanillaMenuBuilder(self, items, menu)

    # Drop

    _allowDropOnRow = None
    _allowDropBetweenRows = None

    def setDropSettings(self, settings):
        self._allowDropOnRow = settings.get("allowDropOnRow", False)
        self._allowDropBetweenRows = settings.get("allowDropBetweenRows", True)
        super().setDropSettings(settings)

    def _dropCandidateUpdated(self, draggingInfo, index, operation):
        if self._dropCandidateCallback is None:
            return AppKit.NSDragOperationNone
        info = self._unpackDropCandidateInfo(draggingInfo)
        info["index"] = index
        if not self._allowDropOnRow and not self._allowDropBetweenRows:
            index = None
        elif not self._allowDropOnRow and operation == AppKit.NSTableViewDropOn:
            return AppKit.NSDragOperationNone
        elif not self._allowDropBetweenRows and operation == AppKit.NSTableViewDropAbove:
            return AppKit.NSDragOperationNone
        if not len(self.get()):
            index = None
        operation = self._dropCandidateCallback(info)
        operation = dropOperationMap.get(operation, operation)
        # highlight the whole table instead of a single spot
        if index is None:
            self._tableView.setDropRow_dropOperation_(-1, operation)
        return operation

    def _performDrop(self, draggingInfo, index, operation):
        if not self._allowDropOnRow and not self._allowDropBetweenRows:
            index = None
        info = self._unpackDropCandidateInfo(draggingInfo)
        info["index"] = index
        return self._performDropCallback(info)

# -----
# Tools
# -----

class List2GroupRow:

    def __init__(self, value=None):
        self.value = value


def makeIndexSet(indexes):
    indexSet = AppKit.NSMutableIndexSet.indexSet()
    for i in indexes:
        indexSet.addIndex_(i)
    return indexSet

# -----
# Cells
# -----

from vanilla.vanillaGroup import Group
from vanilla.vanillaEditText import EditText

truncationMap = dict(
    clipping=AppKit.NSLineBreakByClipping,
    head=AppKit.NSLineBreakByTruncatingHead,
    tail=AppKit.NSLineBreakByTruncatingTail,
    middle=AppKit.NSLineBreakByTruncatingMiddle
)

class EditTextList2Cell(Group):

    """
    An object that displays text in a List2 column.

    **verticalAlignment** The vertical alignment of the text
    within the row. Options:

    - `"top"`
    - `"center"`
    - `"bottom"`

    **truncationMode** How text should be truncated. Options:

    - `"clipping"`
    - `"head"`
    - `"tail"`
    - `"middle"`
    - A specific `NSLineBreakMode`.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    # Implementation Note:
    # Using NSTextField directly as the row view doesn't
    # allow for vertically positioning the text anywhere
    # but to the top. In macOS 11 this leads to text
    # being out of alignment with other cell types like
    # checkboxes and sliders. I found numerous complaints
    # about this on Stack Overflow so I'm not alone in
    # noticing this. This is apparently solved automatically
    # when using IB, but a pain when building things
    # programatically. Additionally, I chose to use NSView
    # as the base of this instead of NSTableCellView because
    # NSTableCellView doesn't have a textField by default
    # so it has to be built and we may as well skip the
    # expense of NSTableCellView and go straight to NSView.
    # Sigh.

    def __init__(self,
            verticalAlignment="center",
            editable=False,
            truncationMode="tail",
            callback=None
        ):
        self._externalCallback = callback
        super().__init__("auto")
        self.editText = EditText(
            "auto",
            readOnly=not editable,
            callback=self._internalCallback
        )
        container = self._nsObject
        textField = self.editText.getNSTextField()
        if verticalAlignment == "top":
            yRule = "V:|[editText]"
        elif verticalAlignment == "bottom":
            yRule = "V:[editText]|"
        else:
            yRule = dict(
                view1=self.editText,
                attribute1="centerY",
                view2=self,
                attribute2="centerY"
            )
        rules = [
            "H:|[editText]|",
            yRule
        ]
        if verticalAlignment != "center":
            heightRule = dict(
                view1=self.editText,
                attribute1="height",
                view2=self,
                attribute2="height"
            )
            rules.append(heightRule)
        self.addAutoPosSizeRules(rules)
        textField.setDrawsBackground_(False)
        textField.setBezeled_(False)
        lineBreakMode = truncationMap.get(truncationMode, truncationMode)
        textField.setLineBreakMode_(lineBreakMode)

    def getNSTextField(self):
        return self.editText.getNSTextField()

    def _internalCallback(self, sender):
        if self._externalCallback is not None:
            self._externalCallback(self)

    def set(self, value):
        self.editText.set(value)

    def get(self):
        return self.editText.get()


class GroupTitleList2Cell(EditTextList2Cell):

    """
    An object that displays highlighted text for group rows
    in a List2 column.

    **font** The font.

    **textColor** The text color.

    **backgroundColor** The background color.

    **verticalAlignment** The vertical alignment of the text
    within the row. Options:

    - `"top"`
    - `"center"`
    - `"bottom"`

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            font=None,
            textColor=None,
            backgroundColor=None,
            verticalAlignment="center",
            editable=False,
            callback=None
        ):
        super().__init__(
            editable=False,
            callback=callback
        )
        textField = self.getNSTextField()
        if backgroundColor is not None:
            textField.setDrawsBackground_(True)
            textField.setBackgroundColor_(backgroundColor)
        if textColor is not None:
            textField.setTextColor_(textColor)
        if font is not None:
            textField.setFont_(font)



from vanilla.vanillaSlider import Slider

class SliderList2Cell(Slider):

    """
    An object that displays a slider in a List2 column.

    **minValue** The minimum value for the slider.

    **maxValue** The maximum value for the slider.

    **tickMarkCount** The number of tick marks to be displayed on the slider.
    If *None* is given, no tick marks will be displayed.

    **stopOnTickMarks** Boolean representing if the slider knob should only
    stop on the tick marks.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            minValue=0,
            maxValue=100,
            value=50,
            tickMarkCount=0,
            stopOnTickMarks=False,
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            minValue=minValue,
            maxValue=maxValue,
            value=value,
            tickMarkCount=tickMarkCount,
            stopOnTickMarks=stopOnTickMarks,
            sizeStyle="small",
            callback=callback
        )
        self.enable(editable)


from vanilla.vanillaCheckBox import CheckBox

class CheckBoxList2Cell(CheckBox):

    """
    An object that displays a check box in a List2 column.

    **title** The title to be set in *all* items in the List column.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            title=None,
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            title=title,
            sizeStyle="small",
            callback=callback
        )
        self.enable(editable)


from vanilla.vanillaPopUpButton import PopUpButton

class PopUpButtonList2Cell(PopUpButton):

    """
    An object that displays a pop up list in a List2 column.

    **items** The items that should appear in the pop up list.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            items=[],
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            items=items,
            sizeStyle="small",
            callback=callback
        )
        self.enable(editable)


from vanilla.vanillaImageView import ImageView

class ImageList2Cell(ImageView):

    """
    An object that displays an image in a List2 column.

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
    | "proportional" | Proportionally scale the image to fit in the |
    |                | view if it is larger than the view.          |
    +----------------+----------------------------------------------+
    | "fit"          | Distort the proportions of the image until   |
    |                | it fits exactly in the view.                 |
    +----------------+----------------------------------------------+
    | "none"         | Do not scale the image.                      |
    +----------------+----------------------------------------------+

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            horizontalAlignment="center",
            verticalAlignment="center",
            scale="proportional",
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            horizontalAlignment=horizontalAlignment,
            verticalAlignment=verticalAlignment,
            scale=scale
        )

    def set(self, image):
        self.setImage(imageObject=image)

    def get(self):
        return self.getNSImageView().image()


from vanilla.vanillaSegmentedButton import SegmentedButton

class SegmentedButtonList2Cell(SegmentedButton):

    """
    An object that displays a segmented button in a List2 column.

    **segmentDescriptions** An ordered list of dictionaries describing the segments.

    **minValue** The minimum value for the slider.

    **maxValue** The maximum value for the slider.

    +------------------------+-----------------------------------------------------+
    | imagePath (optional)   | A file path to an image to display in the segment.  |
    +------------------------+-----------------------------------------------------+
    | imageNamed (optional)  | The name of an image already loaded as a `NSImage`_ |
    |                        | by the application to display in the segment.       |
    +------------------------+-----------------------------------------------------+
    | imageObject (optional) | A `NSImage`_ object to display in the segment.      |
    +------------------------+-----------------------------------------------------+

    .. _NSImage: https://developer.apple.com/documentation/appkit/nsimage?language=objc

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            segmentDescriptions=[],
            selectionStyle="one",
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            segmentDescriptions=segmentDescriptions,
            selectionStyle=selectionStyle,
            sizeStyle="small",
            callback=callback
        )
        self.enable(editable)


from vanilla.vanillaColorWell import ColorWell

class ColorWellList2Cell(ColorWell):

    """
    An object that displays a color well in a List2 column.

    **title** The title to be set in *all* items in the List column.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            editable=False,
            callback=None,
            colorWellStyle=None
        ):
        if colorWellStyle is None:
            colorWellStyle = "minimal"
        super().__init__(
            "auto",
            callback=callback,
            colorWellStyle=colorWellStyle
        )
        colorWell = self.getNSColorWell()
        self.enable(editable)


from vanilla.vanillaLevelIndicator import LevelIndicator

class LevelIndicatorList2Cell(LevelIndicator):

    """
    An object that displays a level indicator in a List2 column.
    Refer to the LevelIndicator documentation for options.

    .. note::
       This class should only be used in the *columnDescriptions*
       *cellClass* argument during the construction of a List.
       This is never constructed directly.
    """

    def __init__(self,
            style="discrete",
            value=5,
            minValue=0,
            maxValue=10,
            warningValue=None,
            criticalValue=None,
            tickMarkPosition=None,
            minorTickMarkCount=None,
            majorTickMarkCount=None,
            imagePath=None,
            imageNamed=None,
            imageObject=None,
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            style=style,
            value=value,
            minValue=minValue,
            maxValue=maxValue,
            warningValue=warningValue,
            criticalValue=criticalValue,
            tickMarkPosition=tickMarkPosition,
            minorTickMarkCount=minorTickMarkCount,
            majorTickMarkCount=majorTickMarkCount,
            # sizeStyle="small",
            callback=callback
        )
        self.enable(editable)
        cell = self._nsObject.cell()
        if imagePath is not None:
            image = AppKit.NSImage.alloc().initWithContentsOfFile_(imagePath)
        elif imageNamed is not None:
            image = AppKit.NSImage.imageNamed_(imageNamed)
        elif imageObject is not None:
            image = imageObject
        if imageObject is not None:
            cell.setImage_(image)
