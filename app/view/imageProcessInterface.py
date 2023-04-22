import sys

from PyQt5.QtCore import QEasingCurve, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QApplication, QVBoxLayout, QLabel, QSizePolicy, QGridLayout
from qfluentwidgets import PopUpAniStackedWidget, NavigationInterface, ScrollArea, PushButton, FluentIcon, LineEdit, \
    ToolButton

from app.common.styleSheet import StyleSheet
from app.componets.imageBox import ImageBox

from app.common import resource


class ImageProcessInterface(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.view = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.view)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.view.setObjectName("view")

        StyleSheet.IMAGE_PROCESS_INTERFACE.apply(self)

        self.imgGridLayout = QGridLayout(self.vBoxLayout.widget())
        self.leftImgInputLayout = QGridLayout(self.imgGridLayout.widget())
        self.consoleHBoxLayout = QHBoxLayout(self.vBoxLayout.widget())

        self.leftImgBox = ImageBox(self.imgGridLayout.widget(), True)
        self.rightImgBox = ImageBox(self.imgGridLayout.widget(), False)

        self.leftImgInput = LineEdit(self.imgGridLayout.widget())
        self.leftImgInput.setPlaceholderText("选择一张图片或一个文件夹")
        self.leftImgInput.setClearButtonEnabled(True)
        self.leftImgInput.textChanged.connect(self.onInputUrlChanged)

        self.leftImgInputButton = ToolButton(FluentIcon.FOLDER.path())

        self.processButton = PushButton("开始", self.consoleHBoxLayout.widget(), FluentIcon.SEND_FILL)

        self.initWidget()

    def initWidget(self):
        self.initLayout()

        self.imgGridLayout.addWidget(self.leftImgBox, 0, 0, 1, 1)
        self.imgGridLayout.addWidget(self.rightImgBox, 0, 1, 1, 1)
        self.imgGridLayout.addLayout(self.leftImgInputLayout, 1, 0, 1, 1)
        self.leftImgInputLayout.addWidget(self.leftImgInput, 0, 0, 1, 4)
        self.leftImgInputLayout.addWidget(self.leftImgInputButton, 0, 4, 1, 1)

        self.consoleHBoxLayout.addWidget(self.processButton)

        self.vBoxLayout.addLayout(self.imgGridLayout)
        self.vBoxLayout.addLayout(self.consoleHBoxLayout)

        self.show()

    def initLayout(self):
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.imgGridLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.consoleHBoxLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.imgGridLayout.setContentsMargins(10, 20, 10, 20)
        self.imgGridLayout.setSpacing(20)

        self.leftImgInputLayout.setContentsMargins(0, 0, 0, 0)
        self.leftImgInputLayout.setSpacing(5)

    def onInputUrlChanged(self, text):
        if len(text) == 0:
            self.leftImgBox.clearImage()
        else:
            self.leftImgBox.setImage(text)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = ImageProcessInterface(None)
    window.setWindowTitle("My PyQt App")

    # 显示主窗口
    window.show()

    # 运行应用程序事件循环
    sys.exit(app.exec_())