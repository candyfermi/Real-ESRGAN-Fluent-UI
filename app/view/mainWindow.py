from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication
from qfluentwidgets import NavigationItemPosition, FluentIcon,MessageDialog, FluentWindow, SplashScreen

from app.common.signalBus import signalBus
from app.common import resource
from app.view.imageProcessInterface import ImageProcessInterface
from app.view.settingInterface import SettingInterface


class MainWindow(FluentWindow):
    def __init__(self):
        super().__init__()
        self.initWindow()

        self.imageProcessInterface = ImageProcessInterface(self)
        self.imageProcessInterface.setObjectName("imageProcessInterface")
        self.settingInterface = SettingInterface(self)
        self.settingInterface.setObjectName("settingInterface")

        # add items to navigation interface
        self.initNavigation()
        self.splashScreen.finish()

    def initNavigation(self):
        self.addSubInterface(
            self.imageProcessInterface,
            FluentIcon.ZOOM,
            self.tr("超分辨率"),
        )
        self.addSubInterface(
            self.settingInterface,
            FluentIcon.SETTING,
            self.tr("设置"),
            NavigationItemPosition.BOTTOM
        )

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setWindowIcon(QIcon(':/res/image/icon.png'))
        self.setWindowTitle('RealESRGAN Fluent UI')

        self.splashScreen = SplashScreen(self.windowIcon(), self)
        self.splashScreen.setIconSize(QSize(128, 128))
        self.splashScreen.raise_()

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)
        self.show()
        QApplication.processEvents()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        if hasattr(self, "splashScreen"):
            self.splashScreen.resize(self.size())

    def closeEvent(self, event):
        if self.imageProcessInterface.isProcessing():
            closeDialog = MessageDialog(self.tr("关闭窗口"),
                                        self.tr("图像处理进程正在后台运行，此时退出可能导致结果丢失，确定要关闭吗"),
                                        self.window())
            closeDialog.yesButton.clicked.connect(self.__close)
            closeDialog.cancelButton.clicked.connect(lambda: event.ignore())
            closeDialog.exec()
        else:
            event.accept()

    def __close(self):
        self.imageProcessInterface.stopProcess()
        self.close()
