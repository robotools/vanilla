from vanillaBase import VanillaBaseObject, VanillaBaseControl, VanillaError
from vanillaBox import Box, HorizontalLine, VerticalLine
from vanillaBrowser import ObjectBrowser
from vanillaButton import Button, SquareButton, ImageButton, HelpButton
from vanillaCheckBox import CheckBox
from vanillaColorWell import ColorWell
from vanillaComboBox import ComboBox
from vanillaDatePicker import DatePicker
from vanillaDrawer import Drawer
from vanillaEditText import EditText, SecureEditText
from vanillaGradientButton import GradientButton
from vanillaGroup import Group
from vanillaImageView import ImageView
from vanillaLevelIndicator import LevelIndicator, LevelIndicatorListCell
from vanillaList import List, CheckBoxListCell, SliderListCell, PopUpButtonListCell, ImageListCell, SegmentedButtonListCell
from vanillaPathControl import PathControl
from vanillaPopUpButton import PopUpButton, ActionButton
from vanillaProgressBar import ProgressBar
from vanillaProgressSpinner import ProgressSpinner
from vanillaRadioGroup import RadioGroup
from vanillaScrollView import ScrollView
from vanillaSearchBox import SearchBox
from vanillaSegmentedButton import SegmentedButton
from vanillaSlider import Slider
from vanillaSplitView2 import SplitView2
from vanillaTabs import Tabs
from vanillaTextBox import TextBox
from vanillaTextEditor import TextEditor
from vanillaWindows import Window, FloatingWindow, HUDFloatingWindow, Sheet

__all__ = [
    "VanillaBaseObject", "VanillaBaseControl", "VanillaError",
    "Box", "HorizontalLine", "VerticalLine",
    "Button", "SquareButton", "ImageButton", "HelpButton",
    "CheckBox",
    "ColorWell",
    "ComboBox",
    "DatePicker",
    "Drawer",
    "EditText",
    "GradientButton",
    "Group",
    "ImageView",
    "LevelIndicator", "LevelIndicatorListCell",
    "List", "CheckBoxListCell", "SliderListCell", "PopUpButtonListCell", "ImageListCell", "SegmentedButtonListCell",
    "ObjectBrowser",
    "PathControl",
    "PopUpButton", "ActionButton",
    "ProgressBar",
    "ProgressSpinner",
    "RadioGroup",
    "ScrollView",
    "SearchBox",
    "SecureEditText",
    "SegmentedButton",
    "Slider",
    "SplitView",
    "SplitView2",
    "Tabs",
    "TextBox",
    "TextEditor",
    "Window", "FloatingWindow", "HUDFloatingWindow", "Sheet"
    ]

# OS 10.7 objects
try:
    from vanillaPopover import Popover
    __all__.append("Popover")
except (ImportError, NameError):
    pass

# RBSplitView required for SplitView
class _NoRBSplitView(object):

    def __init__(self, *args, **kwargs):
        raise VanillaError("SplitView is not available because the RBSplitView framework cannot be found. Refer to the Vanilla documentation for details.")

try:
    from vanillaSplitView import SplitView
    from vanilla.externalFrameworks import RBSplitView
except (ImportError, ValueError):
    SplitView = _NoRBSplitView

