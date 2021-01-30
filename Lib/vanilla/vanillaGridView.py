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

class GridView(VanillaBaseObject):

    """

    **columnDescriptions** An optional list of dictionaries
    defining specific attributes for the columns. 

    +--------------------------+-------------------------------+
    | *"width"* (optional)     | The width of the column.      |
    +--------------------------+-------------------------------+
    | *"padding"* (optional)   | The padding for the column.   |
    +--------------------------+-------------------------------+
    | *"placement"* (optional) | The placement for the column. |
    +--------------------------+-------------------------------+
    """

    nsGridViewClass = AppKit.NSGridView

    def __init__(self,
        posSize,
        rows,
        columnDescriptions=None,
        columnWidth=None,
        columnSpacing=0,
        columnPadding=(0, 0),
        columnPlacement="leading",
        rowHeight=None,
        rowSpacing=0,
        rowPadding=(0, 0),
        rowPlacement="top"
    ):
        self._setupView(self.nsGridViewClass, posSize)
        gridView = self._getContentView()
        gridView.setColumnSpacing_(columnSpacing)
        gridView.setRowSpacing_(rowSpacing)
        gridView.setXPlacement_(columnPlacements[columnPlacement])
        gridView.setYPlacement_(rowPlacements[rowPlacement])
        gridView.setRowAlignment_(AppKit.NSGridRowAlignmentFirstBaseline)
        # build the columns
        self._buildColumns(columnDescriptions, columnWidth, columnPadding)
        # build the rows
        self._buildRows(rows, rowHeight, rowPadding)

    def getNSGridView(self):
        return self._getContentView()

    # Building

    def _buildColumns(self, columnDescriptions, globalWidth, globalPadding):
        gridView = self._getContentView()
        for columnDescription in columnDescriptions:
            width = columnDescription.get("width", globalWidth)
            padding = columnDescription.get("padding", globalPadding)
            placement = columnDescription.get("placement")
            column = gridView.addColumnWithViews_([])
            column.setWidth_(width)
            column.setLeadingPadding_(padding[0])
            column.setTrailingPadding_(padding[1])
            if placement is not None:
                column.setXPlacement_(columnPlacements[placement])

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
            if "padding" not in row:
                row["padding"] = globalPadding
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
            padding = rowData["padding"]
            placement = rowData.get("placement")
            row = gridView.rowAtIndex_(rowIndex)
            row.setHeight_(height)
            row.setTopPadding_(padding[0])
            row.setBottomPadding_(padding[1])
            if placement is not None:
                row.setYPlacement_(rowPlacements[placement])
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
                if viewData is None:
                    continue
                view = viewData["view"]
                columnPlacement = viewData.get("columnPlacement")
                rowPlacement = viewData.get("rowPlacement")
                if isinstance(view, VanillaBaseObject):
                    view = view._getContentView()
                cell = gridView.cellAtColumnIndex_rowIndex_(columnIndex, rowIndex)
                cell.setContentView_(view)
                if columnPlacement is not None:
                    cell.setXPlacement_(columnPlacements[columnPlacement])
                if rowPlacement is not None:
                    cell.setYPlacement_(rowPlacements[rowPlacement])

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
                placement="trailing"
            ),
            dict(
                width=300,
                placement="fill"
            )
        ]

        self.editText = vanilla.EditText(
            "auto",
            "Type to test callback.",
            callback=self.editTextCallback
        )
        views = [
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
                padding=(0, 0),
                views=(
                    None,
                    vanilla.CheckBox("auto", "CheckBox 2")
                )
            ),
            dict(
                padding=(0, 0),
                views=(
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
            (
                vanilla.TextBox("auto", "RadioGroup:"),
                vanilla.RadioGroup("auto", ["One", "Two", "Three"])
            ),
            (
                vanilla.TextBox("auto", "ColorWell:"),
                vanilla.ColorWell((0, 0, 100, 75), color=AppKit.NSColor.redColor())
            ),
            dict(
                height=100,
                views=(
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
                views=(
                    vanilla.TextBox("auto", "TextEditor:"),
                    vanilla.TextEditor("auto", "TextEditor")
                )
            ),
        ]
        self.w.gridView = GridView(
            "auto",
            views,
            columnDescriptions,
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