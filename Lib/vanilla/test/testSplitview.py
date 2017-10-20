from vanilla import *


class TestSplitView(object):

    def __init__(self, view):

        self.w = Window((400, 400), "%s" % view.__name__, minSize=(200, 200))

        anEditor = TextEditor((0, 0, -0, -0))
        aList = List((0, 0, -0, -0), ["a", "b", "c"])

        group = Group((0, 0, -0, -0))
        group.aList = List((0, 0, -0, -0), ["x", "y", "z"])

        nestedPaneDescriptions = [
            dict(view=group, identifier="group", canCollapse=False),
            dict(view=aList, identifier="aList", minSize=100, maxSize=300)
        ]

        nestedSplit = view((0, 0, -0, -0), paneDescriptions=nestedPaneDescriptions)

        paneDescriptions = [
            dict(view=anEditor, identifier="anEditor", canCollapse=False),
            dict(view=nestedSplit, identifier="nestedSplit", minSize=100, maxSize=300),
        ]
        self.w.splitView = view((0, 0, -0, -0), paneDescriptions=paneDescriptions, isVertical=False)
        self.w.open()


def testSplitView():

    for view in SplitView, SplitView2:
        TestSplitView(view)


testSplitView()
