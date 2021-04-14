import operator
import weakref
import types
from objc import python_method
import AppKit
import vanilla
from vanilla.nsSubclasses import getNSSubclass
from vanilla.vanillaBase import VanillaCallbackWrapper, osVersionCurrent, osVersion10_16

import objc
objc.setVerbose(True)


"""
items must be a list of:
- strings: we make a dict for each
- dicts: d[x] = y and y = d[x] are used for get/set
- objects: need to define get/set on a value by value basis

column descriptions:

- identifier
- title (optional)
- width (optional)
- minWidth (optional)
- maxWidth (optional)
- cellClass (optional, text cell if not given)
- cellClassArguments (optional)
- editable (optional)
- property (optional)
- getMethod (optional)
- setMethod (optional)
- getFunction (optional)
- setFunction (optional)
"""

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
        self._presentedItems = []
        self._tableView = tableView
        self._cellClasses = {} # { identifier : class }
        self._cellWrappers = {} # { nsView : vanilla wrapper } for view + wrapper reuse purposes
        self._valueGetters = {} # { identifier : options (see below) }
        self._valueSetters = {} # { identifier : options (see below) }
        # {
        #     property : str
        #     method : str
        #     function : func
        # }
        return self

    def setCellClass_withKwargs_forColumn_(self, cls, kwargs, identifier):
        if "callback" in kwargs:
            kwargs["callback"] = self.cellEditCallback
        self._cellClasses[identifier] = (cls, kwargs)

    def setGetters_setters_(self, getters, setters):
        self._valueGetters = getters
        self._valueSetters = setters

    def vanillaWrapper(self):
        return self._tableView.vanillaWrapper()

    def items(self):
        return self._items

    def setItems_(self, items):
        self._items = items
        self._updatePresentedItems()

    def _updatePresentedItems(self):
        tableView = self._tableView
        sortDescriptors = tableView.sortDescriptors()
        items = self._items
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
            items = sorted(
                items,
                key=key,
                reverse=reverse
            )
        self._presentedItems = list(items)
        tableView.reloadData()

    # Data Editing Via Cells

    def getObjectValueForColumn_row_(self, identifier, row):
        item = self._presentedItems[row]
        getters = self._valueGetters.get(identifier, {})
        property = getters.get("property")
        method = getters.get("method")
        function = getters.get("function")
        if property is not None:
            return getattr(item, property)
        elif method is not None:
            return getattr(item, method)()
        elif function is not None:
            return function(item)
        return item[identifier]

    def setObjectValue_forColumn_row_(self, value, identifier, row):
        item = self._presentedItems[row]
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

    # Selection

    def selectedItems(self):
        indexes = self._tableView.selectedRowIndexes()
        items = [self._presentedItems[i] for i in indexes]
        return items

    def setSelectedItems_(self, items):
        indexes = [
            self._presentedItems.index(item)
            for item in items
            if item in self._presentedItems
        ]
        indexes = makeIndexSet(indexes)
        self._tableView.setSelectedRows_(indexes)

    # Data Source

    def numberOfRowsInTableView_(self, tableView):
        return len(self._presentedItems)

    def tableView_objectValueForTableColumn_row_(self, tableView, column, row):
        identifier = column.identifier()
        return self.getObjectValueForColumn_row_(identifier, row)

    def tableView_sortDescriptorsDidChange_(self, tableView, sortDescriptors):
        self._updatePresentedItems()

    # Delegate

    def tableView_viewForTableColumn_row_(self, tableView, column, row):
        identifier = column.identifier()
        value = self.getObjectValueForColumn_row_(identifier, row)
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

    # Editing

    @python_method
    def cellEditCallback(self, sender):
        identifier, row = sender._representedColumnRow
        value = sender.get()
        self.setObjectValue_forColumn_row_(value, identifier, row)
        wrapper = self.vanillaWrapper()
        if wrapper._editCallback is not None:
            wrapper._editCallback(wrapper)


class VanillaList2TableViewSubclass(AppKit.NSTableView): pass


