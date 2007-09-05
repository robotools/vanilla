from AppKit import *
import vanilla

class TestCell(NSActionCell):

    def drawWithFrame_inView_(self, frame, view):
        value = self.objectValue()
        if value == 1:
            NSColor.redColor().set()
        elif value == 2:
            NSColor.greenColor().set()
        elif value == 3:
            NSColor.blueColor().set()
        else:
            NSColor.yellowColor().set()
        NSRectFill(frame)


class Test(object):

    def __init__(self):
        self.w  = vanilla.Window((400, 400))
        columnDescriptions = [
            dict(title="test", key="test", cell=TestCell.alloc().init()),
            dict(title="string", key="string")
        ]
        items = [
            dict(test=1, string="one"),
            dict(test=2, string="two"),
            dict(test=3, string="three"),
        ]
        self.w.l = vanilla.List((10, 10, -10, -10), items, columnDescriptions=columnDescriptions)
        self.w.open()

if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(Test)
