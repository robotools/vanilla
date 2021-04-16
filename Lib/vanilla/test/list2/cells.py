import pprint
import AppKit
import vanilla

class Test:

    def __init__(self):
        self.w = vanilla.Window((1000, 500))
        self.w.line = vanilla.VerticalLine("auto")

        items = []
        for i in range(3):
            d = dict(
                textField="ABC",
                editableTextField="XYZ",
                slider=25,
                editableSlider=75,
                checkBox=True,
                editableCheckBox=False,
                popUpButton=1,
                editablePopUpButton=2,
                image=AppKit.NSImage.imageNamed_(AppKit.NSImageNameTrashFull),
                segmentedButton=1,
                editableSegmentedButton=2,
                colorWell=AppKit.NSColor.redColor(),
                editableColorWell=AppKit.NSColor.greenColor(),
                custom=dict(
                    c=AppKit.NSColor.yellowColor(),
                    pub=1,
                    cb=False,
                    s=0.5
                )
            )
            items.append(d)

        columnDescriptions = [
            dict(
                identifier="textField",
                title="TextField",
                width=75,
                editable=False
            ),
            dict(
                identifier="editableTextField",
                title="TextField-E",
                width=75,
                editable=True
            ),
            dict(
                identifier="slider",
                title="Slider",
                width=100,
                cellClass=vanilla.SliderList2Cell,
                cellClassArguments=dict(
                    minValue=0,
                    maxValue=100
                ),
                editable=False,
            ),
            dict(
                identifier="editableSlider",
                title="Slider-E",
                width=100,
                cellClass=vanilla.SliderList2Cell,
                cellClassArguments=dict(
                    minValue=0,
                    maxValue=100
                ),
                editable=True,
            ),
            dict(
                identifier="checkBox",
                title="CheckBox",
                width=20,
                cellClass=vanilla.CheckBoxList2Cell,
                editable=False,
            ),
            dict(
                identifier="editableCheckBox",
                title="CheckBox-E",
                width=20,
                cellClass=vanilla.CheckBoxList2Cell,
                editable=True,
            ),
            dict(
                identifier="popUpButton",
                title="PopUpButton",
                width=100,
                cellClass=vanilla.PopUpButtonList2Cell,
                cellClassArguments=dict(
                    items=list("ABCDE")
                ),
                editable=False,
            ),
            dict(
                identifier="editablePopUpButton",
                title="PopUpButton-E",
                width=100,
                cellClass=vanilla.PopUpButtonList2Cell,
                cellClassArguments=dict(
                    items=list("ABCDE")
                ),
                editable=True,
            ),
            dict(
                identifier="image",
                title="Image",
                width=35,
                cellClass=vanilla.ImageList2Cell
            ),
            dict(
                identifier="segmentedButton",
                title="SegmentedButton",
                width=100,
                cellClass=vanilla.SegmentedButtonList2Cell,
                cellClassArguments=dict(
                    segmentDescriptions=[
                        dict(title="A"),
                        dict(title="B"),
                        dict(title="C")
                    ]
                ),
                editable=False,
            ),
            dict(
                identifier="editableSegmentedButton",
                title="SegmentedButton-E",
                width=100,
                cellClass=vanilla.SegmentedButtonList2Cell,
                cellClassArguments=dict(
                    segmentDescriptions=[
                        dict(title="A"),
                        dict(title="B"),
                        dict(title="C")
                    ]
                ),
                editable=True,
            ),
            dict(
                identifier="colorWell",
                title="ColorWell",
                width=50,
                cellClass=vanilla.ColorWellList2Cell,
                editable=False,
            ),
            dict(
                identifier="editableColorWell",
                title="ColorWell-E",
                width=50,
                cellClass=vanilla.ColorWellList2Cell,
                editable=True,
            ),
            dict(
                identifier="custom",
                title="Custom",
                width=100,
                cellClass=CustomList2Cell,
                editable=True,
            ),
        ]
        self.w.list = vanilla.List2(
            "auto",
            items=items,
            columnDescriptions=columnDescriptions,
            editCallback=self.editCallback
        )
        self.w.getButton = vanilla.Button(
            "auto",
            "Get Values",
            callback=self.getButtonCallback
        )
        rules = [
            "H:|-[list]-|",
            "H:[getButton]-|",
            "V:|-[list]-[getButton]-|"
        ]
        self.w.addAutoPosSizeRules(rules)
        self.w.open()

    def editCallback(self, sender):
        print("editCallback")

    def getButtonCallback(self, sender):
        for i, item in enumerate(self.w.list.get()):
            print(f"{i} ----------")
            for k, v in item.items():
                if k == "image":
                    continue
                v = pprint.pformat(v)
                print(f"{k} : {v}")
            print("\n")


class CustomList2Cell(vanilla.Box):

    def __init__(self, editable=True, callback=None):
        self.callback = callback
        super().__init__(
            "auto",
            cornerRadius=10
        )
        self.popUpButton = vanilla.PopUpButton(
            "auto",
            items=list("ABC"),
            callback=self.changedCallback
        )
        self.checkBox = vanilla.CheckBox(
            "auto",
            title="Test",
            callback=self.changedCallback
        )
        self.slider = vanilla.Slider(
            "auto",
            minValue=0,
            maxValue=1.0,
            callback=self.changedCallback
        )
        rules = [
            "H:|-space-[popUpButton]-space-|",
            "H:|-space-[checkBox]-space-|",
            "H:|-space-[slider]-space-|",
            "V:|-space-[popUpButton]-space-[checkBox]-space-[slider]-space-|",
        ]
        metrics = dict(
            space=10
        )
        self.addAutoPosSizeRules(rules, metrics)

    def changedCallback(self, sender):
        self.callback(self)

    def get(self):
        value = dict(
            c=self.getNSBox().backgroundColor(),
            pub=self.popUpButton.get(),
            cb=self.checkBox.get(),
            s=self.slider.get()
        )
        return value

    def set(self, value):
        self.getNSBox().setBackgroundColor_(value["c"])
        self.popUpButton.set(value["pub"])
        self.checkBox.set(value["cb"])
        self.slider.set(value["s"])


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
