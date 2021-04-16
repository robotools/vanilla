import vanilla

def makeItems():
    items = []
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    for i, letter in enumerate(letters):
        number = i + 1
        item = dict(
            letter=letter,
            number=number
        )
        items.append(item)
    return items


class Test:

    def __init__(self):
        self.w = vanilla.Window((500, 1))
        self.w.line = vanilla.VerticalLine("auto")

        columnDescriptions = [
            dict(
                identifier="letter",
                title="Letter",
                sortable=True
            ),
            dict(
                identifier="number",
                title="Number",
                sortable=True
            )
        ]
        self.w.text = vanilla.TextBox(
            "auto",
            "Select items on the left and the same items "
            "should be selected on the right regardless "
            "of different sort orders."
        )
        self.w.itemList1 = vanilla.List2(
            "auto",
            items=makeItems(),
            columnDescriptions=columnDescriptions,
            selectionCallback=self.itemList1SelectionCallback
        )
        self.w.itemList2 = vanilla.List2(
            "auto",
            items=makeItems(),
            columnDescriptions=columnDescriptions
        )
        rules = [
            "H:|-[text]-|",
            "H:|-[itemList1]-[itemList2(==itemList1)]-|",
            "V:|-[text]",
            "V:[text]-[itemList1(==300)]-|",
            "V:[text]-[itemList2(==itemList1)]-|",
        ]
        self.w.addAutoPosSizeRules(rules)
        self.w.open()

    def itemList1SelectionCallback(self, sender):
        indexes = self.w.itemList1.getSelectedIndexes()
        self.w.itemList2.setSelectedIndexes(indexes)


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