class List2(vanilla.ScrollView):

    nsTableViewClass = VanillaList2TableViewSubclass
    dataSourceAndDelegateClass = VanillaList2DataSourceAndDelegate

    def __init__(self,
            posSize,
            items=[],
            columnDescriptions=[],
            allowsMultipleSelection=True,
            allowsEmptySelection=True,
            showColumnTitles=True,
            drawFocusRing=True,
            drawVerticalLines=False,
            drawHorizontalLines=False,
            autohidesScrollers=False,
            selectionCallback=None,
            doubleClickCallback=None,
            editCallback=None,
        ):
        if not columnDescriptions:
            showColumnTitles = False
            columnDescriptions = [
                dict(
                    identifier="value",
                    cellClass=TextFieldTableCell
                )
            ]
        self._tableView = getNSSubclass(self.nsTableViewClass)(self)
        self._tableViewDataSourceAndDelegate = self.dataSourceAndDelegateClass.alloc().initWithTableView_(self._tableView)
        self._tableView.setDataSource_(self._tableViewDataSourceAndDelegate)
        self._tableView.setDelegate_(self._tableViewDataSourceAndDelegate)
        # callbacks
        self._selectionCallback = selectionCallback
        self._editCallback = editCallback
        if doubleClickCallback is not None:
            self._doubleClickTarget = VanillaCallbackWrapper(doubleClickCallback)
            self._tableView.setTarget_(self._doubleClickTarget)
            self._tableView.setDoubleAction_("action:")
        # behavior attributes
        self._tableView.setAllowsEmptySelection_(allowsEmptySelection)
        self._tableView.setAllowsMultipleSelection_(allowsMultipleSelection)
        # visual attributes
        if not showColumnTitles:
            self._tableView.setHeaderView_(None)
            self._tableView.setCornerView_(None)
        self._tableView.setUsesAlternatingRowBackgroundColors_(True)
        if not drawFocusRing:
            self._tableView.setFocusRingType_(NSFocusRingTypeNone)
        if drawVerticalLines or drawHorizontalLines:
            if drawVerticalLines and drawHorizontalLines:
                lineType = NSTableViewSolidVerticalGridLineMask | NSTableViewSolidHorizontalGridLineMask
            elif drawVerticalLines:
                lineType = NSTableViewSolidVerticalGridLineMask
            else:
                lineType = NSTableViewSolidHorizontalGridLineMask
            self._tableView.setGridStyleMask_(lineType)
        if osVersionCurrent >= osVersion10_16:
            self._tableView.setStyle_(AppKit.NSTableViewStyleInset)
        # columns
        self._buildColumns(columnDescriptions)
        # self._tableView.setRowSizeStyle_(AppKit.NSTableViewRowSizeStyleDefault)
        super().__init__(
            posSize,
            nsView=self._tableView,
            autohidesScrollers=autohidesScrollers
        )
        # populate
        self._itemsWereDict = True
        self.set(items)

    def _breakCycles(self):
        super()._breakCycles()
        self._selectionCallback = None
        self._editCallback = None

    def _buildColumns(self, columnDescriptions):
        getters = {}
        setters = {}
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
            cellClass = columnDescription.get("cellClass", TextFieldTableCell)
            cellKwargs = columnDescription.get("cellClassArguments", {})
            editable = columnDescription.get("editable", False)
            property = columnDescription.get("property")
            getMethod = columnDescription.get("getMethod")
            setMethod = columnDescription.get("setMethod")
            getFunction = columnDescription.get("getFunction")
            setFunction = columnDescription.get("setFunction")
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
            if editable:
                cellKwargs["callback"] = True
            self._tableViewDataSourceAndDelegate.setCellClass_withKwargs_forColumn_(
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
            if sortable:
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
        self._tableViewDataSourceAndDelegate.setGetters_setters_(getters, setters)
        self._tableView.setRowHeight_(max(rowHeights))

    def _wrapItem(self, item):
        if isinstance(item, simpleDataTypes):
            self._itemsWereDict = False
            item = dict(value=item)
        return item

    def getNSScrollView(self):
        """
        Return the `NSScrollView`_ that this object wraps.
    
        .. _NSScrollView: https://developer.apple.com/documentation/appkit/nsscrollview?language=objc
        """
        return self._nsObject
    
    def getNSTableView(self):
        """
        Return the `NSTableView`_ that this object wraps.
    
        .. _NSTableView: https://developer.apple.com/documentation/appkit/nstableview?language=objc
        """
        return self._tableView

    # Data

    def set(self, items):
        """
        Set the items in the list.

        **items** should follow the same format as described in the constructor.
        """
        items = [self._wrapItem(item) for item in items]
        self._tableViewDataSourceAndDelegate.setItems_(items)

    def get(self):
        """
        Get the list of items in the list.
        """
        items = list(self._tableViewDataSourceAndDelegate.items())
        if not self._itemsWereDict:
            items = [item["value"] for item in items]
        return items

    def reloadData(self, indexes=None):
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

    def getSelection(self):
        pass

    def setSelection(self, indexes):
        pass

    def getSelectedItems(self):
        pass

    def setSelectedItems(self, items):
        pass


# -----
# Tools
# -----

def makeIndexSet(indexes):
    indexSet = AppKit.NSMutableIndexSet.indexSet()
    for i in indexes:
        indexSet.addIndex_(i)
    return indexSet

# -----
# Cells
# -----

class TextFieldTableCell(vanilla.EditText):

    def __init__(self,
            callback=None
        ):
        super().__init__(
            "auto",
            callback=callback
        )
        textField = self.getNSTextField()
        textField.setDrawsBackground_(False)
        textField.setBezeled_(False)


class SliderTableCell(vanilla.Slider):

    def __init__(self,
            minValue=0,
            maxValue=100,
            value=50,
            tickMarkCount=0,
            stopOnTickMarks=False,
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


# ----
# Test
# ----

class CustomTableCell(vanilla.Box):

    def __init__(self):
        super().__init__(
            "auto",
            cornerRadius=10
        )
        self.button1 = vanilla.Button(
            "auto",
            "Hello"
        )
        self.button2 = vanilla.CheckBox(
            "auto",
            "World"
        )
        self.button3 = vanilla.Button(
            "auto",
            "!?!?!?!?!?!"
        )
        rules = [
            "H:|-border-[button1]-border-|",
            "H:|-border-[button2]-border-|",
            "H:|-border-[button3]-border-|",
            "V:|-border-[button1]-border-[button2]-border-[button3]-border-|",
        ]
        metrics = dict(
            border=10
        )
        self.addAutoPosSizeRules(rules, metrics)

    def get(self):
        return self.getNSBox().backgroundColor()

    def set(self, value):
        self.getNSBox().setBackgroundColor_(value)


class TestObject(dict):

    def __init__(self, propertyValue="", color=AppKit.NSColor.blackColor(), **kwargs):
        super().__init__()
        self.update(kwargs)
        self.propertyValue = propertyValue
        self._color = color

    def getColor(self):
        return self._color

    def setColor(self, color):
        self._color = color

    def getValues(self):
        values = list(self.items())
        values.append(("propertyValue", self.propertyValue))
        return values


class Test:

    def __init__(self):
        self.w = vanilla.Window((500, 500))
        self.items = []
        for i in range(1):
            self.items += [
                TestObject(
                    stringValue="AAA",
                    numberValue=1,
                    propertyValue="one",
                    color=AppKit.NSColor.redColor()
                ),
                TestObject(
                    stringValue="BBB",
                    numberValue=2,
                    propertyValue="two",
                    color=AppKit.NSColor.greenColor()
                ),
                TestObject(
                    stringValue="CCC",
                    numberValue=3,
                    propertyValue="three",
                    color=AppKit.NSColor.blueColor()
                ),
            ]
        columnDescriptions = [
            dict(
                title="String",
                identifier="stringValue",
                cellClass=TextFieldTableCell,
                editable=False,
                sortable=True
            ),
            dict(
                title="Number",
                identifier="numberValue",
                cellClass=SliderTableCell,
                cellClassArguments=dict(
                    minValue=0,
                    maxValue=5,
                    tickMarkCount=10
                ),
                editable=True,
                sortable=True
            ),
            dict(
                title="Property",
                identifier="propertyValue",
                property="propertyValue",
                editable=True,
                sortable=True
            ),
            dict(
                title="Method",
                identifier="method",
                cellClass=CustomTableCell,
                getMethod="getColor",
                editable=False
            ),
        ]
        # self.items = list(range(5))
        # columnDescriptions = None
        self.w.l = List2(
            (10, 10, -10, -40),
            self.items,
            columnDescriptions=columnDescriptions,
            editCallback=self.editCallback,
            selectionCallback=self.selectionCallback,
            doubleClickCallback=self.doubleClickCallback
        )
        self.w.getButton = vanilla.Button(
            (10, -30, 100, 20),
            "get values",
            callback=self.getButtonCallback
        )
        self.w.setButton = vanilla.Button(
            (120, -30, 100, 20),
            "set values",
            callback=self.setButtonCallback
        )
        self.w.open()

    def editCallback(self, sender):
        print("editCallback")

    def selectionCallback(self, sender):
        print("selectionCallback")

    def doubleClickCallback(self, sender):
        print("doubleClickCallback")

    def getButtonCallback(self, sender):
        print(self.w.l.get())
        # import pprint
        # pprint.pprint([i.getValues() for i in self.items])

    def setButtonCallback(self, sender):
        for i in self.items:
            i["stringValue"] = "XXX"
            i["numberValue"] = 2.5
            i.propertyValue = "123"
        self.w.l.reloadData()
        # items = list(range(100, 150))
        # self.w.l.set(items)

from vanilla.test.testTools import executeVanillaTest
executeVanillaTest(Test)

