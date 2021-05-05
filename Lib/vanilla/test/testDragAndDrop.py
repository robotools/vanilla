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
        AppKit.NSColor.blackColor().set()
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
            (600, 300),
            "Dragon Drop"
        )

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
                    view=self.dragSourceTitle,
                    width="fill"
                ),
                dict(
                    view=self.dragSourceCountSlider,
                    width="fill"
                ),
                dict(
                    view=self.dragSourceTypePopUp,
                    width="fill"
                ),
                dict(
                    view=self.dragSourceFormationPopUp,
                    width="fill"
                )
            ],
            spacing=20,
            alignment="leading"
        )

        # source

        self.dragSourceView = DraggingSourceView("auto")

        # drop settings

        self.dropOperation = "copy"

        self.dropDestTitle = vanilla.TextBox(
            "auto",
            "Drop Details:"
        )
        self.dropDestOperationPopUp = vanilla.PopUpButton(
            "auto",
            dropOperationMap.keys(),
            callback=self.dropDestSettingsCallback
        )
        index = list(dropOperationMap).index(self.dropOperation)
        self.dropDestOperationPopUp.set(index)

        self.dropDestSettingsStack = vanilla.VerticalStackView(
            "auto",
            views=[
                dict(
                    view=self.dropDestTitle,
                    width="fill"
                ),
                dict(
                    view=self.dropDestOperationPopUp,
                    width="fill"
                )
            ],
            spacing=20,
            alignment="leading"
        )

        # destinations

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

        # stacks

        self.topStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                dict(
                    view=self.dragSourceSettingsStack,
                ),
                dict(
                    view=self.dragSourceView,
                    width=100
                ),
                dict(
                    view=self.dropDestSettingsStack
                )
            ],
            spacing=20
        )

        self.bottomStack = vanilla.HorizontalStackView(
            "auto",
            views=[
                self.dest1,
                self.dest2,
                self.dest3
            ],
            spacing=20
        )

        self.w.stack = vanilla.VerticalStackView(
            "auto",
            views=[
                self.topStack,
                dict(
                    view=self.bottomStack,
                    height=200
                )
            ],
            spacing=20
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

    # string drop destination

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

    # plist drop destination

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

    # files

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


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
