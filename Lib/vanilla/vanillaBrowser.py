"""
This is adapted from the PyObjC PythonBrowser demo.
I beleive that demo was written by Just van Rossum.
"""

import AppKit
from objc import python_method
from operator import getitem, setitem

import inspect

from vanilla.vanillaBase import VanillaBaseObject
from vanilla.nsSubclasses import getNSSubclass

import warnings
warnings.filterwarnings("ignore", category=UserWarning)

TYPE_COLUMN_MAP = {
    "list" : "List",
    "dict" : "Dict",
    "NoneType" : "None",
    "instance" : "",
    "int" : "Integer",
    "float" : "Float",
    "str" : "String",
    "instancemethod" : "Method"
}

class ObjectBrowser(VanillaBaseObject):

    """
    An object browser.

    **posSize** Tuple of form *(left, top, width, height)* or *"auto"* representing the position and
    size of the browser.

    **obj** The object to be displayed.
    """

    def __init__(self, posSize, obj):
        self._model = PythonBrowserModel.alloc().initWithObject_(obj)

        self._posSize = posSize

        self._nsObject = getNSSubclass("NSScrollView")(self)
        self._nsObject.setAutohidesScrollers_(True)
        self._nsObject.setHasHorizontalScroller_(True)
        self._nsObject.setHasVerticalScroller_(True)
        self._nsObject.setBorderType_(AppKit.NSBezelBorder)
        self._nsObject.setDrawsBackground_(True)

        self._outlineView = getNSSubclass("NSOutlineView")(self)
        self._outlineView.setFrame_(((0, 0), (100, 100)))
        self._outlineView.setUsesAlternatingRowBackgroundColors_(True)
        self._outlineView.setAllowsColumnResizing_(True)
        self._outlineView.setRowHeight_(17.0)

        self._outlineView.setColumnAutoresizingStyle_(AppKit.NSTableViewUniformColumnAutoresizingStyle)
        columns = [
            ("name", "Name"),
            ("type", "Type"),
            ("value", "Value"),
            ("arguments", "Arguments")
        ]
        for key, title in columns:
            column = AppKit.NSTableColumn.alloc().initWithIdentifier_(key)
            column.setResizingMask_(AppKit.NSTableColumnAutoresizingMask | AppKit.NSTableColumnUserResizingMask)
            column.headerCell().setTitle_(title)
            dataCell = column.dataCell()
            dataCell.setDrawsBackground_(False)
            dataCell.setStringValue_("")  # cells have weird default values
            column.setEditable_(False)
            self._outlineView.addTableColumn_(column)
            if key == "name":
                self._outlineView.setOutlineTableColumn_(column)

        self._outlineView.setDataSource_(self._model)
        self._outlineView.setDelegate_(self._model)

        self._nsObject.setDocumentView_(self._outlineView)
        self._setAutosizingFromPosSize(posSize)

    def getNSScrollView(self):
        return self._nsObject

    def getNSOutlineView(self):
        return self._outlineView


class PythonBrowserModel(AppKit.NSObject):

    """This is a delegate as well as a data source for NSOutlineViews."""

    def initWithObject_(self, obj):
        self = self.init()
        self.setObject_(obj)
        return self

    def setObject_(self, obj):
        self.root = PythonItem("<root>", obj, None, None)

    # NSOutlineViewDataSource  methods

    def outlineView_numberOfChildrenOfItem_(self, view, item):
        if item is None:
            item = self.root
        return len(item)

    def outlineView_child_ofItem_(self, view, child, item):
        if item is None:
            item = self.root
        return item.getChild(child)

    def outlineView_isItemExpandable_(self, view, item):
        if item is None:
            item = self.root
        return item.isExpandable()

    def outlineView_objectValueForTableColumn_byItem_(self, view, col, item):
        if item is None:
            item = self.root
        identifier = col.identifier()
        value = getattr(item, identifier)
        # filter the type values
        if identifier == "type":
            value = TYPE_COLUMN_MAP.get(value, value)
        return value

    def outlineView_shouldEditTableColumn_item_(self, view, col, item):
        return False

    def outlineView_toolTipForCell_rect_tableColumn_item_mouseLocation_(self, view, cell, rect, col, item, location):
        ## addig a tooltip, use the __doc__ from the object
        return item.getDoc(), rect

# objects of these types are not eligable for expansion in the outline view
SIMPLE_TYPES = (str, int, float, complex)

