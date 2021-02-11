import AppKit
import vanilla

class TestGridView:

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
            dict(
                height=100,
                cells=(
                    vanilla.TextBox("auto", "Box:"),
                    vanilla.Box("auto", fillColor=AppKit.NSColor.blueColor(), cornerRadius=20)
                )
            ),
        ]
        self.w.gridView = vanilla.GridView(
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
        self.w.testButtonGrid = vanilla.GridView(
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
    import vanilla
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(TestGridView)