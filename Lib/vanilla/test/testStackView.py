import AppKit
import vanilla


class TestStackView:

    """
    This is a vanilla implementation of an example here:
    https://developer.apple.com/library/archive/documentation/UserExperience/Conceptual/AutolayoutPG/LayoutUsingStackViews.html#//apple_ref/doc/uid/TP40010853-CH11-SW1
    """

    def __init__(self):
        self.w = vanilla.Window((500, 500), minSize=(200, 200))

        # Stack 1
        blue = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 0, 1, 0.75)
        stack1Views = [
            vanilla.Box("auto", fillColor=blue),
            vanilla.Box("auto", fillColor=blue),
            vanilla.Box("auto", fillColor=blue)
        ]
        stack1 = vanilla.VerticalStackView(
            "auto",
            views=stack1Views,
            spacing=10,
            edgeInsets=(0, 0, 0, 0)
        )

        # Stack 2
        green = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(0, 1, 0, 0.75)
        greenBox = vanilla.Box("auto", fillColor=green)
        stack2Views = [
            dict(
                view=greenBox,
                width=150
            ),
            dict(
                view=stack1
            )
        ]
        stack2 = vanilla.HorizontalStackView(
            "auto",
            views=stack2Views,
            spacing=10,
            edgeInsets=(0, 0, 0, 0),
            distribution="fill"
        )

        # Stack 3
        red = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 0, 0, 0.75)
        stack3Views = [
            dict(
                view=vanilla.Box("auto", fillColor=red),
                width=75
            ),
            dict(
                view=vanilla.Box("auto", fillColor=red),
                width=75
            ),
            dict(
                view=vanilla.Box("auto", fillColor=red),
                width=75
            )
        ]
        stack3 = vanilla.HorizontalStackView(
            "auto",
            views=stack3Views,
            spacing=10,
            edgeInsets=(0, 0, 0, 0)
        )

        # Stack 4
        yellow = AppKit.NSColor.colorWithCalibratedRed_green_blue_alpha_(1, 1, 0, 0.75)
        stack4Views = [
            dict(
                view=stack2,
                width=">=100"
            ),
            dict(
                view=vanilla.Box("auto", fillColor=yellow),
                height=">=50, <=100"
            ),
            dict(
                view=stack3,
                height=30
            )
        ]
        stack4 = vanilla.VerticalStackView(
            "auto",
            views=stack4Views,
            spacing=10,
            edgeInsets=(0, 0, 0, 0)
        )

        self.w.stack = stack4
        metrics = dict(
            margin=15
        )
        rules = [
            "H:|-margin-[stack]-margin-|",
            "V:|-margin-[stack]-margin-|",
        ]
        self.w.addAutoPosSizeRules(rules, metrics)

        self.w.open()


if __name__ == "__main__":
    import vanilla
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(TestStackView)