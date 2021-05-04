import objc
import AppKit
import vanilla

objc.setVerbose(True)

# -----------------
# Vanilla Additions
# -----------------

# Dragging Source

draggingFormationMap = dict(
    default=AppKit.NSDraggingFormationDefault,
    none=AppKit.NSDraggingFormationNone,
    pile=AppKit.NSDraggingFormationPile,
    stack=AppKit.NSDraggingFormationStack,
    list=AppKit.NSDraggingFormationList
)

pasteboardTypeMap = dict(
    string=AppKit.NSPasteboardTypeString,
    plist="dev.robotools.vanilla.propertyList"
)

def startDraggingSession(
        view,
        event,
        items,
        source=None,
        formation="default",
        location=(0, 0)
    ):
    if isinstance(view, vanilla.VanillaBaseObject):
        view = view._getContentView()
    if source is None:
        source = view
    draggingItems = []
    for item in items:
        if "location" not in item:
            item["location"] = location
        draggingItem = makeDraggingItem(**item)
        draggingItems.append(draggingItem)
    session = view.beginDraggingSessionWithItems_event_source_(
        draggingItems,
        event,
        source
    )
    formation = draggingFormationMap.get(formation, formation)
    session.setDraggingFormation_(formation)
    return session

def makeDraggingItem(
        typesAndValues,
        location=(0, 0),
        size=(50, 50),
        image=None
    ):
    pasteboardItem = AppKit.NSPasteboardItem.alloc().init()
    for pasteboardType, value in typesAndValues.items():
        pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
        if isinstance(value, bytes):
            pasteboardItem.setData_forType_(value, pasteboardType)
        elif isinstance(value, dict):
            pasteboardItem.setPropertyList_forType_(value, pasteboardType)
        else:
            pasteboardItem.setString_forType_(value, pasteboardType)
    draggingItem = AppKit.NSDraggingItem.alloc().initWithPasteboardWriter_(pasteboardItem)
    draggingItem.setDraggingFrame_contents_(
        (location, size),
        image
    )
    return draggingItem


# Drop Target

dragOperationMap = dict(
    none=AppKit.NSDragOperationNone,
    copy=AppKit.NSDragOperationCopy,
    link=AppKit.NSDragOperationLink,
    generic=AppKit.NSDragOperationGeneric,
    private=AppKit.NSDragOperationPrivate,
    move=AppKit.NSDragOperationMove,
    delete=AppKit.NSDragOperationDelete,
    drag=AppKit.NSDragOperationEvery
)

