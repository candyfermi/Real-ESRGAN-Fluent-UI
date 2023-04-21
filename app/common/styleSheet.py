# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    MAIN_WINDOW = "main_window"

    def path(self, theme=Theme.AUTO):
        return f":/res/qss/{self.value}.qss"
