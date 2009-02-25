"""
XXX This is SUPER-EXPERIMENTAL!
This may not be needed after 10.5 or it may be a better
idea to wrap some of the open sourced Obj-C HUD frameworks.
"""

from Foundation import *
from AppKit import *
from vanilla import *
from vanillaHUD.controlDrawingTools import *


HUDWindowTitlebarHeight = 19.0

_windowImages = {}

# close button
def _makeCloseWindowButton():
    image = NSImage.alloc().initWithSize_((13.0, 13.0))
    image.lockFocus()

    path = NSBezierPath.bezierPathWithOvalInRect_(((0.0, 0.0), (13.0, 13.0)))
    NSColor.colorWithCalibratedWhite_alpha_(0.9, 1.0).set()
    path.fill()

    path = NSBezierPath.bezierPath()
    path.moveToPoint_((3.5, 3.5))
    path.lineToPoint_((9.5, 9.5))
    path.moveToPoint_((3.5, 9.5))
    path.lineToPoint_((9.5, 3.5))
    path.setLineWidth_(2.0)
    NSColor.colorWithCalibratedWhite_alpha_(.4, 1.0).set()
    path.stroke()

    image.unlockFocus()
    _windowImages['close'] = image

# resize indicator
def _makeResizeWindowIndicator():
    image = NSImage.alloc().initWithSize_((14.0, 14.0))
    image.lockFocus()

    NSColor.colorWithCalibratedWhite_alpha_(0.9, 1.0).set()

    path = NSBezierPath.bezierPath()
    path.moveToPoint_((2.0, 2.0))
    path.lineToPoint_((12.0, 12.0))
    path.moveToPoint_((6.0, 2.0))
    path.lineToPoint_((12.0, 8.0))
    path.moveToPoint_((10.0, 2.0))
    path.lineToPoint_((12.0, 4.0))
    path.setLineWidth_(1.0)
    path.stroke()

    image.unlockFocus()
    _windowImages['resize'] = image


class HUDResizeCornerIndicatorControl(NSControl):

    def acceptsFirstMouse_(self, event):
        return True

    def drawRect_(self, rect):
        if 'resize' not in _windowImages:
            _makeResizeWindowIndicator()
        image = _windowImages['resize']
        image.drawAtPoint_fromRect_operation_fraction_(
            (0.0, 3.0), ((0.0, 0.0), image.size()), NSCompositeSourceOver, 1.0)

    def mouseDragged_(self, event):
        mouseX, mouseY = self.convertPoint_fromView_(event.locationInWindow(), None)
        window = self.window()
        windowFrame = window.frame()
        (windowLeft, windowBottom), (windowWidth, windowHeight) = windowFrame
        deltaX = event.deltaX()
        deltaY = event.deltaY()
        newWidth = windowWidth + deltaX
        newHeight = windowHeight + deltaY
        #
        maxSize = window.maxSize()
        if maxSize is not None:
            maxWidth, maxHeight = maxSize
            if newWidth > maxWidth:
                newWidth = maxWidth
            if newHeight > maxHeight:
                newHeight = maxHeight
        #
        minSize = window.minSize()
        if minSize is not None:
            minWidth, minHeight = minSize
            if newWidth < minWidth:
                newWidth = minWidth
            if newHeight < minHeight:
                newHeight = minHeight
        #
        windowBottom = windowBottom + (windowHeight - newHeight)
        #
        window.setFrame_display_animate_(((windowLeft, windowBottom), (newWidth, newHeight)), True, False)


class HUDNSWindow(NSPanel):

    def canBecomeKeyWindow(self):
        return True


