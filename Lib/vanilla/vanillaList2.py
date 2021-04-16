import operator
import weakref
import types
from objc import python_method
import AppKit
import vanilla
from vanilla.nsSubclasses import getNSSubclass
from vanilla.vanillaBase import VanillaCallbackWrapper, osVersionCurrent, osVersion10_16
from vanilla.vanillaScrollView import ScrollView

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
        self._arrangedIndexes = []
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
        self._updateArrangedIndexes()

    def arrangedIndexes(self):
        return self._arrangedIndexes

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

    # Data Editing Via Cells

    def getItemValueForColumn_row_(self, identifier, row):
        item = self._getItemForRow(row)
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

    def setItemValue_forColumn_row_(self, value, identifier, row):
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
        identifier = column.identifier()
        return self.getItemValueForColumn_row_(identifier, row)

    def tableView_sortDescriptorsDidChange_(self, tableView, sortDescriptors):
        self._updateArrangedIndexes()

    # Delegate

    def tableView_viewForTableColumn_row_(self, tableView, column, row):
        identifier = column.identifier()
        value = self.getItemValueForColumn_row_(identifier, row)
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
        self.setItemValue_forColumn_row_(value, identifier, row)
        wrapper = self.vanillaWrapper()
        if wrapper._editCallback is not None:
            wrapper._editCallback(wrapper)


class VanillaList2TableViewSubclass(AppKit.NSTableView): pass


class List2(ScrollView):

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
                    cellClass=EditTextListCell
                )
            ]
        self._tableView = getNSSubclass(self.nsTableViewClass)(self)
        self._dataSourceAndDelegate = self.dataSourceAndDelegateClass.alloc().initWithTableView_(self._tableView)
        self._tableView.setDataSource_(self._dataSourceAndDelegate)
        self._tableView.setDelegate_(self._dataSourceAndDelegate)
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
            cellClass = columnDescription.get("cellClass", EditTextListCell)
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
            cellKwargs["editable"] = editable
            if editable:
                cellKwargs["callback"] = True
            self._dataSourceAndDelegate.setCellClass_withKwargs_forColumn_(
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
        self._dataSourceAndDelegate.setGetters_setters_(getters, setters)
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

    # Data

    def set(self, items):
        """
        Set the items in the list.

        **items** should follow the same format as described in the constructor.
        """
        items = [self._wrapItem(item) for item in items]
        self._dataSourceAndDelegate.setItems_(items)

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
        indexes = self._tableView.selectedRowIndexes()
        items = self.get()
        indexes = self.getArrangedIndexes()
        items = [items[i] for i in indexes]
        return items

    def setSelectedItems(self, items):
        """
        XXX note performance issues and issue with duplicate items
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
        rowIndexes = self._tableView.selectedRowIndexes()
        arrangedIndexes = self.getArrangedIndexes()
        itemIndexes = [
            arrangedIndexes[i]
            for i in rowIndexes
        ]
        return itemIndexes

    def setSelectedIndexes(self, indexes):
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

from vanilla.vanillaEditText import EditText

class EditTextListCell(EditText):

    def __init__(self,
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            callback=callback
        )
        textField = self.getNSTextField()
        textField.setDrawsBackground_(False)
        textField.setBezeled_(False)
        textField.setEditable_(editable)


from vanilla.vanillaSlider import Slider

class SliderListCell(Slider):

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

class CheckBoxListCell(CheckBox):

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

class PopUpButtonListCell(PopUpButton):

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

class ImageListCell(ImageView):

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

class SegmentedButtonListCell(SegmentedButton):

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

class ColorWellListCell(ColorWell):

    def __init__(self,
            editable=False,
            callback=None
        ):
        super().__init__(
            "auto",
            callback=callback
        )
        colorWell = self.getNSColorWell()
        self.enable(editable)