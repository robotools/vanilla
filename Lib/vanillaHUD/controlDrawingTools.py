from Foundation import *
from AppKit import *

HUDControlGradientLightColorValue = 0.2
HUDControlGradientDarkColorValue = 0.1
HUDSelectedControlGradientLightColorValue = 0.25
HUDSelectedControlGradientDarkColorValue = 0.15

HUDWindowTitleBarColor = NSColor.colorWithCalibratedWhite_alpha_(0.2, 0.9)
HUDWindowBodyColor = NSColor.colorWithCalibratedWhite_alpha_(0.05, 0.9)
HUDWindowBorderColor = NSColor.colorWithCalibratedWhite_alpha_(0.45, 1.0)
HUDEntryControlFillColor = NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.92)
HUDControlFrameColor = NSColor.colorWithCalibratedWhite_alpha_(0.64, 1.0)
HUDControlFillColor = NSColor.colorWithCalibratedWhite_alpha_(0.05, 1.0)
HUDBoxFillColor = NSColor.colorWithCalibratedWhite_alpha_(0.05, 0.5)
HUDButtonTextColor = NSColor.colorWithCalibratedWhite_alpha_(0.75, 1.0)
HUDControlBevelLightColor = NSColor.colorWithCalibratedWhite_alpha_(1.0, 0.035)
HUDControlBevelDarkColor = NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.2)
HUDEntrySelectedTextBackgroundColor = NSColor.colorWithCalibratedWhite_alpha_(0.35, 1.0)

HUDControlShadow = NSShadow.alloc().init()
HUDControlShadow.setShadowOffset_((0, -2))
HUDControlShadow.setShadowColor_(NSColor.blackColor())
HUDControlShadow.setShadowBlurRadius_(2.0)

def rectVerticalGradientFill(rect, topColor, bottomColor):
    (xMin, yMin), (w, h) = rect
    bands = h
    colorStep = (topColor - bottomColor) / bands
    color = bottomColor
    for i in xrange(int(bands)):
        r = ((xMin, yMin), (w, 1.0))
        NSColor.colorWithCalibratedWhite_alpha_(color, 1.0).set()
        NSRectFill(r)
        color += colorStep
        yMin += 1.0

def rectHorizontalGradientFill(rect, leftColor, rightColor):
    (xMin, yMin), (w, h) = rect
    bands = w
    colorStep = (rightColor - leftColor) / bands
    color = leftColor
    for i in xrange(int(bands)):
        r = ((xMin, yMin), (1.0, h))
        NSColor.colorWithCalibratedWhite_alpha_(color, 1.0).set()
        NSRectFill(r)
        color += colorStep
        xMin += 1.0

def tileImagesInRect(images, rect):
    leftImage, centerImage, rightImage = images
    
    (xMin, yMin), (w, h) = rect
    
    leftWidth = leftImage.size()[0]
    rightWidth = rightImage.size()[0]
    centerWidth = w - (leftWidth + rightWidth)
    
    leftImage.drawAtPoint_fromRect_operation_fraction_(
        (xMin, yMin), ((0.0, 0.0), leftImage.size()), NSCompositeSourceOver, 1.0
        )
    xMin += leftWidth
    centerImage.drawInRect_fromRect_operation_fraction_(
        ((xMin, yMin), (centerWidth, h)), ((0.0, 0.0), centerImage.size()), NSCompositeSourceOver, 1.0
        )
    xMin += centerWidth
    rightImage.drawAtPoint_fromRect_operation_fraction_(
        (xMin, yMin), ((0.0, 0.0), rightImage.size()), NSCompositeSourceOver, 1.0
        )

