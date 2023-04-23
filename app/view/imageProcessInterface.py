import sys

from PyQt5.QtCore import QEasingCurve, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QApplication, QVBoxLayout, QLabel, QSizePolicy, QGridLayout, \
    QFileDialog
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
        self.consoleGridLayout = QGridLayout(self.vBoxLayout.widget())

        self.leftImgBox = ImageBox(self.imgGridLayout.widget(), True)
        self.rightImgBox = ImageBox(self.imgGridLayout.widget(), False)

        self.leftImgInput = LineEdit(self.imgGridLayout.widget())
        self.leftImgInput.setPlaceholderText(self.tr("选择一张图片或一个目录"))
        self.leftImgInput.setClearButtonEnabled(True)

        self.leftImgInputImageButton = ToolButton(FluentIcon.PHOTO.path())
        self.leftImgInputDirButton = ToolButton(FluentIcon.FOLDER.path())

        self.separator = QFrame(self.vBoxLayout.widget())
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setObjectName("separator")

        self.processButton = PushButton(self.tr("开始"), self.consoleGridLayout.widget(), FluentIcon.SEND_FILL)

        self.__initWidget()

    def __initWidget(self):
        self.__initLayout()

        self.imgGridLayout.addWidget(self.leftImgBox, 0, 0, 1, 1)
        self.imgGridLayout.addWidget(self.rightImgBox, 0, 1, 1, 1)
        self.imgGridLayout.addLayout(self.leftImgInputLayout, 1, 0, 1, 1)
        self.leftImgInputLayout.addWidget(self.leftImgInput, 0, 0, 1, 3)
        self.leftImgInputLayout.addWidget(self.leftImgInputImageButton, 0, 3, 1, 1)
        self.leftImgInputLayout.addWidget(self.leftImgInputDirButton, 0, 4, 1, 1)

        self.consoleGridLayout.addWidget(self.processButton)

        self.vBoxLayout.addLayout(self.imgGridLayout)
        self.vBoxLayout.addWidget(self.separator)
        self.vBoxLayout.addLayout(self.consoleGridLayout)

        self.show()

        self.__connectSignalToSlot()

    def __initLayout(self):
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.imgGridLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.consoleGridLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)

        self.imgGridLayout.setContentsMargins(0, 0, 0, 10)
        self.imgGridLayout.setSpacing(20)

        self.leftImgInputLayout.setContentsMargins(0, 0, 0, 0)
        self.leftImgInputLayout.setSpacing(5)

        self.consoleGridLayout.setContentsMargins(0, 10, 0, 0)
        self.consoleGridLayout.setSpacing(10)

    def __connectSignalToSlot(self):
        self.leftImgInput.textChanged.connect(self.__onInputUrlChanged)
        self.leftImgBox.dropSignal.connect(self.__onInputDrop)

        self.leftImgInputImageButton.clicked.connect(self.__openSelectInputImageDialog)
        self.leftImgInputDirButton.clicked.connect(self.__openSelectInputDirDialog)

    def __openSelectInputImageDialog(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        fileDialog.setWindowTitle(self.tr("选择一张图片"))
        fileDialog.setNameFilter(self.tr("图片文件 (*.jpg *.jpeg *.png *.bmp)"))
        fileDialog.setDirectory(".")
        if fileDialog.exec_():
            urls = fileDialog.selectedUrls()
            self.leftImgInput.setText(urls[0].toLocalFile())

    def __openSelectInputDirDialog(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.DirectoryOnly)
        fileDialog.setWindowTitle(self.tr("选择一个目录"))
        fileDialog.setDirectory(".")
        if fileDialog.exec_():
            urls = fileDialog.selectedUrls()
            self.leftImgInput.setText(urls[0].toLocalFile())

    def __onInputUrlChanged(self, text):
        if len(text) == 0:
            self.leftImgBox.clearImage()
        else:
            self.leftImgBox.setImage(text)

    def __onInputDrop(self, url):
        self.leftImgInput.setText(url)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = ImageProcessInterface(None)
    window.setWindowTitle("My PyQt App")

    # 显示主窗口
    window.show()

    # 运行应用程序事件循环
    sys.exit(app.exec_())