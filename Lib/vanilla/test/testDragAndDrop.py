import os
import objc
import AppKit
import vanilla
from vanilla.dragAndDrop import dropOperationMap

objc.setVerbose(True)


# ----
# Test
# ----

import objc
objc.setVerbose(True)

draggingImages = []
colors = [
    (0, 0, 0),
    (1, 0, 0),
    (0, 1, 0),
    (0, 0, 1),
    (1, 1, 0),
    (0, 1, 1),
    (1, 0, 1),
    (0.5, 1, 0),
    (0, 0.5, 1),
    (1, 1, 1)
]
for color in colors:
    image = AppKit.NSImage.alloc().initWithSize_((50, 50))
    image.lockFocus()
    r, g, b = color
    AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(r, g, b, 0.8).set()
    path = AppKit.NSBezierPath.bezierPathWithRoundedRect_xRadius_yRadius_(
        ((0, 0), image.size()),
        10,
        10
    )
    path.fill()
    image.unlockFocus()
    draggingImages.append(image)

draggingValues = dict(
    string=[],
    plist=[]
)
for i in range(10):
    letters = "ABCDEFGIJKLMNOPQRSTUVWXYZ"
    draggingValues["string"].append(letters[i])
    draggingValues["plist"].append(
        dict(
            letter=letters[i],
            number=i
        )
    )

class DraggingSourceNSView(AppKit.NSView):

    draggingItemCount = 1
    draggingFormation = "default"
    draggingType = "string"

    def drawRect_(self, rect):
        rect = self.bounds()
        AppKit.NSColor.whiteColor().set()
        AppKit.NSRectFill(rect)
        rect = AppKit.NSInsetRect(rect, 20, 20)
        AppKit.NSColor.greenColor().set()
        AppKit.NSRectFill(rect)

    def mouseDown_(self, event):
        width, height = self.frame().size
        x = (width * 0.5)
        items = []
        for i in range(self.draggingItemCount):
            image = draggingImages[i]
            value = draggingValues[self.draggingType][i]
            y = height / (i + 1)
            location = (x, y)
            item = dict(
                typesAndValues={
                    self.draggingType : value
                },
                image=image,
                location=location
            )
            items.append(item)
        vanilla.startDraggingSession(
            view=self,
            event=event,
            items=items,
            formation=self.draggingFormation
        )


class DraggingSourceView(vanilla.Group):

    nsViewClass = DraggingSourceNSView


