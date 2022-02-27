import objc
import AppKit
from vanilla.vanillaBase import VanillaBaseObject

# Dragging Source

draggingFormationMap = dict(
    default=AppKit.NSDraggingFormationDefault,
    none=AppKit.NSDraggingFormationNone,
    pile=AppKit.NSDraggingFormationPile,
    stack=AppKit.NSDraggingFormationStack,
    list=AppKit.NSDraggingFormationList
)
try:
    NSPasteboardTypeFileURL = AppKit.NSPasteboardTypeFileURL
except AttributeError:
    NSPasteboardTypeFileURL = "public.file-url"

pasteboardTypeMap = dict(
    string=AppKit.NSPasteboardTypeString,
    plist="dev.robotools.vanilla.propertyList",
    fileURL=NSPasteboardTypeFileURL
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
      Acceptable value types are strings, bytes and any python
      object structure that can be represented as a Property List.
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
    if isinstance(view, VanillaBaseObject):
        view = view._nsObject
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

def makePasteboardItem(typesAndValues):
    pasteboardItem = AppKit.NSPasteboardItem.alloc().init()
    for pasteboardType, value in typesAndValues.items():
        pasteboardType = pasteboardTypeMap.get(pasteboardType, pasteboardType)
        if isinstance(value, bytes):
            pasteboardItem.setData_forType_(value, pasteboardType)
        elif isinstance(value, str):
            pasteboardItem.setString_forType_(value, pasteboardType)
        else:
            pasteboardItem.setPropertyList_forType_(value, pasteboardType)
    return pasteboardItem

def _makeDraggingItem(
        typesAndValues,
        location=(0, 0),
        size=None,
        image=None
    ):
    pasteboardItem = makePasteboardItem(typesAndValues)
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
    - "fileURL"

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

    def _getDropView(self):
        return self._nsObject

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
        view = self._getDropView()
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
            pasteboardTypes = self._getDropView().registeredDraggedTypes()
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
        x, y = self._getDropView().convertPoint_fromView_(
            draggingInfo.draggingLocation(),
            None
        )
        w, h = self._getDropView().frame().size
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
