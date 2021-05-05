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
    plist="dev.robotools.vanilla.propertyList",
    fileURL=AppKit.NSPasteboardTypeFileURL
)

def startDraggingSession(
        view,
        event,
        items,
        source=None,
        formation="default",
        location=None
    ):
    """
    Start a dragging session.

    `view` The view that is initiating the session.
    This may be a vanilla object or an instance of NSView.

    `event` The mouse event that is initiating the session.

    `items` A list of item definition dictionaries.

    - `typesAndValues` A dictionary of pasteboard types
      as keys and the object value for the type as the value.
    - `location` The location within the source view from
      which the dragging image should originate. Optional.
    - `size` The size to display the dragging image. Optional.
    - `image` An image previewing the item. Optional.

    `source` A source for the dragging data if it is something
    other than the view that initiated the session. Optional.

    `formation` The formation of the dragging images. Options:

    - "default"
    - "none"
    - "pile"
    - "stack"
    - "list"

    `location` A fallback in case `location` is not defined in
    an item dictionary. Optional.
    """
    if isinstance(view, vanilla.VanillaBaseObject):
        view = view._getContentView()
    if source is None:
        source = view
    draggingItems = []
    if location is None:
        rect = view.visibleRect()
        x = AppKit.NSMidX(rect)
        y = AppKit.NSMidY(rect)
        location = (x, y)
    for item in items:
        if "location" not in item:
            item["location"] = location
        draggingItem = _makeDraggingItem(**item)
        draggingItems.append(draggingItem)
    session = view.beginDraggingSessionWithItems_event_source_(
        draggingItems,
        event,
        source
    )
    formation = draggingFormationMap.get(formation, formation)
    session.setDraggingFormation_(formation)
    return session

def _makeDraggingItem(
        typesAndValues,
        location=(0, 0),
        size=None,
        image=None
    ):
    pasteboardItem = AppKit.NSPasteboardItem.alloc().init()
    for pasteboardType, value in typesAndValues.items():
        pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
        if isinstance(value, bytes):
            pasteboardItem.setData_forType_(value, pasteboardType)
        elif isinstance(value, str):
            pasteboardItem.setString_forType_(value, pasteboardType)
        else:
            pasteboardItem.setPropertyList_forType_(value, pasteboardType)
    if size is None:
        if image is not None:
            size = image.size()
        else:
            size = (20, 20)
    draggingItem = AppKit.NSDraggingItem.alloc().initWithPasteboardWriter_(pasteboardItem)
    draggingItem.setDraggingFrame_contents_(
        (location, size),
        image
    )
    return draggingItem


# Drop Target

dropOperationMap = dict(
    none=AppKit.NSDragOperationNone,
    copy=AppKit.NSDragOperationCopy,
    link=AppKit.NSDragOperationLink,
    generic=AppKit.NSDragOperationGeneric,
    private=AppKit.NSDragOperationPrivate,
    move=AppKit.NSDragOperationMove,
    delete=AppKit.NSDragOperationDelete,
    drag=AppKit.NSDragOperationEvery
)

