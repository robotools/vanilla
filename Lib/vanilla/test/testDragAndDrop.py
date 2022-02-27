import os
import objc
import AppKit
import vanilla
from vanilla.dragAndDrop import dropOperationMap



# ----
# Test
# ----

objc.options.verbose = True

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
    shadow = AppKit.NSShadow.alloc().init()
    shadow.setShadowOffset_((0, -5))
    shadow.setShadowBlurRadius_(5)
    shadow.setShadowColor_(AppKit.NSColor.blackColor())
    shadow.set()
    text = AppKit.NSAttributedString.alloc().initWithString_attributes_(
        "🐲",
        {
            AppKit.NSFontAttributeName : AppKit.NSFont.systemFontOfSize_(40),
            AppKit.NSShadowAttributeName : shadow
        }
    )
    text.drawAtPoint_((3, 3))
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
            y = height * i * 0.1
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


titleSpacing = 5
controlSpacing = 10

class Test:

    def __init__(self):
        self.w = vanilla.Window(
            (600, 1),
            "Drag and Drop Test"
        )

        self.makeMainSource()
        self.makeDestViews()
        self.makeDestLists()

        self.w.stack = vanilla.VerticalStackView(
            "auto",
            views=[
                vanilla.TextBox(
                    "auto",
                    "Drag from the green block to one of "
                    "the yellow blocks or lists."
                    "\n"
                    "Drag files from Finder to the file "
                    "yellow block or the list."
                    "\n"
                    "The string list is reorderable."
                ),
                dict(
                    view=self.mainSourceStack,
                    width="fill"
                ),
                dict(
                    view=self.destViewViewStack,
                    height=150,
                    width="fill"
                ),
                dict(
                    view=self.destViewListStack,
                    height=150,
                    width="fill"
                ),
                # vanilla.HorizontalLine("auto"),
                # vanilla.TextBox("auto", "Drag within the list to reorder items."),
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

    def makeMainSource(self):
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
        self.mainSourceStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                dict(
                    view=self.dragSourceView,
                    width=100
                ),
                dict(
                    view=self.dragSourceSettingsStack,

                ),
                dict(
                    view=self.dropDestSettingsStack,

                )
            ],
            spacing=20,
            alignment="leading"
        )

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
        self.stringDestList._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.stringDestList._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()
        self.plistDestList._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.plistDestList._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()
        self.fileURLDestList._allowDropOnRow = self.dropDestOnRowCheckBox.get()
        self.fileURLDestList._allowDropBetweenRows = self.dropDestBetweenRowsCheckBox.get()

    # Destination Views
    # -----------------

    def makeDestViews(self):
        dropSettings = dict(
            pasteboardTypes=["string"],
            dropCandidateEnteredCallback=self.stringDestViewDropCandidateEnteredCallback,
            dropCandidateCallback=self.stringDestViewDropCandidateCallback,
            dropCandidateEndedCallback=self.stringDestViewDropCandidateEndedCallback,
            dropCandidateExitedCallback=self.stringDestViewDropCandidateExitedCallback,
            performDropCallback=self.stringDestViewPerformDropCallback
        )
        self.stringDestView = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.stringDestView.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.greenColor(),
            borderWidth=0,
            margins=0,
            cornerRadius=0
        )
        self.stringDestView.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "drop: string"
        )
        self.stringDestView.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.clearColor(),
            borderColor=AppKit.NSColor.redColor(),
            borderWidth=1,
            cornerRadius=10,
            margins=0
        )
        self.stringDestView.locationBox.show(False)

        dropSettings = dict(
            pasteboardTypes=["plist"],
            dropCandidateEnteredCallback=self.plistDestViewDropCandidateEnteredCallback,
            dropCandidateCallback=self.plistDestViewDropCandidateCallback,
            dropCandidateEndedCallback=self.plistDestViewDropCandidateEndedCallback,
            dropCandidateExitedCallback=self.plistDestViewDropCandidateExitedCallback,
            performDropCallback=self.plistDestViewPerformDropCallback
        )
        self.plistDestView = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.plistDestView.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.blackColor(),
            margins=0,
            cornerRadius=0
        )
        self.plistDestView.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "drop: plist"
        )
        self.plistDestView.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.clearColor(),
            borderColor=AppKit.NSColor.redColor(),
            borderWidth=1,
            cornerRadius=10,
            margins=0
        )
        self.plistDestView.locationBox.show(False)

        dropSettings = dict(
            pasteboardTypes=["fileURL"],
            dropCandidateEnteredCallback=self.fileURLDestViewDropCandidateEnteredCallback,
            dropCandidateCallback=self.fileURLDestViewDropCandidateCallback,
            dropCandidateEndedCallback=self.fileURLDestViewDropCandidateEndedCallback,
            dropCandidateExitedCallback=self.fileURLDestViewDropCandidateExitedCallback,
            performDropCallback=self.fileURLDestViewPerformDropCallback
        )
        self.fileURLDestView = vanilla.Group(
            "auto",
            dropSettings=dropSettings
        )
        self.fileURLDestView.box = vanilla.Box(
            (0, 0, 0, 0),
            fillColor=AppKit.NSColor.yellowColor(),
            borderColor=AppKit.NSColor.blackColor(),
            margins=0,
            cornerRadius=0
        )
        self.fileURLDestView.textBox = vanilla.TextBox(
            (20, 20, 0, 0),
            "drop: files"
        )
        self.fileURLDestView.locationBox = vanilla.Box(
            (0, 0, 2, 2),
            fillColor=AppKit.NSColor.clearColor(),
            borderColor=AppKit.NSColor.redColor(),
            borderWidth=1,
            cornerRadius=10,
            margins=0
        )
        self.fileURLDestView.locationBox.show(False)

        self.destViewViewStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                self.stringDestView,
                self.plistDestView,
                dict(
                    view=vanilla.VerticalLine("auto"),
                    height="fill",
                    width=1
                ),
                self.fileURLDestView
            ],
            spacing=20
        )

    # string

    def stringDestViewDropCandidateEnteredCallback(self, info):
        self.stringDestView.box.setBorderColor(AppKit.NSColor.greenColor())
        self.stringDestView.box.setBorderWidth(20)
        self.stringDestView.locationBox.show(True)
        return self.dropOperation

    def stringDestViewDropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "string"
        )
        location = info["location"]
        x, y = location
        self.stringDestView.locationBox.setPosSize((x-10, y-10, 20, 20))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.stringDestView.textBox.set(text)
        return self.dropOperation

    def stringDestViewDropCandidateExitedCallback(self, info):
        self.stringDestView.box.setBorderColor(AppKit.NSColor.orangeColor())
        self.stringDestView.locationBox.show(False)

    def stringDestViewDropCandidateEndedCallback(self, info):
        self.stringDestView.box.setBorderWidth(0)
        self.stringDestView.locationBox.show(False)
        self.stringDestView.textBox.set("drop: string")

    def stringDestViewPerformDropCallback(self, info):
        print("dest1PerformDropCallback")
        return True

    # plist

    def plistDestViewDropCandidateEnteredCallback(self, info):
        self.plistDestView.box.setBorderColor(AppKit.NSColor.greenColor())
        self.plistDestView.box.setBorderWidth(20)
        self.plistDestView.locationBox.show(True)
        return self.dropOperation

    def plistDestViewDropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "plist"
        )
        location = info["location"]
        x, y = location
        self.plistDestView.locationBox.setPosSize((x-10, y-10, 20, 20))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.plistDestView.textBox.set(text)
        return self.dropOperation

    def plistDestViewDropCandidateExitedCallback(self, info):
        self.plistDestView.box.setBorderColor(AppKit.NSColor.orangeColor())
        self.plistDestView.locationBox.show(False)

    def plistDestViewDropCandidateEndedCallback(self, info):
        self.plistDestView.box.setBorderWidth(0)
        self.plistDestView.locationBox.show(False)
        self.plistDestView.textBox.set("drop: string")

    def plistDestViewPerformDropCallback(self, info):
        print("dest2PerformDropCallback")
        return True

    # file urls

    def fileURLDestViewDropCandidateEnteredCallback(self, info):
        self.fileURLDestView.box.setBorderColor(AppKit.NSColor.greenColor())
        self.fileURLDestView.box.setBorderWidth(20)
        self.fileURLDestView.locationBox.show(True)
        return self.dropOperation

    def fileURLDestViewDropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getDropItemValues(
            items,
            "fileURL"
        )
        location = info["location"]
        x, y = location
        self.fileURLDestView.locationBox.setPosSize((x-10, y-10, 20, 20))
        text = (
            f"count={len(items)}",
            f"items={repr(items)}",
            f"source={source.__class__.__name__}"
        )
        text = "\n".join(text)
        self.fileURLDestView.textBox.set(text)
        return self.dropOperation

    def fileURLDestViewDropCandidateExitedCallback(self, info):
        self.fileURLDestView.box.setBorderColor(AppKit.NSColor.orangeColor())
        self.fileURLDestView.locationBox.show(False)

    def fileURLDestViewDropCandidateEndedCallback(self, info):
        self.fileURLDestView.box.setBorderWidth(0)
        self.fileURLDestView.locationBox.show(False)
        self.fileURLDestView.textBox.set("drop: files")

    def fileURLDestViewPerformDropCallback(self, info):
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

    # Destination Lists
    # -----------------

    def makeDestLists(self):
        dragSettings = dict(
            makeDragDataCallback=self.stringDestListMakeDragDataCallback
        )
        dropSettings = dict(
            pasteboardTypes=[
                "string",
                "dev.robotools.test.stringDestListIndexes"
            ],
            dropCandidateEnteredCallback=self.stringDestListDropCandidateEnteredCallback,
            dropCandidateEndedCallback=self.stringDestListDropCandidateEndedCallback,
            dropCandidateExitedCallback=self.stringDestListDropCandidateExitedCallback,
            dropCandidateCallback=self.stringDestListDropCandidateCallback,
            performDropCallback=self.stringDestListPerformDropCallback
        )
        self.stringDestList = vanilla.List2(
            "auto",
            ["XXX", "YYY", "ZZZ"],
            dragSettings=dragSettings,
            dropSettings=dropSettings
        )

        columnDescriptions = [
            dict(
                identifier="letter",
                title="ABC",
                width=35
            ),
            dict(
                identifier="number",
                title="#",
                width=35
            )
        ]
        dragSettings = dict(
            makeDragDataCallback=self.plistDestListMakeDragDataCallback
        )
        dropSettings = dict(
            pasteboardTypes=["plist"],
            dropCandidateEnteredCallback=self.plistDestListDropCandidateEnteredCallback,
            dropCandidateEndedCallback=self.plistDestListDropCandidateEndedCallback,
            dropCandidateExitedCallback=self.plistDestListDropCandidateExitedCallback,
            dropCandidateCallback=self.plistDestListDropCandidateCallback,
            performDropCallback=self.plistDestListPerformDropCallback
        )
        self.plistDestList = vanilla.List2(
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
            dragSettings=dragSettings,
            dropSettings=dropSettings
        )

        dropSettings = dict(
            pasteboardTypes=["fileURL"],
            dropCandidateCallback=self.fileURLDestListDropCandidateCallback,
            performDropCallback=self.fileURLDestListPerformDropCallback
        )
        self.fileURLDestList = vanilla.List2(
            "auto",
            [],
            dropSettings=dropSettings
        )

        self.destViewListStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                self.stringDestList,
                self.plistDestList,
                dict(
                    view=vanilla.VerticalLine("auto"),
                    height="fill",
                    width=1
                ),
                self.fileURLDestList
            ],
            spacing=20
        )

    # string

    def stringDestListDropCandidateEnteredCallback(self, info):
        self.stringDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.greenColor()
        )
        return "generic"

    def stringDestListDropCandidateExitedCallback(self, info):
        self.stringDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.orangeColor()
        )

    def stringDestListDropCandidateEndedCallback(self, info):
        self.stringDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.whiteColor()
        )

    def stringDestListMakeDragDataCallback(self, index):
        typesAndValues = {
            "string" : self.stringDestList.get()[index],
            "dev.robotools.test.stringDestListIndexes" : index
        }
        return typesAndValues

    def stringDestListDropCandidateCallback(self, info):
        source = info["source"]
        if source == self.stringDestList:
            return "move"
        return "copy"

    def stringDestListPerformDropCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        index = info["index"]
        items = info["items"]
        # reorder
        if source == self.stringDestList:
            indexes = sender.getDropItemValues(items, "dev.robotools.test.stringDestListIndexes")
            # XXX this is wrong
            items = list(self.stringDestList.get())
            move = [items.pop(i) for i in indexes]
            # insert
            if index is not None:
                items[index:index] = move
            # append
            else:
                items += move
        else:
            items = sender.getDropItemValues(items, "string")
            allItems = list(self.stringDestList.get())
            # insert
            if index is not None:
                items = allItems[:index] + items + allItems[index:]
            # append
            else:
                items = allItems + items
        self.stringDestList.set(items)
        return True

    # plist

    def plistDestListDropCandidateEnteredCallback(self, info):
        self.plistDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.greenColor()
        )
        return "generic"

    def plistDestListDropCandidateExitedCallback(self, info):
        self.plistDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.orangeColor()
        )

    def plistDestListDropCandidateEndedCallback(self, info):
        self.plistDestList.getNSScrollView().setBackgroundColor_(
            AppKit.NSColor.whiteColor()
        )

    def plistDestListMakeDragDataCallback(self, index):
        typesAndValues = {
            "plist" : self.plistDestList.get()[index]
        }
        return typesAndValues

    def plistDestListDropCandidateCallback(self, info):
        source = info["source"]
        if source == self.plistDestList:
            return "none"
        return "copy"

    def plistDestListPerformDropCallback(self, info):
        sender = info["sender"]
        index = info["index"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        allItems = list(self.plistDestList.get())
        items = allItems[:index] + items + allItems[index:]
        self.plistDestList.set(items)
        return True

    # file urls

    def fileURLDestListDropCandidateCallback(self, info):
        existing = list(self.fileURLDestList.get())
        sender = info["sender"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        items = [os.path.basename(item.path()) for item in items]
        items = [item for item in items if item not in existing]
        if not items:
            return "none"
        return "link"

    def fileURLDestListPerformDropCallback(self, info):
        existing = list(self.fileURLDestList.get())
        sender = info["sender"]
        index = info["index"]
        items = info["items"]
        items = sender.getDropItemValues(items)
        items = [os.path.basename(item.path()) for item in items]
        items = [item for item in items if item not in existing]
        if index is not None:
            items = existing[:index] + items + existing[index:]
        self.fileURLDestList.set(items)
        return True


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
