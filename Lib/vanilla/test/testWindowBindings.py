import vanilla

instructions = """
1. Launch the test window.
- (Psst, press the button up there.)

2. Move the test window.
- "move" - not observed

3. Resize the test window.
- "resize" - not observed

4. Select this window...

- "resigned main" - not observed
- "resigned key" - not observed

... then select the test window.

- "became main" - not observed
- "became key" - not observed

5. Close the test window.
- "should close" - not observed
- "close" - not observed
"""

class TestWindowBindingsLauncher:

    def __init__(self):
        self.w = vanilla.Window((250, 500), "Test Launcher")
        self.w.launchButton = vanilla.Button(
            (10, 10, -10, 20),
            "Launch Test Window",
            self.launchButtonCallback
        )
        self.w.reportField = vanilla.TextEditor(
            (10, 40, -10, -10),
            instructions
        )
        self.w.open()

    def launchButtonCallback(self, sender):
        TestWindowBindings(
            getter=self.w.reportField.get,
            setter=self.w.reportField.set
        )
        text = self.w.reportField.get()
        text = text.replace("- (Psst, press the button up there.)", "- Done!")
        self.w.reportField.set(text)

class TestWindowBindings:

    def __init__(self, setter, getter):
        self.textSetter = setter
        self.textGetter = getter
        self.w = vanilla.Window(
            (300, 300),
            "Test Window",
            minSize=(200, 200)
        )
        self.w.text = vanilla.EditText(
            (10, 10, -10, -10),
            "Follow the instructions in the launcher window."
        )
        self.w.open()
        self.w.bind("should close", self.shouldCloseCallback)
        self.w.bind("close", self.closeCallback)
        self.w.bind("move", self.moveCallback)
        self.w.bind("resize", self.resizeCallback)
        self.w.bind("became main", self.becameMainCallback)
        self.w.bind("resigned main", self.resignedMainCallback)
        self.w.bind("became key", self.becameKeyCallback)
        self.w.bind("resigned key", self.resignedKeyCallback)

    def shouldCloseCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"should close\" - not observed", "- \"should close\" - Done!")
        self.textSetter(text)
        return True

    def closeCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"close\" - not observed", "- \"close\" - Done!")
        self.textSetter(text)

    def moveCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"move\" - not observed", "- \"move\" - Done!")
        self.textSetter(text)

    def resizeCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"resize\" - not observed", "- \"resize\" - Done!")
        self.textSetter(text)

    def becameMainCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"became main\" - not observed", "- \"became main\" - Done!")
        self.textSetter(text)

    def resignedMainCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"resigned main\" - not observed", "- \"resigned main\" - Done!")
        self.textSetter(text)

    def becameKeyCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"became key\" - not observed", "- \"became key\" - Done!")
        self.textSetter(text)

    def resignedKeyCallback(self, sender):
        text = self.textGetter()
        text = text.replace("- \"resigned key\" - not observed", "- \"resigned key\" - Done!")
        self.textSetter(text)


if __name__ == "__main__":
    from vanilla.test.testTools import executeVanillaTest
    executeVanillaTest(TestWindowBindingsLauncher)