class DropTargetProtocolMixIn:

    """
    # Drop Settings

    `pasteboardTypes`

    A list of `NSPasteboardType` values, convenience values
    or custom strings defining the pasteboard types this
    view will accept during drops.

    - "string"
    - "plist"

    `dropCandidateCallback`

    Optional. A method that will be called when one of the
    other `dropCandidate` callbacks is not defined. This must
    return one of the drop operations listed below.

    `dropCandidateEnteredCallback`

    Optional. A method that will be called when a drag
    operation enters the view. This must return one of
    the drop operations listed below.

    `dropCandidateUpdatedCallback`

    Optional. A method that will be called when a drag
    operation updates within the view. This must return
    one of the drop operations listed below.

    `dropCandidateExitedCallback`

    Optional. A method that will be called when a drag
    operation exits the view.

    `dropCandidateEndedCallback`

    Optional. A method that will be called when a drag
    operation that previously entered the view ends.

    `prepareForDropCallback`

    Optional. A method that will be called at the start of
    a drop. This should not drop the incoming data. This
    must return a boolean indicating if the drop is acceptable.

    `performDropCallback`

    A method that will be called when the drop is performed.
    This must return a boolean indicating if the drop was accepted.

    `finishDropCallback`

    Optional. A method that will be called after the drop has
    been performed.

    ## Drop Operations:

    These define the drop operation that the view will
    perform if the drop candidate is actually dropped.

    - "none"
    - "copy"
    - "link"
    - "generic"
    - "private"
    - "move"
    - "delete"
    - "drag"

    ## Dragging Info

    The callbacks will be sent a single `draggingInfo` argument.
    The value of this will be a dict with these key/value pairs:

    - `sender` The vanilla wrapper of the view being targeted
      for the drop.
    - `source` The source view that initiated the dragging operation.
      If this view is wrapped by vanilla, the vanilla wrapper
      will be given as the source.
    - `items` The list of NSPasteboardItem objects. Use the
      `getDropItemValues` method to unpack these to Python objects.
    - `location` The location of the drop.
    - `draggingInfo` The underlying NSDraggingInfo object.
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

    def getDropItemValues(self, items, pasteboardType=None):
        """
        Get Python objects from the given NSPasteboardItem
        objects for the given pasteboard type. If this view
        is registered for only one pasteboard type, None may
        be given as the pasteboard type.
        """
        if pasteboardType is None:
            pasteboardTypes = self._getContentView().registeredDraggedTypes()
            assert len(pasteboardTypes) == 1
            pasteboardType = pasteboardTypes[0]
        pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
        values = []
        for item in items:
            if pasteboardType == AppKit.NSPasteboardTypeFileURL:
                value = item.stringForType_(pasteboardType)
                value = AppKit.NSURL.URLWithString_(value)
            else:
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

    def _dropCandidateEntered(self, draggingInfo):
        operation = self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateEnteredCallback,
            draggingEvent="entered"
        )
        return dropOperationMap.get(operation, operation)

    def _dropCandidateUpdated(self, draggingInfo):
        operation = self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateUpdatedCallback,
            draggingEvent="updated"
        )
        return dropOperationMap.get(operation, operation)

    def _dropCandidateEnded(self, draggingInfo):
        self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateEndedCallback,
            draggingEvent="ended"
        )

    def _dropCandidateExited(self, draggingInfo):
        self._dropCandidateCallbackCaller(
            draggingInfo,
            self._dropCandidateExitedCallback,
            draggingEvent="exited"
        )

    def _updateDropCandidateImages(self, draggingInfo):
        """
        XXX

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

    def _prepareForDrop(self, draggingInfo):
        if self._prepareForDropCallback is None:
            return True
        info = self._unpackDropCandidateInfo(draggingInfo)
        return self._prepareForDropCallback(info)

    def _performDrop(self, draggingInfo):
        info = self._unpackDropCandidateInfo(draggingInfo)
        return self._performDropCallback(info)

    def _finishDrop(self, draggingInfo):
        if self._finishDropCallback is None:
            return
        info = self._unpackDropCandidateInfo(draggingInfo)
        self._finishDropCallback(info)


# --------------------
# vanilla.Group update
# --------------------

class VanillaGroupView(AppKit.NSView):

    # ------------------------------------
    # Start dragging destination protocol.
    #
    # If this is changed, it must be changed
    # in all other classes where this code has
    # been duplicated

    def draggingEntered_(self, draggingInfo):
        return self.vanillaWrapper()._dropCandidateEntered(draggingInfo)

    def draggingUpdated_(self, draggingInfo):
        return self.vanillaWrapper()._dropCandidateUpdated(draggingInfo)

    @objc.signature(b"Z@:@") # PyObjC bug? <- Found in the FontGoogles source.
    def draggingEnded_(self, draggingInfo):
        return self.vanillaWrapper()._dropCandidateEnded(draggingInfo)

    def draggingExited_(self, draggingInfo):
        return self.vanillaWrapper()._dropCandidateExited(draggingInfo)

    def updateDraggingItemsForDrag_(self, draggingInfo):
        return self.vanillaWrapper()._updateDropCandidateImages(draggingInfo)

    def prepareForDragOperation_(self, draggingInfo):
        return self.vanillaWrapper()._prepareForDrop(draggingInfo)

    def performDragOperation_(self, draggingInfo):
        return self.vanillaWrapper()._performDrop(draggingInfo)

    def concludeDragOperation_(self, draggingInfo):
        return self.vanillaWrapper()._finishDrop(draggingInfo)

    # End dragging destination protocol.
    # ----------------------------------


class Group2(vanilla.Group, DropTargetProtocolMixIn):

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
                location=location
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

        dropSettings = dict(
            pasteboardTypes=["fileURL"],
            dropCandidateCallback=self.dest3DropCandidateCallback,
            dropCandidateEndedCallback=self.dest3DropCandidateEndedCallback,
            dropCandidateExitedCallback=self.dest3DropCandidateExitedCallback,
            performDropCallback=self.dest3PerformDropCallback
        )
        self.dest3 = Group2(
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
