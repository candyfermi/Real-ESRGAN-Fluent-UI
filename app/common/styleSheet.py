# coding: utf-8
from enum import Enum

from qfluentwidgets import StyleSheetBase, Theme, isDarkTheme, qconfig


class StyleSheet(StyleSheetBase, Enum):
    """ Style sheet  """

    MAIN_WINDOW = "main_window"
    IMAGE_PROCESS_INTERFACE = "image_process_interface"
    SETTING_INTERFACE = "setting_interface"
    PROGRESS_TIP = "progress_tip"
    PARAMS_DIALOG = "params_dialog"

    def path(self, theme=Theme.AUTO):
        theme = qconfig.theme if theme == Theme.AUTO else theme
        return f":/res/qss/{theme.value.lower()}/{self.value}.qss"
