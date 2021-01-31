from warnings import warn
from vanilla.vanillaStackView import HorizontalStackView, VerticalStackView

class HorizontalStackGroup(HorizontalStackView):

    def __init__(self, posSize, *args, **kwargs):
        warn(
            DeprecationWarning("Use HorizontalStackView instead of HorizontalStackGroup.")
        )
        super().__init__(posSize, [], *args, **kwargs)

    def addView(self, *args, **kwargs):
        self.appendView(*args, **kwargs)


class VerticalStackGroup(VerticalStackView):

    def __init__(self, posSize, *args, **kwargs):
        warn(
            DeprecationWarning("Use VerticalStackView instead of VerticalStackGroup.")
        )
        super().__init__(posSize, [], *args, **kwargs)

    def addView(self, *args, **kwargs):
        self.appendView(*args, **kwargs)