def getChilderen(root):
    childeren = []

    for name, obj in inspect.getmembers(root):
        ## ignore private methods and attributes
        if name.startswith("_"):
            continue
        ## ignore imported modules
        #elif inspect.ismodule(obj):
        #    continue
        ## ignore methods and attributed usind in pyobjc
        elif name.startswith("pyobjc_"):
            continue
        ## ignore methods and attributed usind in pyobjc
        elif type(obj).__name__ in ["native_selector"]:
            continue
        childeren.append(name)

    return childeren


def getArguments(obj):
    """
    Return all arguments for a method of function
    and leave 'self' out.
    """
    try:
        arguments = inspect.formatargspec(*inspect.getargspec(obj))
    except TypeError:
        arguments = ""
    return arguments.replace("self, ", "").replace("self", "")

class PythonItem(AppKit.NSObject):

    """Wrapper class for items to be displayed in the outline view."""

    # We keep references to all child items (once created). This is
    # neccesary because NSOutlineView holds on to PythonItem instances
    # without retaining them. If we don"t make sure they don"t get
    # garbage collected, the app will crash. For the same reason this
    # class _must_ derive from NSObject, since otherwise autoreleased
    # proxies will be fed to NSOutlineView, which will go away too soon.

    def __new__(cls, *args, **kwargs):
        # "Pythonic" constructor
        return cls.alloc().init()

    def __init__(self, name, obj, parent, setvalue, ignoreAppKit=True):
        self.realName = name
        self.name = str(name)
        self.parent = parent
        self.arguments = ""
        self.type = type(obj).__name__
        if obj is None:
            self.value = "None"
        elif not isinstance(obj, SIMPLE_TYPES):
            self.value = ""
        else:
            self.value = obj

        ## in pyOjbc a python_selector should have an attr callable with is actually the method or function
        if self.type == "python_selector" and hasattr(obj, "callable"):
            obj = obj.callable

        self.object = obj
        self.children = []

        self.getters = dict()
        self.setters = dict()
        if isinstance(obj, dict):
            self.children = sorted(obj.keys())
            self._setGetters(self.children, getitem)
            self._setSetters(self.children, setitem)
        elif obj is None or isinstance(obj, SIMPLE_TYPES):
            pass
        elif isinstance(obj, (list, tuple, set)):
            self.children = list(range(len(obj)))
            self._setGetters(self.children, getitem)
            self._setSetters(self.children, setitem)
        elif isinstance(obj, property):
            pass
        elif inspect.ismethod(obj):
            self.arguments = getArguments(obj)
        elif inspect.isfunction(obj):
            self.arguments = getArguments(obj)
        else:
            try:
                l = list(obj)
                self.children = list(range(len(l)))
                self._setGetters(self.children, getitem)
                self._setSetters(self.children, setitem)
            except:
                pass

            try:
                d = dict(obj)
                self.children = sorted(d.keys())
                self._setGetters(self.children, getitem)
                self._setSetters(self.children, setitem)
            except:
                pass
            children = getChilderen(obj)
            self._setGetters(children, getattr)
            self._setSetters(children, setattr)
            self.children += children

            if inspect.isclass(obj) and hasattr(obj, "__init__"):
                self.arguments = getArguments(getattr(obj, "__init__"))

        if ignoreAppKit:
            self.children = [child for child in self.children if not (isinstance(child, str) and hasattr(AppKit, child))]

        self._childRefs = {}

    @python_method
    def _setSetters(self, names, callback):
        for name in names:
            self.setters[name] = callback

    @python_method
    def _setGetters(self, names, callback):
        for name in names:
            self.getters[name] = callback

    def isExpandable(self):
        return bool(self.children)

    @python_method
    def getChild(self, child):
        if child in self._childRefs:
            return self._childRefs[child]

        name = self.children[child]
        getter = self.getters.get(name)
        setter = self.setters.get(name)
        obj = getter(self.object, name)

        childObj = self.__class__(name, obj, self.object, setter)
        self._childRefs[child] = childObj
        return childObj

    def getDoc(self):
        doc = inspect.getdoc(self.object)
        if doc:
            return doc
        return None

    def __len__(self):
        return len(self.children)


if __name__ == "__main__":
    import vanilla
    testObject = vanilla

    class TestWindow():
        def __init__(self):
            self.w = vanilla.Window((400, 400), "inspect object browser %s" %testObject, minSize=(100, 100))
            self.w.b = ObjectBrowser((0, 0, -0, -0), testObject)
            self.w.open()


    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(TestWindow)







