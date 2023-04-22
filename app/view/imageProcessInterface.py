from PyQt5.QtCore import QEasingCurve, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QApplication, QVBoxLayout, QLabel
from qfluentwidgets import PopUpAniStackedWidget, NavigationInterface, ScrollArea
from qframelesswindow import FramelessWindow

from app.common.styleSheet import StyleSheet
from app.componets.imageBox import ImageBox

from app.common import resource


class ImageProcessInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.leftImgBox = ImageBox(self, True, True)
        self.rightImgBox = ImageBox(self, False, True)
        self.vBoxLayout = QVBoxLayout(self.view)
        self.imgHBoxLayout = QHBoxLayout()
        self.leftImgVBoxLayout = QVBoxLayout()
        self.rightImgVBoxLayout = QVBoxLayout()
        self.consoleHBoxLayout = QHBoxLayout()

        self.initWidget()

    def initWidget(self):
        self.view.setObjectName("view")

        StyleSheet.IMAGE_PROCESS_INTERFACE.apply(self)

        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.vBoxLayout.setContentsMargins(0, 0, 0, 36)
        self.vBoxLayout.setSpacing(40)
        self.vBoxLayout.setAlignment(Qt.AlignTop)
        self.vBoxLayout.addWidget(QLabel("hhhh"))

        self.imgHBoxLayout.setContentsMargins(10, 20, 10, 20)
        self.imgHBoxLayout.setSpacing(40)
        self.imgHBoxLayout.setAlignment(Qt.AlignCenter)

        self.leftImgVBoxLayout.addWidget(self.leftImgBox)
        self.rightImgVBoxLayout.addWidget(self.rightImgBox)

        self.imgHBoxLayout.addLayout(self.leftImgVBoxLayout)
        self.imgHBoxLayout.addLayout(self.rightImgVBoxLayout)

        self.vBoxLayout.addLayout(self.imgHBoxLayout)
        self.vBoxLayout.addLayout(self.consoleHBoxLayout)
