import AppKit
import vanilla
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
    (or NSView subclass) object or a dictionary with this structure:

    - *view* A Vanilla object or NSView (or NSView subclass) object.
    - *width* (optional) A width to apply to the view.
    - *height* (optional) A height to apply to the view.
    - *columnPlacement* (optional) A horizontal placement for the
      cell that overrides the row level or GridView level placement.
    - *rowPlacement* (optional) A vertical placement for the cell
      that overrides the row level or GridView level placement.
    - *rowAlignment* (optional) A row alignment for the cell that
      overrides the row level or GridView level alignment.
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
        self._setupView(self.nsGridViewClass, posSize)
        gridView = self._getContentView()
        gridView.setColumnSpacing_(columnSpacing)
        gridView.setRowSpacing_(rowSpacing)
        gridView.setXPlacement_(columnPlacements[columnPlacement])
        gridView.setYPlacement_(rowPlacements[rowPlacement])
        gridView.setRowAlignment_(rowAlignments[rowAlignment])
        self._buildColumns(columnDescriptions, columnWidth, columnPadding)
        self._buildRows(contents, rowHeight, rowPadding)

    def getNSGridView(self):
        return self._getContentView()

    # Building

    def _buildColumns(self, columnDescriptions, globalWidth, globalPadding):
        gridView = self._getContentView()
        for columnDescription in columnDescriptions:
            width = columnDescription.get("width", globalWidth)
            columnPadding = columnDescription.get("columnPadding", globalPadding)
            columnPlacement = columnDescription.get("columnPlacement")
            column = gridView.addColumnWithViews_([])
            column.setWidth_(width)
            column.setLeadingPadding_(columnPadding[0])
            column.setTrailingPadding_(columnPadding[1])
            if columnPlacement is not None:
                column.setXPlacement_(columnPlacements[columnPlacement])

    def _buildRows(self, rows, globalHeight, globalPadding):
        gridView = self._getContentView()
        for rowIndex in range(len(rows)):
            gridView.addRowWithViews_([])
        # normalize the data
        r = []
        for row in rows:
            if not isinstance(row, dict):
                row = dict(views=row)
            if "height" not in row:
                row["height"] = globalHeight
            if "rowPadding" not in row:
                row["rowPadding"] = globalPadding
            v = []
            for view in row["views"]:
                if not isinstance(view, dict):
                    view = dict(view=view)
                v.append(view)
            row["views"] = v
            r.append(row)
        rows = r
        # set row sizing
        for rowIndex, rowData in enumerate(rows):
            height = rowData["height"]
            rowPadding = rowData["rowPadding"]
            rowPlacement = rowData.get("rowPlacement")
            rowAlignment = rowData.get("rowAlignment")
            row = gridView.rowAtIndex_(rowIndex)
            row.setHeight_(height)
            row.setTopPadding_(rowPadding[0])
            row.setBottomPadding_(rowPadding[1])
            if rowPlacement is not None:
                row.setYPlacement_(rowPlacements[rowPlacement])
            if rowAlignment is not None:
                row.setRowAlignment_(rowAlignments[rowAlignment])
        # populate columns
        columns = {}
        for rowData in rows:
            views = rowData["views"]
            for columnIndex, view in enumerate(views):
                if columnIndex not in columns:
                    columns[columnIndex] = []
                columns[columnIndex].append(view)
        columns = [views for columnIndex, views in sorted(columns.items())]
        self._populateColumns(columns)

    def _populateColumns(self, columns):
        gridView = self._getContentView()
        for columnIndex, views in enumerate(columns):
            # merge cells
            if None in views:
                mergers = [[]]
                for rowIndex, view in enumerate(views):
                    if view is None:
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
            for rowIndex, viewData in enumerate(views):
                view = viewData["view"]
                if view is None:
                    continue
                if isinstance(view, VanillaBaseObject):
                    view = view._getContentView()
                cell = gridView.cellAtColumnIndex_rowIndex_(columnIndex, rowIndex)
                cell.setContentView_(view)
                columnPlacement = viewData.get("columnPlacement")
                rowPlacement = viewData.get("rowPlacement")
                rowAlignment = viewData.get("rowAlignment")
                width = viewData.get("width")
                height = viewData.get("height")
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


    # Columns & Rows

    def showColumn(self, index, value):
        gridView = self._getContentView()
        column = gridView.columnAtIndex_(index)
        column.setHidden_(not value)

    def showRow(self, index, value):
        gridView = self._getContentView()
        row = gridView.rowAtIndex_(index)
        row.setHidden_(not value)


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

        rules = [
            "H:|-margin-[gridView]-margin-|",
            "V:|-margin-[gridView]-margin-|"
        ]
        metrics = dict(
            margin=15
        )
        self.w.addAutoPosSizeRules(rules, metrics)
        self.w.open()

    def editTextCallback(self, sender):
        print("editTextCallback:", sender.get())


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)