class HUDWindow(FloatingWindow):

    nsWindowStyleMask = NSBorderlessWindowMask
    nsWindowLevel = NSFloatingWindowLevel
    nsWindowClass = HUDNSWindow

    def __init__(self, posSize, title="", minSize=None, maxSize=None,
            autosaveName=None, closable=True, roundBottomOfWindow=True,
            initiallyVisible=True):
        # autosaved frames don't seem to work for HUDWindow
        # so force it to work. DANGEROUS!
        if autosaveName:
            d = NSUserDefaults.standardUserDefaults()
            k = "NSWindow Frame %s" % autosaveName
            if k in d:
                x, y, w, h = [float(i) for i in d[k].split(" ")[:4]]
                posSize = (x, y-HUDWindowTitlebarHeight, w, h-HUDWindowTitlebarHeight)
        if len(posSize) == 2:
            windowWidth, windowHeight = posSize
            windowHeight += HUDWindowTitlebarHeight
            posSize = (windowWidth, windowHeight)
        else:
            windowLeft, windowTop, windowWidth, windowHeight = posSize
            windowTop -= HUDWindowTitlebarHeight
            if windowTop < 0:
                windowTop = 0
            windowHeight += HUDWindowTitlebarHeight
            posSize = (windowLeft, windowTop, windowWidth, windowHeight)
        super(HUDWindow, self).__init__(posSize, title, minSize=None,
                maxSize=None, textured=False, autosaveName=autosaveName,
                closable=closable, initiallyVisible=initiallyVisible)
        self._minSize = minSize
        self._maxSize = maxSize
        window = self._window
        window.setAlphaValue_(1.0)
        window.setOpaque_(False)
        window.setHasShadow_(True)
        contentView = HUDContentView.alloc().init()
        contentView.setRoundBottom_(roundBottomOfWindow)
        if minSize is not None or maxSize is not None:
            left = windowWidth - 17.0
            bottom = 0.0
            mask = NSViewMinXMargin | NSViewMaxYMargin
            resizeView = HUDResizeCornerIndicatorControl.alloc().initWithFrame_(((-17.0, bottom), (17.0, 17.0)))
            contentView.addSubview_(resizeView)
            resizeView.setAutoresizingMask_(mask)
        window.setContentView_(contentView)
        window.setBackgroundColor_(NSColor.clearColor())
        window.setMovableByWindowBackground_(True)
        if closable:
            if 'close' not in _windowImages:
                _makeCloseWindowButton()
            image = _windowImages['close']
            self._closeWindowButton = ImageButton((3, 3, 13, 13), imageObject=image,
                bordered=False, callback=self._closeButtonAction)
            self._closeWindowButton.bind('w', ['command'])

    def __setattr__(self, attr, value):
        # offset for title and window border
        if isinstance(value, VanillaBaseObject) and attr != '_closeWindowButton':
            l, t, w, h = value._posSize
            windowW, windowH = self._window.frame().size

            if l < 0:
                l -= 1
            else:
                l += 1

            if t >= 0.0:
                t += HUDWindowTitlebarHeight

            if w <= 0 or w == windowW:
                w -= 1

            if h <= 0 or h == windowH:
                h -= 1

            value._posSize = (l, t, w, h)
        super(HUDWindow, self).__setattr__(attr, value)

    def _calculateTitlebarHeight(self):
        return HUDWindowTitlebarHeight

    def open(self):
        super(HUDWindow, self).open()
        if self._minSize is not None:
            self._window.setMinSize_(self._minSize)
        if self._maxSize is not None:
            self._window.setMaxSize_(self._maxSize)
        del self._minSize
        del self._maxSize
        self._window.contentView().setNeedsDisplay_(True)

    def _closeButtonAction(self, sender):
        self.close()


_titleParagraphAttrs = NSMutableParagraphStyle.alloc().init()
_titleParagraphAttrs.setAlignment_(NSCenterTextAlignment)
_titleParagraphAttrs.setLineBreakMode_(NSLineBreakByClipping)
_titleShadow = NSShadow.alloc().init()
_titleShadow.setShadowOffset_((1.5, -1.5))
_titleShadow.setShadowBlurRadius_(0.5)
HUDWindowTitleAttributes = {
        NSFontAttributeName : NSFont.boldSystemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize)),
        NSForegroundColorAttributeName : NSColor.whiteColor(),
        NSShadowAttributeName : _titleShadow,
        NSParagraphStyleAttributeName : _titleParagraphAttrs
        }