class Test:

    def __init__(self):
        self.w = vanilla.Window(
            (1, 1),
            "Dragon Drop"
        )

        titleSpacing = 5
        controlSpacing = 10

        # source settings

        self.dragSourceTitle = vanilla.TextBox(
            "auto",
            "Drag Details:"
        )
        self.dragSourceCountSlider = vanilla.Slider(
            "auto",
            minValue=1,
            maxValue=10,
            value=1,
            tickMarkCount=10,
            stopOnTickMarks=True,
            callback=self.dragSourceSettingsCallback
        )
        self.dragSourceTypePopUp = vanilla.PopUpButton(
            "auto",
            [
                "string",
                "plist"
            ],
            callback=self.dragSourceSettingsCallback
        )
        self.dragSourceFormationPopUp = vanilla.PopUpButton(
            "auto",
            [
                "default",
                "none",
                "pile",
                "stack",
                "list"
            ],
            callback=self.dragSourceSettingsCallback
        )
        self.dragSourceSettingsStack = vanilla.VerticalStackView(
            "auto",
            views=[
                dict(
                    view=vanilla.TextBox("auto", "Drag Count:"),
                    width="fill",
                    spacing=titleSpacing
                ),
                dict(
                    view=self.dragSourceCountSlider,
                    width="fill"
                ),
                dict(
                    view=vanilla.TextBox("auto", "Drag Type:"),
                    width="fill",
                    spacing=titleSpacing
                ),
                dict(
                    view=self.dragSourceTypePopUp,
                    width="fill"
                ),
                dict(
                    view=vanilla.TextBox("auto", "Drag Formation:"),
                    width="fill",
                    spacing=titleSpacing
                ),
                dict(
                    view=self.dragSourceFormationPopUp,
                    width="fill"
                )
            ],
            spacing=controlSpacing,
            alignment="leading"
        )

        # source

        self.dragSourceView = DraggingSourceView("auto")

        # drop settings

        self.dropOperation = "copy"

        self.dropDestOperationPopUp = vanilla.PopUpButton(
            "auto",
            dropOperationMap.keys(),
            callback=self.dropDestSettingsCallback
        )
        index = list(dropOperationMap).index(self.dropOperation)
        self.dropDestOperationPopUp.set(index)

        self.dropDestOnRowCheckBox = vanilla.CheckBox(
            "auto",
            title="Drop On Row",
            value=False,
            callback=self.dropDestSettingsCallback
        )
        self.dropDestBetweenRowsCheckBox = vanilla.CheckBox(
            "auto",
            title="Drop Between Rows",
            value=True,
            callback=self.dropDestSettingsCallback
        )

        self.dropDestSettingsStack = vanilla.VerticalStackView(
            "auto",
            views=[
                dict(
                    view=vanilla.TextBox("auto", "Drop Mode:"),
                    width="fill",
                    spacing=titleSpacing
                ),
                dict(
                    view=self.dropDestOperationPopUp,
                    width="fill"
                ),
                dict(
                    view=self.dropDestOnRowCheckBox,
                    width="fill",
                    spacing=titleSpacing
                ),
                dict(
                    view=self.dropDestBetweenRowsCheckBox,
                    width="fill",
                    spacing=titleSpacing
                )
            ],
            spacing=controlSpacing,
            alignment="leading"
        )

        # views

        dropSettings = dict(
            pasteboardTypes=["string"],
            dropCandidateCallback=self.dest1DropCandidateCallback,
            dropCandidateEndedCallback=self.dest1DropCandidateEndedCallback,
            dropCandidateExitedCallback=self.dest1DropCandidateExitedCallback,
            performDropCallback=self.dest1PerformDropCallback
        )
        self.dest1 = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.dest1.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.blackColor(),
            margins=0,
            cornerRadius=0
        )
        self.dest1.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "string"
        )
        self.dest1.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.redColor(),
            borderColor=AppKit.NSColor.redColor(),
            cornerRadius=0,
            margins=0
        )

        dropSettings = dict(
            pasteboardTypes=["plist"],
            dropCandidateCallback=self.dest2DropCandidateCallback,
            dropCandidateEndedCallback=self.dest2DropCandidateEndedCallback,
            dropCandidateExitedCallback=self.dest2DropCandidateExitedCallback,
            performDropCallback=self.dest2PerformDropCallback
        )
        self.dest2 = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.dest2.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.blackColor(),
            margins=0,
            cornerRadius=0
        )
        self.dest2.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "plist"
        )
        self.dest2.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.redColor(),
            borderColor=AppKit.NSColor.redColor(),
            cornerRadius=0,
            margins=0
        )

        dropSettings = dict(
            pasteboardTypes=["fileURL"],
            dropCandidateCallback=self.dest3DropCandidateCallback,
            dropCandidateEndedCallback=self.dest3DropCandidateEndedCallback,
            dropCandidateExitedCallback=self.dest3DropCandidateExitedCallback,
            performDropCallback=self.dest3PerformDropCallback
        )
        self.dest3 = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.dest3.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.blackColor(),
            margins=0,
            cornerRadius=0
        )
        self.dest3.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "files"
        )
        self.dest3.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.redColor(),
            borderColor=AppKit.NSColor.redColor(),
            cornerRadius=0,
            margins=0
        )

        # lists

        dropSettings = dict(
            pasteboardTypes=["string"],
            dropCandidateCallback=self.list1DropCandidateCallback,
            performDropCallback=self.list1PerformDropCallback
        )
        self.list1 = vanilla.List2(
            "auto",
            ["XXX", "YYY", "ZZZ"],
            dropSettings=dropSettings
        )

        columnDescriptions = [
            dict(
                identifier="letter",
                title="ABC"
            ),
            dict(
                identifier="number",
                title="#"
            )
        ]
        dropSettings = dict(
            pasteboardTypes=["plist"],
            dropCandidateCallback=self.list2DropCandidateCallback,
            performDropCallback=self.list2PerformDropCallback
        )
        self.list2 = vanilla.List2(
            "auto",
            [
                dict(
                    letter="XXX",
                    number=-1
                ),
                dict(
                    letter="YYY",
                    number=-2
                ),
                dict(
                    letter="ZZZ",
                    number=-3
                ),
            ],
            columnDescriptions=columnDescriptions,
            dropSettings=dropSettings
        )

        dropSettings = dict(
            pasteboardTypes=["fileURL"],
            dropCandidateCallback=self.list3DropCandidateCallback,
            performDropCallback=self.list3PerformDropCallback
        )
        self.list3 = vanilla.List2(
            "auto",
            [],
            dropSettings=dropSettings
        )

        # stacks

        self.topStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                dict(
                    view=self.dragSourceView,
                    width=100
                ),
                dict(
                    view=self.dragSourceSettingsStack,
                    width=200,
                ),
                dict(
                    view=self.dropDestSettingsStack,
                    width=200
                )
            ],
            spacing=20,
            alignment="leading"
        )

        self.viewStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                self.dest1,
                self.dest2,
                self.dest3
            ],
            spacing=20
        )

        self.listStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                self.list1,
                self.list2,
                self.list3
            ],
            spacing=20
        )

        self.w.stack = vanilla.VerticalStackView(
            "auto",
            views=[
                vanilla.TextBox(
                    "auto",
                    "Drag from the green block to one of "
                    "the destinations.\nOr drag files from "
                    "Finder to the file destinations."
                ),
                self.topStack,
                dict(
                    view=self.viewStack,
                    height=150
                ),
                dict(
                    view=self.listStack,
                    height=150
                ),
                vanilla.HorizontalLine("auto"),
                vanilla.TextBox("auto", "Drag within the list to reorder items."),
            ],
            spacing=20,
            alignment="leading"
        )

        rules = [
            "H:|-[stack]-|",
            "V:|-[stack]-|"
        ]
        self.w.addAutoPosSizeRules(rules)

        self.w.open()

    def dragSourceSettingsCallback(self, sender):
        count = self.dragSourceCountSlider.get()
        typ = self.dragSourceTypePopUp.get()
        typ = self.dragSourceTypePopUp.getItems()[typ]
        formation = self.dragSourceFormationPopUp.get()
        formation = self.dragSourceFormationPopUp.getItems()[formation]
        view = self.dragSourceView.getNSView()
        view.draggingItemCount = int(count)
        view.draggingFormation = formation
        view.draggingType = typ

    def dropDestSettingsCallback(self, sender):
        operations = self.dropDestOperationPopUp.getItems()
        index = self.dropDestOperationPopUp.get()
        self.dropOperation = operations[index]
        self.list1._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.list1._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()
        self.list2._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.list2._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()
        self.list3._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.list3._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()

    # view: string drop destination

    def dest1DropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "string"
        )
        location = info["location"]
        x, y = location
        self.dest1.locationBox.setPosSize((x-1, y-1, 2, 2))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.dest1.textBox.set(text)
        return self.dropOperation

    def dest1DropCandidateExitedCallback(self, info):
        self.dest1.textBox.set("drop exited")

    def dest1DropCandidateEndedCallback(self, info):
        self.dest1.textBox.set("drop ended")

    def dest1PerformDropCallback(self, info):
        print("dest1PerformDropCallback")
        return True

    # view: plist drop destination

    def dest2DropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "plist"
        )
        location = info["location"]
        x, y = location
        self.dest2.locationBox.setPosSize((x-1, y-1, 2, 2))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.dest2.textBox.set(text)
        return self.dropOperation

    def dest2DropCandidateExitedCallback(self, info):
        self.dest2.textBox.set("drop exited")

    def dest2DropCandidateEndedCallback(self, info):
        self.dest2.textBox.set("drop ended")

    def dest2PerformDropCallback(self, info):
        print("dest2PerformDropCallback")
        return True

    # view: files

    def dest3DropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "fileURL"
        )
        location = info["location"]
        x, y = location
        self.dest3.locationBox.setPosSize((x-1, y-1, 2, 2))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.dest3.textBox.set(text)
        return self.dropOperation
    
    def dest3DropCandidateExitedCallback(self, info):
        self.dest3.textBox.set("drop exited")
    
    def dest3DropCandidateEndedCallback(self, info):
        self.dest3.textBox.set("drop ended")
    
    def dest3PerformDropCallback(self, info):
        print("dest3PerformDropCallback")
        sender = info["sender"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "fileURL"
        )
        for item in items:
            print(item.path())
        return True

    # list: string

    def list1DropCandidateCallback(self, info):
        return "copy"
    
    def list1PerformDropCallback(self, info):
        sender = info["sender"]
        row = info["row"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        allItems = list(self.list1.get())
        items = allItems[:row] + items + allItems[row:]
        self.list1.set(items)
        return True

    # list: plist
    
    def list2DropCandidateCallback(self, info):
        return "copy"
    
    def list2PerformDropCallback(self, info):
        sender = info["sender"]
        row = info["row"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        allItems = list(self.list2.get())
        items = allItems[:row] + items + allItems[row:]
        self.list2.set(items)
        return True

    # list: file urls
    
    def list3DropCandidateCallback(self, info):
        existing = list(self.list3.get())
        sender = info["sender"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        items = [os.path.basename(item.path()) for item in items]
        items = [item for item in items if item not in existing]
        if not items:
            return "none"
        return "link"
    
    def list3PerformDropCallback(self, info):
        existing = list(self.list3.get())
        sender = info["sender"]
        row = info["row"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        items = [os.path.basename(item.path()) for item in items]
        items = [item for item in items if item not in existing]
        items = existing[:row] + items + existing[row:]
        self.list3.set(items)
        return True


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
