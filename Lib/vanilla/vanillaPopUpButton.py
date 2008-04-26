from AppKit import NSPopUpButton
from vanillaBase import VanillaBaseControl


class PopUpButton(VanillaBaseControl):
    
    """
    A button which, when selected, displays a list of items for the user to choose from.
    
    pre.
    from vanilla import *
     
    class PopUpButtonDemo(object):
        
        def __init__(self):
            self.w = Window((100, 40))
            self.w.popUpButton = PopUpButton((10, 10, -10, 20),
                                  ['A', 'B', 'C'],
                                  callback=self.popUpButtonCallback)
            self.w.open()
            
        def popUpButtonCallback(self, sender):
            print 'pop up button selection!', sender.get()
            
    PopUpButtonDemo()
    """

    nsPopUpButtonClass = NSPopUpButton

    frameAdjustments = {
        'mini': (-1, 0, 3, 0),
        'small': (-3, -4, 6, 5),
        'regular': (-3, -4, 6, 6),
    }

    def __init__(self, posSize, items, callback=None, sizeStyle="regular"):
        """
        *posSize* Tuple of form (left, top, width, height) representing the position and size of the pop up button. The size of the button sould match the appropriate value for the given _sizeStyle_.

        |\\3. *Standard Dimensions* |
        | Regular | H | 20          |
        | Small   | H | 17          |
        | Mini    | H | 15          |
        
        *items* A list of items to appear in the pop up list.
        
        *callback* The method to be called when the user selects an item in the pop up list.
        
        *sizeStyle* A string representing the desired size style of the pop up button. The options are:
        
        | "regular" |
        | "small"   |
        | "mini"    |
        """
        self._setupView(self.nsPopUpButtonClass, posSize, callback=callback)
        self._setSizeStyle(sizeStyle)
        self._nsObject.addItemsWithTitles_(items)
        
    def getNSPopUpButton(self):
        """
        Return the _NSPopUpButton_ that this object wraps.
        """
        return self._nsObject

    def get(self):
        """
        Get the index selected item in the pop up list.
        """
        return self._nsObject.indexOfSelectedItem()

    def set(self, value):
        """
        Set the index of the selected item in the pop up list.
        """
        self._nsObject.selectItemAtIndex_(value)

    def setItems(self, items):
        """
        Set the items to appear in the pop up list.
        """
        self._nsObject.removeAllItems()
        self._nsObject.addItemsWithTitles_(items)

    def getItems(self):
        """
        Get the list of items that appear in the pop up list.
        """
        return self._nsObject.itemTitles()
