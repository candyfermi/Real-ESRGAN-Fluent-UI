import os
import sys

from PyQt5.QtCore import Qt, QTranslator
from PyQt5.QtWidgets import QApplication

from app.view.mainWindow import MainWindow
from app.common.config import cfg


if cfg.get(cfg.dpiScale) == "Auto":
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
else:
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "0"
    os.environ["QT_SCALE_FACTOR"] = str(cfg.get(cfg.dpiScale))

QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

# 创建一个 PyQt 应用程序
app = QApplication(sys.argv)
app.setAttribute(Qt.AA_DontCreateNativeWidgetSiblings)

translator = QTranslator()
language = cfg.get(cfg.language).value
translator.load(language, "locale", ".", ":/res/i18n")
app.installTranslator(translator)

# 创建主窗口
window = MainWindow()

# 显示主窗口
window.show()

# 运行应用程序事件循环
app.exec_()