class HUDContentView(NSView):

    def acceptsFirstMouse_(self, event):
        return True

    def setRoundBottom_(self, value):
        self._roundBottom = value

    def drawRect_(self, rect):
        windowBounds = self.bounds()
        windowWidth, windowHeight = windowBounds.size
        windowIsClosable = self.window().styleMask() & NSClosableWindowMask
        # some constants
        titleBarHeight = HUDWindowTitlebarHeight
        windowCornerRadius = 8.0
        bottomOfTitle = windowHeight - titleBarHeight
        windowBodyFrame = ((0.0, 0.0), (windowWidth, bottomOfTitle))
        windowTitleBarFrame = ((0.0, bottomOfTitle), (windowWidth, titleBarHeight))
        ## the body
        if NSIntersectsRect(rect, windowBodyFrame):
            windowBodyPath = roundedRectBezierPath(windowBodyFrame, windowCornerRadius,
                            roundUpperLeft=False, roundUpperRight=False,
                            roundLowerLeft=self._roundBottom, roundLowerRight=self._roundBottom)
            HUDWindowBodyColor.set()
            windowBodyPath.fill()
        ## the title bar
        if NSIntersectsRect(rect, windowTitleBarFrame):
            windowTitleBarPath = roundedRectBezierPath(windowTitleBarFrame, windowCornerRadius,
                            roundLowerLeft=False, roundLowerRight=False)
            HUDWindowTitleBarColor.set()
            windowTitleBarPath.fill()
            ## the title text
            title = self.window().title()
            if title:
                textWidth, textHeight = title.sizeWithAttributes_(HUDWindowTitleAttributes)
                b = bottomOfTitle + ((titleBarHeight - textHeight) / 2)
                h = textHeight
                # don't overlap the close button with text
                if windowIsClosable and textWidth > windowWidth - 40.0:
                    l = 20.0
                    w = textWidth
                else:
                    l = 0.0
                    w = windowWidth
                rect = ((l, b), (w, h))
                NSString.drawInRect_withAttributes_(title, rect, HUDWindowTitleAttributes)
        ## the border
        if intersectsRectEdge(windowBounds, rect):
            windowBorderPath = roundedRectBezierPath(windowBounds, windowCornerRadius,
                            roundLowerLeft=self._roundBottom, roundLowerRight=self._roundBottom)
            windowBorderPath.setLineWidth_(1.0)
            HUDWindowBorderColor.set()
            strokeInsideBezierPath(windowBorderPath)


class HUDTextBox(TextBox):

    def __init__(self, posSize, text="", alignment="natural", selectable=False):
        super(HUDTextBox, self).__init__(posSize=posSize, text=text, alignment=alignment, selectable=selectable, sizeStyle='small')
        self._nsObject.setTextColor_(NSColor.whiteColor())


class HUDNSTextFieldCell(NSTextFieldCell):

    def drawWithFrame_inView_(self, frame, view):
        HUDControlFrameColor.set()
        (xMin, yMin), (width, height) = frame
        xMin += 1
        yMin += 1
        width -= 2
        height -= 2
        borderFrame = ((xMin, yMin), (width, height))
        NSFrameRect(borderFrame)
        self.drawInteriorWithFrame_inView_(frame, view)

    def setUpFieldEditorAttributes_(self, textObj):
        super(HUDNSTextFieldCell, self).setUpFieldEditorAttributes_(textObj)
        textObj.setSelectedTextAttributes_({NSBackgroundColorAttributeName : HUDEntrySelectedTextBackgroundColor})
        textObj.setInsertionPointColor_(NSColor.whiteColor())
        return textObj


class HUDNSTextField(NSTextField):

    def cellClass(cls):
        return HUDNSTextFieldCell
    cellClass = classmethod(cellClass)


class HUDEditText(EditText):

    _textFieldClass = HUDNSTextField

    def __init__(self, posSize, text="", callback=None, continuous=True, readOnly=False, formatter=None, placeholder=None):
        super(HUDEditText, self).__init__(posSize=posSize, text=text, callback=callback,
            continuous=continuous, readOnly=readOnly, formatter=formatter, placeholder=placeholder, sizeStyle='small')
        self._nsObject.setTextColor_(NSColor.whiteColor())
        self._nsObject.setBackgroundColor_(HUDEntryControlFillColor)
        self._nsObject.setFocusRingType_(NSFocusRingTypeNone)


class HUDTextEditor(TextEditor):

    def __init__(self, posSize, text="", callback=None, readOnly=False, checksSpelling=False):
        super(HUDTextEditor, self).__init__(posSize=posSize, text=text, callback=callback, readOnly=readOnly, checksSpelling=checksSpelling)
        self._textView.setBackgroundColor_(HUDEntryControlFillColor)
        self._textView.setInsertionPointColor_(NSColor.whiteColor())
        self._textView.setTextColor_(NSColor.whiteColor())
        font = NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize))
        self._textView.setFont_(font)


