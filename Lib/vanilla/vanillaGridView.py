import AppKit
import vanilla
from vanilla import VanillaBaseObject

import objc
objc.setVerbose(True)

columnPlacements = dict(
    leading=AppKit.NSGridCellPlacementLeading,
    center=AppKit.NSGridCellPlacementCenter,
    trailing=AppKit.NSGridCellPlacementTrailing,
    fill=AppKit.NSGridCellPlacementFill
)
rowPlacements = dict(
    top=AppKit.NSGridCellPlacementTop,
    center=AppKit.NSGridCellPlacementCenter,
    bottom=AppKit.NSGridCellPlacementBottom,
    fill=AppKit.NSGridCellPlacementFill
)
rowAlignments = dict(
    firstBaseline=AppKit.NSGridRowAlignmentFirstBaseline,
    lastBaseline=AppKit.NSGridRowAlignmentLastBaseline,
    none=AppKit.NSGridRowAlignmentNone
)

class GridView(VanillaBaseObject):

    """
    A view that allows the placement of other views within a grid.

    **contents** The contents to display within the grid. See below for structure.

    **columnWidth** The width for columns.

    **columnSpacing** The amount of spacing between columns.

    **columnPadding** The (left, right) padding for columns.

    **columnPlacement** The horizontal placement of content within columns.

    +------------+
    | "leading"  |
    +------------+
    | "center"   |
    +------------+
    | "trailing" |
    +------------+
    | "fill"     |
    +------------+

    **rowHeight** The height for rows.

    **rowSpacing** The amount of spacing between rows.

    **rowPadding** The (top, bottom) padding for rows.

    **rowPlacement** The vertical placement of content within rows.

    +----------+
    | "top"    |
    +----------+
    | "center" |
    +----------+
    | "bottom" |
    +----------+
    | "fill"   |
    +----------+

    **rowAlignment** The alignment of the row.

    +-----------------+
    | "firstBaseline" |
    +-----------------+
    | "lastBaseline"  |
    +-----------------+
    | "none"          |
    +-----------------+

    **columnDescriptions** An optional list of dictionaries
    defining specific attributes for the columns. 

    +---------------------+
    | *"width"*           |
    +---------------------+
    | *"columnPadding"*   |
    +---------------------+
    | *"columnPlacement"* |
    +---------------------+


    **Contents Definition Structure**

    Contents are defined as with a list of row definitions.
    A row definition is a list of cell definitions or a
    dictionary with this structure:

    - *cells* A list of cell definitions.
    - *rowHeight* (optional) A height for the row that overrides
      the GridView level row height.
    - *rowPadding* (optional) A (top, bottom) padding definition
      for the row that overrides the GridView level row padding.
    - *rowPlacement* (optional) A placement for the row that
      overrides the GridView level row placement.
    - *rowAlignment* (optional) An alignment for the row that
      overrides the GridView level row placement.

    Cells are defined with either a Vanilla object, a NSView
    (or NSView subclass) object, None, or a dictionary with
    this structure:

    - *view* A Vanilla object or NSView (or NSView subclass) object.
    - *width* (optional) A width to apply to the view.
    - *height* (optional) A height to apply to the view.
    - *columnPlacement* (optional) A horizontal placement for the
      cell that overrides the row level or GridView level placement.
    - *rowPlacement* (optional) A vertical placement for the cell
      that overrides the row level or GridView level placement.
    - *rowAlignment* (optional) A row alignment for the cell that
      overrides the row level or GridView level alignment.

    If a cell is defined as None, the cell will be merged with the
    first cell directly above that has content.
    """

    nsGridViewClass = AppKit.NSGridView

    def __init__(self,
            posSize,
            contents,
            columnWidth=None,
            columnSpacing=0,
            columnPadding=(0, 0),
            columnPlacement="leading",
            rowHeight=None,
            rowSpacing=0,
            rowPadding=(0, 0),
            rowPlacement="top",
            rowAlignment="firstBaseline",
            columnDescriptions=None
        ):
        if columnDescriptions is None:
            columnDescriptions = [{} for i in range(len(contents[0]))]
        self._setupView(self.nsGridViewClass, posSize)
        gridView = self._getContentView()
        gridView.setColumnSpacing_(columnSpacing)
        gridView.setRowSpacing_(rowSpacing)
        gridView.setXPlacement_(columnPlacements[columnPlacement])
        gridView.setYPlacement_(rowPlacements[rowPlacement])
        gridView.setRowAlignment_(rowAlignments[rowAlignment])
        self._columnWidth = columnWidth
        self._columnPadding = columnPadding
        self._rowHeight = rowHeight
        self._rowPadding = rowPadding
        self._buildColumns(columnDescriptions)    
        self._buildRows(contents)

    def getNSGridView(self):
        return self._getContentView()

    # Input Normalizing

    def _normalizeRows(self, rows):
        rows = [
            self._normalizeRow(row)
            for row in rows
        ]
        return rows

    def _normalizeRow(self, row):
        if not isinstance(row, dict):
            row = dict(cells=row)
        if "height" not in row:
            row["height"] = self._rowHeight
        if "rowPadding" not in row:
            row["rowPadding"] = self._rowPadding
        row["cells"] = self._normalizeCells(row["cells"])
        return row

    def _normalizeCells(self, cells):
        cells = [
            self._normalizeCell(cell)
            for cell in cells
        ]
        return cells

    def _normalizeCell(self, cell):
        if cell is None:
            return None
        if not isinstance(cell, dict):
            cell = dict(view=cell)
        return cell

    # Building

    def _buildColumns(self, columnDescriptions):
        gridView = self._getContentView()
        for columnDescription in columnDescriptions:
            column = gridView.addColumnWithViews_([])
            self._setColumnAttributes(column, columnDescription)

    def _setColumnAttributes(self, column, columnDescription):
        width = columnDescription.get("width", self._columnWidth)
        columnPadding = columnDescription.get("columnPadding", self._columnPadding)
        columnPlacement = columnDescription.get("columnPlacement")
        if width is not None:
            column.setWidth_(width)
        column.setLeadingPadding_(columnPadding[0])
        column.setTrailingPadding_(columnPadding[1])
        if columnPlacement is not None:
            column.setXPlacement_(columnPlacements[columnPlacement])

    def _populateColumns(self, columns):
        gridView = self._getContentView()
        for columnIndex, cells in enumerate(columns):
            column = gridView.columnAtIndex_(columnIndex)
            self._populateColumn(column, cells)

    def _populateColumn(self, column, cells):
        gridView = self._getContentView()
        columnIndex = gridView.indexOfColumn_(column)
        # merge cells
        if None in cells:
            mergers = [[]]
            for rowIndex, cell in enumerate(cells):
                if cell is None:
                    mergers[-1].append(rowIndex)
                else:
                    if mergers[-1]:
                        mergers.append([])
            for merger in mergers:
                if not merger:
                    continue
                start = merger[0] - 1
                # can't merge first row with a nonexistent previous row
                if start == -1:
                    continue
                end = merger[-1]
                length = end - start
                gridView.mergeCellsInHorizontalRange_verticalRange_(
                    AppKit.NSMakeRange(columnIndex, 1),
                    AppKit.NSMakeRange(start, length)
                )
        # place the views
        for rowIndex, cellData in enumerate(cells):
            self._populateCell(columnIndex, rowIndex, cellData)

    def _buildRows(self, rows):
        gridView = self._getContentView()
        rows = self._normalizeRows(rows)
        for rowIndex in range(len(rows)):
            gridView.addRowWithViews_([])
        # set row attributes
        for rowIndex, rowData in enumerate(rows):
            row = gridView.rowAtIndex_(rowIndex)
            self._setRowAttributes(row, rowData)
        # populate columns
        columns = {}
        for rowData in rows:
            cells = rowData["cells"]
            for columnIndex, view in enumerate(cells):
                if columnIndex not in columns:
                    columns[columnIndex] = []
                columns[columnIndex].append(view)
        columns = [cells for columnIndex, cells in sorted(columns.items())]
        self._populateColumns(columns)

    def _setRowAttributes(self, row, rowData):
        height = rowData["height"]
        rowPadding = rowData["rowPadding"]
        rowPlacement = rowData.get("rowPlacement")
        rowAlignment = rowData.get("rowAlignment")
        if height is not None:
            row.setHeight_(height)
        row.setTopPadding_(rowPadding[0])
        row.setBottomPadding_(rowPadding[1])
        if rowPlacement is not None:
            row.setYPlacement_(rowPlacements[rowPlacement])
        if rowAlignment is not None:
            row.setRowAlignment_(rowAlignments[rowAlignment])

    def _populateRow(self, row, cells):
        gridView = self._getContentView()
        rowIndex = gridView.indexOfRow_(row)
        for columnIndex, cellData in enumerate(cells):
            self._populateCell(columnIndex, rowIndex, cellData)

    def _populateCell(self, columnIndex, rowIndex, cellData):
        if cellData is None:
            return
        gridView = self._getContentView()
        view = cellData["view"]
        if isinstance(view, VanillaBaseObject):
            view = view._getContentView()
        cell = gridView.cellAtColumnIndex_rowIndex_(columnIndex, rowIndex)
        cell.setContentView_(view)
        columnPlacement = cellData.get("columnPlacement")
        rowPlacement = cellData.get("rowPlacement")
        rowAlignment = cellData.get("rowAlignment")
        width = cellData.get("width")
        height = cellData.get("height")
        # special handling and defaults for
        # views without an intrinsic size
        if view.intrinsicContentSize() == (-1, -1):
            if width is None:
                width = gridView.columnAtIndex_(columnIndex).width()
            if height is None:
                height = gridView.rowAtIndex_(rowIndex).height()
            if rowAlignment is None:
                rowAlignment = "none"
            if columnPlacement is None:
                columnPlacement = "leading"
            if rowPlacement is None:
                rowPlacement = "top"
        if columnPlacement is not None:
            cell.setXPlacement_(columnPlacements[columnPlacement])
        if rowPlacement is not None:
            cell.setYPlacement_(rowPlacements[rowPlacement])
        if rowAlignment is not None:
            cell.setRowAlignment_(rowAlignments[rowAlignment])
        constraints = []
        if width is not None:
            constraint = AppKit.NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                view,
                AppKit.NSLayoutAttributeWidth,
                AppKit.NSLayoutRelationEqual,
                None,
                AppKit.NSLayoutAttributeWidth,
                1.0,
                width
            )
            constraints.append(constraint)
        if height is not None:
            constraint = AppKit.NSLayoutConstraint.constraintWithItem_attribute_relatedBy_toItem_attribute_multiplier_constant_(
                view,
                AppKit.NSLayoutAttributeHeight,
                AppKit.NSLayoutRelationEqual,
                None,
                AppKit.NSLayoutAttributeHeight,
                1.0,
                height
            )
            constraints.append(constraint)
        if constraints:
            cell.setCustomPlacementConstraints_(constraints)

    # -------
    # Columns
    # -------

    def getColumnCount(self):
        """
        Get the number of columns.
        """
        gridView = self._getContentView()
        return gridView.numberOfColumns()

    def columnIsVisible(self, index):
        """
        Get the visibility of column at *index*.
        """
        gridView = self._getContentView()
        column = gridView.columnAtIndex_(index)
        return not column.isHidden()

    def showColumn(self, index, value):
        """
        Set the visibility of column at *index*.
        """
        gridView = self._getContentView()
        column = gridView.columnAtIndex_(index)
        column.setHidden_(not value)

    def appendColumn(self, cells, columnWidth=None, columnPadding=None, columnPlacement=None):
        """
        Append a column and populate it with a list of cells.
        The cells must have the same structure as defined in *__init__*.
        """
        gridView = self._getContentView()
        column = gridView.addColumnWithViews_([])
        columnDescription = {}
        if columnWidth is not None:
            columnDescription["columnWidth"] = columnWidth
        if columnPadding is not None:
            columnDescription["columnPadding"] = columnPadding
        if columnPlacement is not None:
            columnDescription["columnPlacement"] = columnPlacement
        self._setColumnAttributes(column, columnDescription)
        cells = self._normalizeCells(cells)
        self._populateColumn(column, cells)

    def insertColumn(self, index, cells, columnWidth=None, columnPadding=None, columnPlacement=None):
        """
        Insert a column at *index* and populate it with a list of cells.
        The cells must have the same structure as defined in *__init__*.
        """
        gridView = self._getContentView()
        column = gridView.insertColumnAtIndex_withViews_(index, [])
        columnDescription = {}
        if columnWidth is not None:
            columnDescription["columnWidth"] = columnWidth
        if columnPadding is not None:
            columnDescription["columnPadding"] = columnPadding
        if columnPlacement is not None:
            columnDescription["columnPlacement"] = columnPlacement
        self._setColumnAttributes(column, columnDescription)
        cells = self._normalizeCells(cells)
        self._populateColumn(column, cells)

    def removeColumn(self, index):
        """
        Remove column at *index*.
        """
        gridView = self._getContentView()
        gridView.removeColumnAtIndex_(index)

    def moveColumn(self, fromIndex, toIndex):
        """
        Move column at *fromIndex* to *toIndex*.
        """
        gridView = self._getContentView()
        gridView.moveColumnAtIndex_toIndex_(fromIndex, toIndex)

    # ----
    # Rows
    # ----

    def getRowCount(self):
        """
        Get the number of rows.
        """
        gridView = self._getContentView()
        return gridView.numberOfRows()

    def showRow(self, index, value):
        """
        Set the visibility of row at *index*.
        """
        gridView = self._getContentView()
        row = gridView.rowAtIndex_(index)
        row.setHidden_(not value)

    def rowIsVisible(self, index):
        """
        Get the visibility of row at *index*.
        """
        gridView = self._getContentView()
        row = gridView.rowAtIndex_(index)
        return not row.isHidden()

    def appendRow(self, cells, rowHeight=None, rowSpacing=None, rowPadding=None, rowPlacement=None, rowAlignment=None):
        """
        Append a row and populate it with a list of cells.
        The cells must have the same structure as defined in *__init__*.

        Merging is not possible with this method.
        """
        gridView = self._getContentView()
        rowDescription = dict(cells=cells)
        if rowHeight is not None:
            rowDescription["rowHeight"] = rowHeight
        if rowSpacing is not None:
            rowDescription["rowSpacing"] = rowSpacing
        if rowPadding is not None:
            rowDescription["rowPadding"] = rowPadding
        if rowPlacement is not None:
            rowDescription["rowPlacement"] = rowPlacement
        if rowAlignment is not None:
            rowDescription["rowAlignment"] = rowAlignment
        rowDescription = self._normalizeRow(rowDescription)
        row = gridView.addRowWithViews_([])
        self._setRowAttributes(row, rowDescription)
        self._populateRow(row, rowDescription["cells"])

    def insertRow(self, index, cells, rowHeight=None, rowSpacing=None, rowPadding=None, rowPlacement=None, rowAlignment=None):
        """
        Insert a row at *index* and populate it with a list of cells.
        The cells definition must have the same structure as defined in *__init__*.

        Merging is not possible with this method.
        """
        gridView = self._getContentView()
        rowDescription = dict(cells=cells)
        if rowHeight is not None:
            rowDescription["rowHeight"] = rowHeight
        if rowSpacing is not None:
            rowDescription["rowSpacing"] = rowSpacing
        if rowPadding is not None:
            rowDescription["rowPadding"] = rowPadding
        if rowPlacement is not None:
            rowDescription["rowPlacement"] = rowPlacement
        if rowAlignment is not None:
            rowDescription["rowAlignment"] = rowAlignment
        rowDescription = self._normalizeRow(rowDescription)
        row = gridView.insertRowAtIndex_withViews_(index, [])
        self._setRowAttributes(row, rowDescription)
        self._populateRow(row, rowDescription["cells"])

    def removeRow(self, index):
        """
        Remove row at *index*.
        """
        gridView = self._getContentView()
        gridView.removeRowAtIndex_(index)

    def moveRow(self, fromIndex, toIndex):
        """
        Move row at *fromIndex* to *toIndex*.
        """
        gridView = self._getContentView()
        gridView.moveRowAtIndex_toIndex_(fromIndex, toIndex)


