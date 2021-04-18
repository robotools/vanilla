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
            allowsSorting=False
        )
        rules = [
            "H:|[list]|",
            "V:|[list]|"
        ]
        self.w.addAutoPosSizeRules(rules)
        self.w.open()


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