_popUpImages = []

def _makePopUpImages():
    leftCapImage = NSImage.alloc().initWithSize_((4.0, 18.0))
    leftCapImage.setFlipped_(True)
    leftCapImage.lockFocus()

    rect = ((0, 0), (6.0, 18.0))

    clipPath = roundedRectBezierPath(rect, radius=4.0,
        roundUpperRight=False, roundLowerRight=False)    
    clipPath.addClip()

    rectVerticalGradientFill(rect, HUDControlGradientLightColorValue, HUDControlGradientDarkColorValue)

    strokeRect = ((.5, .5), (6.0, 17.0))
    strokePath = roundedRectBezierPath(strokeRect, radius=4,
        roundUpperRight=False, roundLowerRight=False, closeRight=False)
    strokePath.setLineWidth_(1.0)
    
    #drawControlBezelForPath(strokePath)
    
    HUDControlFrameColor.set()
    strokePath.stroke()

    leftCapImage.unlockFocus()

    centerImage = NSImage.alloc().initWithSize_((1.0, 18.0))
    centerImage.setFlipped_(True)
    centerImage.lockFocus()

    rect = ((0.0, 0.0), (1.0, 18.0))

    rectVerticalGradientFill(rect, HUDControlGradientLightColorValue, HUDControlGradientDarkColorValue)

    HUDControlBevelLightColor.set()
    NSRectFillUsingOperation(((0.0, 16.0), (1.0, 1.0)), NSCompositeSourceOver)
    
    HUDControlBevelDarkColor.set()
    NSRectFillUsingOperation(((0.0, 1.0), (1.0, 1.0)), NSCompositeSourceOver)

    HUDControlFrameColor.set()
    NSRectFill(((0.0, 0.0), (1.0, 1.0)))
    NSRectFill(((0.0, 17.0), (1.0, 1.0)))

    centerImage.unlockFocus()

    rightCapImage = NSImage.alloc().initWithSize_((20.0, 18.0))
    rightCapImage.setFlipped_(True)
    rightCapImage.lockFocus()

    rect = ((0, 0), (20.0, 18.0))

    clipPath = roundedRectBezierPath(rect, radius=4,
        roundUpperLeft=False, roundLowerLeft=False)
    clipPath.addClip()

    rectVerticalGradientFill(rect, HUDControlGradientLightColorValue, HUDControlGradientDarkColorValue)

    strokeRect = ((0.0, 0.5), (19.5, 17.0))
    strokePath = roundedRectBezierPath(strokeRect, radius=4,
        roundUpperLeft=False, roundLowerLeft=False, closeLeft=False)
    strokePath.moveToPoint_((1.5, 0.0))
    strokePath.lineToPoint_((1.5, 18.0))
    
    #drawControlBezelForPath(strokePath)
    
    HUDControlFrameColor.set()
    strokePath.setLineWidth_(1.0)
    strokePath.stroke()

    arrowPath = NSBezierPath.bezierPath()
    arrowPath.moveToPoint_((10.5, 4.0))
    arrowPath.lineToPoint_((8.5, 8.0))
    arrowPath.lineToPoint_((12.5, 8.0))
    arrowPath.closePath()
    arrowPath.moveToPoint_((8.5, 10.0))
    arrowPath.lineToPoint_((12.5, 10.0))
    arrowPath.lineToPoint_((10.5, 14.0))
    arrowPath.closePath()
    arrowPath.fill()

    rightCapImage.unlockFocus()

    _popUpImages.append(leftCapImage)
    _popUpImages.append(centerImage)
    _popUpImages.append(rightCapImage)


_popUpTitleAttrs = {
    NSFontAttributeName : NSFont.systemFontOfSize_(NSFont.systemFontSizeForControlSize_(NSSmallControlSize) - 1.0),
    NSForegroundColorAttributeName : HUDButtonTextColor
    }

class HUDNSPopUpButtonCell(NSPopUpButtonCell):

    def drawWithFrame_inView_(self, frame, view):
        if not _popUpImages:
            _makePopUpImages()
        w, h = frame.size
        w -= 6
        h = 18.0
        xMin = 3
        yMin = 1
        rect = ((xMin, yMin), (w, h))
        shadowPath = roundedRectBezierPath(rect, radius=4)
        drawControlShadowForPath(shadowPath)
        tileImagesInRect(_popUpImages, rect)
        title = self.selectedItem().title()
        title.drawInRect_withAttributes_(((11, 3), (w-28, 12)), _popUpTitleAttrs)