# ----
# Test
# ----

class Test:

    def __init__(self):
        self.w = vanilla.Window((0, 0))

        columnDescriptions = [
            dict(
                columnPlacement="trailing"
            ),
            dict(
                width=300,
                columnPlacement="fill"
            )
        ]

        self.editText = vanilla.EditText(
            "auto",
            "Type to test callback.",
            callback=self.editTextCallback
        )
        rows = [
            (
                vanilla.TextBox("auto", "TextBox:"),
                vanilla.TextBox("auto", "Hello")
            ),
            (
                vanilla.TextBox("auto", "EditText:"),
                self.editText
            ),
            (
                vanilla.TextBox("auto", "Button:"),
                vanilla.Button("auto", "Button")
            ),
            (
                vanilla.TextBox("auto", "PopUpButton:"),
                vanilla.PopUpButton("auto", ["PopUpButton"])
            ),
            (
                vanilla.TextBox("auto", "ComboBox:"),
                vanilla.ComboBox("auto", ["ComboBox"])
            ),
            (
                vanilla.TextBox("auto", "CheckBox:"),
                vanilla.CheckBox("auto", "CheckBox 1")
            ),
            dict(
                rowPadding=(0, 0),
                cells=(
                    None,
                    vanilla.CheckBox("auto", "CheckBox 2")
                )
            ),
            dict(
                rowPadding=(0, 0),
                cells=(
                    None,
                    vanilla.CheckBox("auto", "CheckBox 3")
                )
            ),
            (
                vanilla.TextBox("auto", "SegmentedButton:"),
                vanilla.SegmentedButton(
                    "auto",
                    [
                        dict(title="One"),
                        dict(title="Two"),
                        dict(title="Three")
                    ],
                    sizeStyle="regular"
                )
            ),
            (
                vanilla.TextBox("auto", "Slider:"),
                vanilla.Slider("auto", minValue=0, maxValue=100, value=50)
            ),
            dict(
                height=100,
                cells=(
                    vanilla.TextBox("auto", "RadioGroup:"),
                    dict(
                        rowAlignment="none",
                        view=vanilla.RadioGroup("auto", ["One", "Two", "Three"])
                    )
                )
            ),
            dict(
                height=100,
                cells=(
                    vanilla.TextBox("auto", "ColorWell:"),
                    dict(
                        width=50,
                        height=75,
                        view=vanilla.ColorWell("auto", color=AppKit.NSColor.redColor())
                    )
                )
            ),
            dict(
                height=100,
                cells=(
                    vanilla.TextBox("auto", "List:"),
                    dict(
                        columnPlacement="fill",
                        rowPlacement="fill",
                        view=vanilla.List("auto", ["One", "Two", "Three"])
                    )
                )
            ),
            dict(
                height=100,
                cells=(
                    vanilla.TextBox("auto", "TextEditor:"),
                    vanilla.TextEditor("auto", "TextEditor")
                )
            ),
        ]
        self.w.gridView = GridView(
            "auto",
            rows,
            columnDescriptions=columnDescriptions,
            columnWidth=150,
            columnSpacing=10,
            rowHeight=25,
            rowPadding=(15, 0)
        )
        self.columnCount = len(columnDescriptions)
        self.rowCount = len(rows)

        # append, insert, etc. buttons

        self.appendColumnButton = vanilla.Button("auto", "Append", callback=self.appendColumnButtonCallback)
        self.insertColumnButton = vanilla.Button("auto", "Insert", callback=self.insertColumnButtonCallback)
        self.removeColumnButton = vanilla.Button("auto", "Remove", callback=self.removeColumnButtonCallback)
        self.moveColumnButton = vanilla.Button("auto", "Move", callback=self.moveColumnButtonCallback)
        self.showColumnButton = vanilla.Button("auto", "Show/Hide", callback=self.showColumnButtonCallback)

        self.appendRowButton = vanilla.Button("auto", "Append", callback=self.appendRowButtonCallback)
        self.insertRowButton = vanilla.Button("auto", "Insert", callback=self.insertRowButtonCallback)
        self.removeRowButton = vanilla.Button("auto", "Remove", callback=self.removeRowButtonCallback)
        self.moveRowButton = vanilla.Button("auto", "Move", callback=self.moveRowButtonCallback)
        self.showRowButton = vanilla.Button("auto", "Show/Hide", callback=self.showRowButtonCallback)

        rows = [
            [
                vanilla.TextBox("auto", "Column:"), self.appendColumnButton, self.insertColumnButton, self.removeColumnButton, self.moveColumnButton, self.showColumnButton
            ],
            [
                vanilla.TextBox("auto", "Row:"), self.appendRowButton, self.insertRowButton, self.removeRowButton, self.moveRowButton, self.showRowButton
            ]
        ]
        columnDescriptions = [dict(width=60, columnPlacement="trailing")]
        for i in range(len(rows[0]) - 1):
            columnDescriptions.append({})

        self.w.line = vanilla.HorizontalLine("auto")
        self.w.testButtonGrid = GridView(
            "auto",
            rows,
            columnDescriptions=columnDescriptions,
            columnWidth=100,
            columnSpacing=5,
            columnPlacement="fill",
            rowHeight=25
        )

        rules = [
            "H:|-margin-[gridView]-margin-|",
            "H:|[line]|",
            "H:|-margin-[testButtonGrid]-margin-|",
            "V:|"
               "-margin-"
               "[gridView]"
               "-margin-"
               "[line]"
               "-margin-"
               "[testButtonGrid]"
               "-margin-"
              "|"
        ]
        metrics = dict(
            margin=15
        )
        self.w.addAutoPosSizeRules(rules, metrics)
        self.w.open()

    def editTextCallback(self, sender):
        print("editTextCallback:", sender.get())

    # Column Tests

    def _makeRows(self):
        columnIndex = self.w.gridView.getColumnCount()
        rowCount = self.w.gridView.getRowCount()
        rows = [
            vanilla.TextBox(
                "auto",
                "C-{columnIndex}-{rowIndex}".format(
                    columnIndex=columnIndex,
                    rowIndex=rowIndex
                )
            )
            for rowIndex in range(rowCount)
        ]
        return rows

    def appendColumnButtonCallback(self, sender):
        rows = self._makeRows()
        self.w.gridView.appendColumn(rows, columnWidth=50)

    def insertColumnButtonCallback(self, sender):
        rows = self._makeRows()
        self.w.gridView.insertColumn(self.columnCount, rows, columnWidth=50)

    def removeColumnButtonCallback(self, sender):
        if self.w.gridView.getColumnCount() <= self.columnCount:
            # not a limitation of GridView, just a limitation of this test
            print("can't delete one of the main columns")
        else:
            self.w.gridView.removeColumn(self.columnCount)

    def moveColumnButtonCallback(self, sender):
        self.w.gridView.moveColumn(0, 1)

    def showColumnButtonCallback(self, sender):
        visible = self.w.gridView.columnIsVisible(1)
        self.w.gridView.showColumn(1, not visible)

    # Row Tests

    def _makeRow(self):
        columnCount = self.w.gridView.getColumnCount()
        rowIndex = self.w.gridView.getRowCount()
        cells = [
            vanilla.TextBox(
                "auto",
                "R-{columnIndex}-{rowIndex}".format(
                    columnIndex=columnIndex,
                    rowIndex=rowIndex
                )
            )
            for columnIndex in range(columnCount)
        ]
        return cells

    def appendRowButtonCallback(self, sender):
        row = self._makeRow()
        self.w.gridView.appendRow(row)

    def insertRowButtonCallback(self, sender):
        row = self._makeRow()
        self.w.gridView.insertRow(self.rowCount, row)

    def removeRowButtonCallback(self, sender):
        if self.w.gridView.getRowCount() <= self.rowCount:
            # not a limitation of GridView, just a limitation of this test
            print("can't delete one of the main rows")
        else:
            self.w.gridView.removeRow(self.rowCount)

    def moveRowButtonCallback(self, sender):
        self.w.gridView.moveRow(0, 1)

    def showRowButtonCallback(self, sender):
        visible = self.w.gridView.rowIsVisible(1)
        self.w.gridView.showRow(1, not visible)


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)