class DropTargetProtocol:

    """
    - NSView subclass must implement the NSDraggingDestination protocol
    - NSView subclass calls vanillaWrapper().<DropTargetMixIn method>
    - DropTargetMixIn calls the external callbacks
    """

    # Drop Setup

    _dropCandidateCallback = None
    _dropCandidateEnteredCallback = None
    _dropCandidateUpdatedCallback = None
    _dropCandidateEndedCallback = None
    _dropCandidateExitedCallback = None
    _prepareForDropCallback = None
    _performDropCallback = None
    _finishDropCallback = None

    def setDropSettings(self, settings):
        pasteboardTypes = settings.get("pasteboardTypes")
        performDropCallback = settings.get("performDropCallback")
        assert pasteboardTypes is not None
        assert performDropCallback is not None
        self._registerDropTypes(pasteboardTypes)
        self._dropCandidateCallback = settings.get("dropCandidateCallback")
        self._dropCandidateEnteredCallback = settings.get("dropCandidateEnteredCallback")
        self._dropCandidateUpdatedCallback = settings.get("dropCandidateUpdatedCallback")
        self._dropCandidateEndedCallback = settings.get("dropCandidateEndedCallback")
        self._dropCandidateExitedCallback = settings.get("dropCandidateExitedCallback")
        self._prepareForDropCallback = settings.get("prepareForDropCallback")
        self._performDropCallback = performDropCallback
        self._finishDropCallback = settings.get("finishDropCallback")

    def _registerDropTypes(self, pasteboardTypes):
        view = self._getContentView()
        unwrapped = []
        for pasteboardType in pasteboardTypes:
            pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
            unwrapped.append(pasteboardType)
        view.registerForDraggedTypes_(unwrapped)

    def getItemValues(self, items, pasteboardType):
        """
        The drag protocol could also have a method for
        getting the python objects without round tripping
        through property list.
        """
        pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
        values = []
        for item in items:
            value = item.propertyListForType_(pasteboardType)
            values.append(value)
        return values

    # Drop Candidate

    def _dropCandidateCallbackCaller(self, draggingInfo, callback, draggingEvent):
        if callback is None:
            callback = self._dropCandidateCallback
        if callback is None:
            value = "none"
        else:
            info = self._unpackDropCandidateInfo(draggingInfo)
            info["draggingEvent"] = draggingEvent
            value = callback(info)
        return value

    def _unpackDropCandidateInfo(self, draggingInfo):
        source = draggingInfo.draggingSource()
        if hasattr(source, "vanillaWrapper"):
            source = source.vanillaWrapper()
        pasteboard = draggingInfo.draggingPasteboard()
        items = pasteboard.pasteboardItems()
        x, y = self._nsObject.convertPoint_fromView_(
            draggingInfo.draggingLocation(),
            None
        )
        w, h = self._nsObject.frame().size
        location = (x, h - y)
        info = dict(
            sender=self,
            source=source,
            items=items,
            location=location,
            draggingInfo=draggingInfo
        )
        return info

    def dropCandidateEntered(self, draggingInfo):
        operation = self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateEnteredCallback,
            draggingEvent="entered"
        )
        return dragOperationMap.get(operation, operation)

    def dropCandidateUpdated(self, draggingInfo):
        operation = self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateUpdatedCallback,
            draggingEvent="updated"
        )
        return dragOperationMap.get(operation, operation)

    def dropCandidateEnded(self, draggingInfo):
        self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateEndedCallback,
            draggingEvent="ended"
        )

    def dropCandidateExited(self, draggingInfo):
        self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateExitedCallback,
            draggingEvent="exited"
        )

    def updateDropCandidateImages(self, draggingInfo):
        """
        XXX

        I'm not sure how enumerateDraggingItemsWithOptions_forView_classes_searchOptions_usingBlock_
        works.

        What I'd like to do in the callback:
        - have a method for getting (item, image) pairs
          for items on the pasteboard with a given type
        - return a list of (item, image [or None]) pairs
        Then use the enumerator to update the images.
        """
        # def imageEnumerator(draggingItem, index, stop):
        #     xxx
        #     print(index)
        #     pass
        # draggingInfo.enumerateDraggingItemsWithOptions_forView_classes_searchOptions_usingBlock_(
        #     AppKit.NSDraggingItemEnumerationConcurrent,
        #     self._getContentView(),
        #     None,
        #     None,
        #     imageEnumerator
        # )
        # print("updateDropCandidateImages")

    # Drop Operation

    def _dropOperationCallbackCaller(self, draggingInfo, callback, draggingEvent):
        if callback is None:
            callback = self._dropCandidateCallback
        if callback is None:
            value = "none"
        else:
            info = self._unpackDropCandidateInfo(draggingInfo)
            info["draggingEvent"] = draggingEvent
            value = callback(info)
        return value

    def prepareForDrop(self, draggingInfo):
        if self._prepareForDropCallback is None:
            return True
        info = self._unpackDropCandidateInfo(draggingInfo)
        return self._prepareForDropCallback(info)

    def performDrop(self, draggingInfo):
        info = self._unpackDropCandidateInfo(draggingInfo)
        return self._performDropCallback(info)

    def finishDrop(self, draggingInfo):
        if self._finishDropCallback is None:
            return True
        info = self._unpackDropCandidateInfo(draggingInfo)
        self._finishDropCallback(info)


class VanillaGroupView(AppKit.NSView):

    def draggingEntered_(self, draggingInfo):
        return self.vanillaWrapper().dropCandidateEntered(draggingInfo)

    def draggingUpdated_(self, draggingInfo):
        return self.vanillaWrapper().dropCandidateUpdated(draggingInfo)

    @objc.signature(b"Z@:@")  # PyObjC bug? <- Found in the FontGoogles source.
    def draggingEnded_(self, draggingInfo):
        return self.vanillaWrapper().dropCandidateEnded(draggingInfo)

    def draggingExited_(self, draggingInfo):
        return self.vanillaWrapper().dropCandidateExited(draggingInfo)

    def updateDraggingItemsForDrag_(self, draggingInfo):
        return self.vanillaWrapper().updateDropCandidateImages(draggingInfo)

    def prepareForDragOperation_(self, draggingInfo):
        return self.vanillaWrapper().prepareForDrop(draggingInfo)

    def performDragOperation_(self, draggingInfo):
        return self.vanillaWrapper().performDrop(draggingInfo)

    def concludeDragOperation_(self, draggingInfo):
        return self.vanillaWrapper().finishDrop(draggingInfo)


class Group2(vanilla.Group, DropTargetProtocol):

    nsViewClass = VanillaGroupView

    def __init__(self, posSize, dropSettings=None):
        super().__init__(posSize)
        if dropSettings is not None:
            self.setDropSettings(dropSettings)

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
                location=location,
                size=image.size()
            )
            items.append(item)
        startDraggingSession(
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
            dragOperationMap.keys(),
            callback=self.dropDestSettingsCallback
        )
        index = list(dragOperationMap).index(self.dropOperation)
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
        self.dest1 = Group2(
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
        self.dest2 = Group2(
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

        self.dest3 = Group2("auto")
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
        items = sender.getItemValues(
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

    # plist drop destination
    
    def dest2DropCandidateCallback(self, info):
        sender = info["sender"]
        source = info["source"]
        items = info["items"]
        items = sender.getItemValues(
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


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