class HUDNSPopUpButton(NSPopUpButton):

    def cellClass(cls):
        return HUDNSPopUpButtonCell
    cellClass = classmethod(cellClass)


class HUDPopUpButton(PopUpButton):

    def __init__(self, posSize, items, callback=None):
        self._setupView(HUDNSPopUpButton, posSize)
        self._setSizeStyle('small')
        self._setCallback(callback)
        self._nsObject.addItemsWithTitles_(items)


class HUDNSLineView(NSView):

    def drawRect_(self, rect):
        HUDControlFrameColor.set()
        NSRectFill(rect)


class HUDHorizontalLine(VanillaBaseObject):

    def __init__(self, posSize):
        self._setupView(HUDNSLineView, posSize)


class HUDVerticalLine(HUDHorizontalLine):

    def __init__(self, posSize):
        self._setupView(HUDNSLineView, posSize)


class HUDNSBox(NSView):

    def drawRect_(self, rect):
        selfBounds = self.bounds()
        if not NSIntersectsRect(rect, selfBounds):
            return
        ctx = NSGraphicsContext.currentContext()
        ctx.saveGraphicsState()
        NSBezierPath.clipRect_(rect)
        radius = 4
        path = roundedRectBezierPath(selfBounds, radius)
        HUDBoxFillColor.set()
        path.fill()
        ctx.restoreGraphicsState()
        # only draw the frame if necessary.
        # this prevents some potential pixel duplication.
        drawFrame = intersectsRectEdge(selfBounds, rect)
        if drawFrame:
            path.setLineWidth_(1.0)
            HUDControlFrameColor.set()
            strokeInsideBezierPath(path)


class HUDBox(VanillaBaseObject):

    def __init__(self, posSize):
        self._setupView(HUDNSBox, posSize)


class HUDList(List):

    def __init__(self, posSize, items=None, dataSource=None, columnDescriptions=None,
                showColumnTitles=True, selectionCallback=None, doubleClickCallback=None,
                editCallback=None, enableDelete=False, enableTypingSensitivity=False,
                allowsMultipleSelection=True, allowsEmptySelection=True,
                drawVerticalLines=False, drawHorizontalLines=False,
                autohidesScrollers=True, rowHeight=17.0):
                super(HUDList, self).__init__(
                    posSize=posSize, items=items, dataSource=dataSource, columnDescriptions=columnDescriptions,
                    showColumnTitles=showColumnTitles, selectionCallback=selectionCallback, doubleClickCallback=doubleClickCallback,
                    editCallback=editCallback, enableDelete=enableDelete, enableTypingSensitivity=enableTypingSensitivity,
                    allowsMultipleSelection=allowsMultipleSelection, allowsEmptySelection=allowsEmptySelection,
                    drawVerticalLines=drawVerticalLines, drawHorizontalLines=drawHorizontalLines,
                    autohidesScrollers=autohidesScrollers, rowHeight=rowHeight
                    )
                #self._nsObject.setHorizontalScroller_(HUDScroller.alloc().init())
                #self._nsObject.setVerticalScroller_(HUDScroller.alloc().init())
                #self._nsObject.setHasHorizontalScroller_(True)
                #self._nsObject.setBackgroundColor_(HUDEntryControlFillColor)
                #
                self._nsObject.horizontalScroller().setControlSize_(NSSmallControlSize)
                self._nsObject.verticalScroller().setControlSize_(NSSmallControlSize)
                #
                self._tableView.setBackgroundColor_(HUDEntryControlFillColor)
                self._tableView.setFocusRingType_(NSFocusRingTypeNone)
                self._tableView.setGridColor_(HUDControlFrameColor)
                self._tableView.setUsesAlternatingRowBackgroundColors_(False)
                #
                for column in self._tableView.tableColumns():
                    cell = column.dataCell()
                    cell.setTextColor_(NSColor.whiteColor())
                    #headerCell = column.headerCell()
                    #headerCell.setTextColor_(NSColor.whiteColor())
                    #headerCell.setBackgroundColor_(HUDControlFillColor)
                    #headerCell.setDrawsBackground_(True)


