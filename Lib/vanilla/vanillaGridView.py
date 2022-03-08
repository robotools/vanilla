import AppKit
from vanilla import VanillaBaseObject

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

    .. image:: /_images/GridView.png

    ::

        from vanilla import Button, GridView, Window

        class GridViewExample:
            def __init__(self):
                self.w = Window((120, 90))

                self.button1 = Button("auto", "one")
                self.button2 = Button("auto", "two")
                self.button3 = Button("auto", "three")
                self.button4 = Button("auto", "four")

                self.w.gridView = GridView(
                    (0, 0, 0, 0),
                    contents=[
                        dict(
                            cells=[
                                dict(view=self.button1),
                                dict(view=self.button2),
                            ]
                        ),
                        dict(
                            cells=[
                                dict(view=self.button3),
                                dict(view=self.button4),
                            ]
                        ),
                    ],
                    columnPadding=(4, 4),
                    rowPadding=(4, 4),
                )

                self.w.open()


        GridViewExample()


    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing
    the position and size of the grid view.

    **contents** The contents to display within the grid. See below for structure.

    **columnWidth** The width for columns.

    **columnSpacing** The amount of spacing between columns.

    **columnPadding** The (left, right) padding for columns.

    **columnPlacement** The horizontal placement of content within columns. Options:

    * "leading"
    * "center"
    * "trailing"
    * "fill"

    **rowHeight** The height for rows.

    **rowSpacing** The amount of spacing between rows.

    **rowPadding** The (top, bottom) padding for rows.

    **rowPlacement** The vertical placement of content within rows. Options:

    * "top"
    * "center"
    * "bottom"
    * "fill"

    **rowAlignment** The alignment of the row. Options:

    * "firstBaseline"
    * "lastBaseline"
    * "none"

    **columnDescriptions** An optional list of dictionaries
    defining specific attributes for the columns. Options:

    * "width"
    * "columnPadding"
    * "columnPlacement"


    **Contents Definition Structure**

    Contents are defined as with a list of row definitions.
    A row definition is a list of cell definitions or a
    dictionary with this structure:

    * **cells** A list of cell definitions.
    * **rowHeight** (optional) A height for the row that overrides
      the GridView level row height.
    * **rowPadding** (optional) A (top, bottom) padding definition
      for the row that overrides the GridView level row padding.
    * **rowPlacement** (optional) A placement for the row that
      overrides the GridView level row placement.
    * **rowAlignment** (optional) An alignment for the row that
      overrides the GridView level row placement.

    Cells are defined with either a Vanilla object, a NSView
    (or NSView subclass) object, None, or a dictionary with
    this structure:

    * **view** A Vanilla object or NSView (or NSView subclass) object.
    * **width** (optional) A width to apply to the view.
    * **height** (optional) A height to apply to the view.
    * **columnPlacement** (optional) A horizontal placement for the
      cell that overrides the row level or GridView level placement.
    * **rowPlacement** (optional) A vertical placement for the cell
      that overrides the row level or GridView level placement.
    * **rowAlignment** (optional) A row alignment for the cell that
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
            sample = contents[0]
            if isinstance(sample, dict):
                count = len(sample["cells"])
            else:
                count = len(sample)
            columnDescriptions = [{} for i in range(count)]
        self._setupView(self.nsGridViewClass, posSize)
        gridView = self.getNSGridView()
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
        gridView = self.getNSGridView()
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
        gridView = self.getNSGridView()
        for columnIndex, cells in enumerate(columns):
            column = gridView.columnAtIndex_(columnIndex)
            self._populateColumn(column, cells)

    def _populateColumn(self, column, cells):
        gridView = self.getNSGridView()
        columnIndex = gridView.indexOfColumn_(column)
        for rowIndex, cellData in enumerate(cells):
            self._populateCell(columnIndex, rowIndex, cellData)

    def _buildRows(self, rows):
        gridView = self.getNSGridView()
        rows = self._normalizeRows(rows)
        for rowIndex in range(len(rows)):
            gridView.addRowWithViews_([])
        # set row attributes
        for rowIndex, rowData in enumerate(rows):
            row = gridView.rowAtIndex_(rowIndex)
            self._setRowAttributes(row, rowData)
        # merge cells
        mergers = {}
        for rowIndex, rowData in enumerate(rows):
            rowMergers = [[]]
            for columnIndex, cell in enumerate(rowData["cells"]):
                if cell is None:
                    rowMergers[-1].append(columnIndex)
                else:
                    if rowMergers[-1]:
                        rowMergers.append([])
            if rowMergers[0]:
                mergers[rowIndex] = rowMergers
        for rowIndex, rowMergers in sorted(mergers.items()):
            for merger in rowMergers:
                if not merger:
                    continue
                start = merger[0] - 1
                # can't merge first column with a nonexistent previous column
                if start == -1:
                    continue
                end = merger[-1] + 1
                length = end - start
                gridView.mergeCellsInHorizontalRange_verticalRange_(
                    AppKit.NSMakeRange(start, length),
                    AppKit.NSMakeRange(rowIndex, 1)
                )
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
        gridView = self.getNSGridView()
        rowIndex = gridView.indexOfRow_(row)
        for columnIndex, cellData in enumerate(cells):
            self._populateCell(columnIndex, rowIndex, cellData)

    def _populateCell(self, columnIndex, rowIndex, cellData):
        if cellData is None:
            return
        gridView = self.getNSGridView()
        view = cellData["view"]
        if isinstance(view, VanillaBaseObject):
            view = view._nsObject
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
            w, h = view.fittingSize()
            if width is None:
                if w > 0:
                    width = w
                else:
                    width = gridView.columnAtIndex_(columnIndex).width()
            if height is None:
                if h > 0:
                    height = h
                else:
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
        gridView = self.getNSGridView()
        return gridView.numberOfColumns()

    def columnIsVisible(self, index):
        """
        Get the visibility of column at *index*.
        """
        gridView = self.getNSGridView()
        column = gridView.columnAtIndex_(index)
        return not column.isHidden()

    def showColumn(self, index, value):
        """
        Set the visibility of column at *index*.
        """
        gridView = self.getNSGridView()
        column = gridView.columnAtIndex_(index)
        column.setHidden_(not value)

    def appendColumn(self, cells, columnWidth=None, columnPadding=None, columnPlacement=None):
        """
        Append a column and populate it with a list of cells.
        The cells must have the same structure as defined in *__init__*.
        """
        gridView = self.getNSGridView()
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
        gridView = self.getNSGridView()
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
        gridView = self.getNSGridView()
        gridView.removeColumnAtIndex_(index)

    def moveColumn(self, fromIndex, toIndex):
        """
        Move column at *fromIndex* to *toIndex*.
        """
        gridView = self.getNSGridView()
        gridView.moveColumnAtIndex_toIndex_(fromIndex, toIndex)

    # ----
    # Rows
    # ----

    def getRowCount(self):
        """
        Get the number of rows.
        """
        gridView = self.getNSGridView()
        return gridView.numberOfRows()

    def showRow(self, index, value):
        """
        Set the visibility of row at *index*.
        """
        gridView = self.getNSGridView()
        row = gridView.rowAtIndex_(index)
        row.setHidden_(not value)

    def rowIsVisible(self, index):
        """
        Get the visibility of row at *index*.
        """
        gridView = self.getNSGridView()
        row = gridView.rowAtIndex_(index)
        return not row.isHidden()

    def appendRow(self, cells, rowHeight=None, rowPadding=None, rowPlacement=None, rowAlignment=None):
        """
        Append a row and populate it with a list of cells.
        The cells must have the same structure as defined in *__init__*.

        Merging is not possible with this method.
        """
        gridView = self.getNSGridView()
        rowDescription = dict(cells=cells)
        if rowHeight is not None:
            rowDescription["rowHeight"] = rowHeight
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

    def insertRow(self, index, cells, rowHeight=None, rowPadding=None, rowPlacement=None, rowAlignment=None):
        """
        Insert a row at *index* and populate it with a list of cells.
        The cells definition must have the same structure as defined in *__init__*.

        Merging is not possible with this method.
        """
        gridView = self.getNSGridView()
        rowDescription = dict(cells=cells)
        if rowHeight is not None:
            rowDescription["rowHeight"] = rowHeight
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
        gridView = self.getNSGridView()
        gridView.removeRowAtIndex_(index)

    def moveRow(self, fromIndex, toIndex):
        """
        Move row at *fromIndex* to *toIndex*.
        """
        gridView = self.getNSGridView()
        gridView.moveRowAtIndex_toIndex_(fromIndex, toIndex)
