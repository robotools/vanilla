import pprint
import AppKit
import vanilla

class Test:

    def __init__(self):
        self.w = vanilla.Window((300, 400))

        items = []
        for i in range(5):
            items.append(vanilla.List2GroupRow(f"Group {i + 1}"))
            items += list("123456789")

        self.w.list = vanilla.List2(
            "auto",
            items=items,
            allowsGroupRows=True,
            floatsGroupRows=True,
            allowsSorting=False,
            groupRowCellClass=CustomCell
        )
        rules = [
            "H:|[list]|",
            "V:|[list]|"
        ]
        self.w.addAutoPosSizeRules(rules)
        self.w.open()


class CustomCell(vanilla.Box):

    def __init__(self):
        super().__init__(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(
                1, 0, 0, 0.25
            ),
            borderWidth=0,
            cornerRadius=10
        )
        self.textBox = vanilla.TextBox(
            (0, 0, 0, 0)
        )

    def set(self, value):
        self.textBox.set(value)

if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