def roundedRectBezierPath(rect, radius,
        roundUpperLeft=True, roundUpperRight=True, roundLowerLeft=True, roundLowerRight=True,
        closeTop=True, closeBottom=True, closeLeft=True, closeRight=True):

    (rectLeft, rectBottom), (rectWidth, rectHeight) = rect
    rectTop = rectBottom + rectHeight
    rectRight = rectLeft + rectWidth

    path = NSBezierPath.bezierPath()

    if roundUpperLeft:
        path.moveToPoint_((rectLeft, rectHeight-radius))
        path.appendBezierPathWithArcFromPoint_toPoint_radius_((rectLeft, rectTop), (rectLeft+radius, rectTop), radius)
    else:
        path.moveToPoint_((rectLeft, rectTop))

    if roundUpperRight:
        if closeTop:
            path.lineToPoint_((rectRight-radius, rectTop))
        else:
            path.moveToPoint_((rectRight-radius, rectTop))
        path.appendBezierPathWithArcFromPoint_toPoint_radius_((rectRight, rectTop), (rectRight, rectTop-radius), radius)
    else:
        if closeTop:
            path.lineToPoint_((rectRight, rectTop))
        else:
            path.moveToPoint_((rectRight, rectTop))

    if roundLowerRight:
        if closeRight:
            path.lineToPoint_((rectRight, rectBottom+radius))
        else:
            path.moveToPoint_((rectRight, rectBottom+radius))
        path.appendBezierPathWithArcFromPoint_toPoint_radius_((rectRight, rectBottom), (rectRight-radius, rectBottom), radius)
    else:
        if closeRight:
            path.lineToPoint_((rectRight, rectBottom))
        else:
            path.moveToPoint_((rectRight, rectBottom))

    if roundLowerLeft:
        if closeBottom:
            path.lineToPoint_((rectLeft+radius, rectBottom))
        else:
            path.moveToPoint_((rectLeft+radius, rectBottom))
        path.appendBezierPathWithArcFromPoint_toPoint_radius_((rectLeft, rectBottom), (rectLeft, rectBottom+radius), radius)
    else:
        if closeBottom:
            path.lineToPoint_((rectLeft, rectBottom))
        else:
            path.moveToPoint_((rectLeft, rectBottom))

    if closeLeft:
        if roundUpperLeft:
            path.lineToPoint_((rectLeft, rectHeight-radius))
        else:
            path.lineToPoint_((rectLeft, rectTop))

    return path

def drawControlBezelForPath(path):
    lineWidth = path.lineWidth()
    path.setLineWidth_(lineWidth + 1)
    
    HUDControlBevelLightColor.set()
    transform = NSAffineTransform.transform()
    transform.translateXBy_yBy_(1, -1)
    path.transformUsingAffineTransform_(transform)
    path.stroke()
    
    HUDControlBevelDarkColor.set()
    transform = NSAffineTransform.transform()
    transform.translateXBy_yBy_(-2, 2)
    path.transformUsingAffineTransform_(transform)
    path.stroke()
    
    transform = NSAffineTransform.transform()
    transform.translateXBy_yBy_(1, -1)
    path.transformUsingAffineTransform_(transform)
    

def drawControlShadowForPath(path):
    ctx = NSGraphicsContext.currentContext()
    ctx.saveGraphicsState()
    HUDControlShadow.set()
    NSColor.colorWithCalibratedWhite_alpha_(0.0, 0.5).set()
    path.fill()
    ctx.restoreGraphicsState()

def strokeInsideBezierPath(path):
    ctx = NSGraphicsContext.currentContext()
    ctx.saveGraphicsState()
    startWidth = path.lineWidth()
    path.setClip()
    path.setLineWidth_(startWidth * 2)
    path.stroke()
    ctx.restoreGraphicsState()
    path.setLineWidth_(startWidth)

def intersectsRectEdge(rect1, rect2):
    """
    returns True if rect2 intersects rect1's edge.

    >>> r1 = ((0, 0), (100, 100))
    >>> r2 = ((0, 0), (50, 50))
    >>> intersectsRectEdge(r1, r2)
    True
    >>> r1 = ((0, 0), (100, 100))
    >>> r2 = ((10, 10), (90, 90))
    >>> intersectsRectEdge(r1, r2)
    True
    >>> r1 = ((0, 0), (100, 100))
    >>> r2 = ((-10, -10), (50, 50))
    >>> intersectsRectEdge(r1, r2)
    True
    >>> r1 = ((0, 0), (100, 100))
    >>> r2 = ((10, 10), (100, 100))
    >>> intersectsRectEdge(r1, r2)
    True
    >>> r1 = ((0, 0), (100, 100))
    >>> r2 = ((10, 10), (50, 50))
    >>> intersectsRectEdge(r1, r2)
    False
    """
    (r1XMin, r1YMin), (r1W, r1H) = rect1
    (r2XMin, r2YMin), (r2W, r2H) = rect2
    if r2XMin <= r1XMin:
        return True
    elif r2YMin <= r1YMin:
        return True
    elif r2XMin + r2W >= r1XMin + r1W:
        return True
    elif r2YMin + r2H >= r1YMin + r1H:
        return True
    return False

if __name__ == "__main__":
    import doctest
    doctest.testmod()