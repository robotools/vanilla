import pprint
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
        self.w = vanilla.Window((500, 300))
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
                sortable=True,
            )
        ]
        self.w.list = vanilla.List2(
            "auto",
            items=makeItems(),
            columnDescriptions=columnDescriptions,
        )
        self.w.appendColumnButton = vanilla.Button(
            "auto",
            "Append Column",
            callback=self.appendColumnButtonCallback
        )
        self.w.removeColumnButton = vanilla.Button(
            "auto",
            "Remove Column",
            callback=self.removeColumnButtonCallback
        )
        self.w.getButton = vanilla.Button(
            "auto",
            "Get Values",
            callback=self.getButtonCallback
        )
        rules = [
            "H:|-[list]-|",
            "H:[getButton]-[appendColumnButton]-[removeColumnButton]-|",
            "V:|-[list]-[appendColumnButton]-|",
            "V:|-[list]-[removeColumnButton]-|",
            "V:|-[list]-[getButton]-|"
        ]
        self.w.addAutoPosSizeRules(rules)
        self.w.open()

    def appendColumnButtonCallback(self, sender):
        try:
            self.w.list.insertColumn(
                1,
                dict(
                    identifier="punctuation",
                    title="Punctuation",
                    sortable=True,
                    editable=True
                ),
            )
        except Exception as e:
            print(e)

    def removeColumnButtonCallback(self, sender):
        self.w.list.removeColumn(
            "punctuation"
        )

    def getButtonCallback(self, sender):
        for i, item in enumerate(self.w.list.get()):
            print(f"{i} ----------")
            for k, v in item.items():
                v = pprint.pformat(v)
                print(f"{k} : {v}")
            print("\n")


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
