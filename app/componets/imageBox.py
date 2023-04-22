import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsPixmapItem, QSizePolicy, QFrame, QStyleOption, QStyle, QVBoxLayout
from PyQt5.QtGui import QPixmap, QWheelEvent, QImage, QPainter
from PyQt5.QtCore import Qt, QMimeData, QEasingCurve, QEvent
from PyQt5.uic.properties import QtGui
from qfluentwidgets import SmoothScrollArea, PixmapLabel, FluentIcon
import sys


class ImageBox(QWidget):
    def __init__(self, parent=None, enableDrop=False):
        super().__init__(parent=parent)

        # 创建垂直布局管理器
        layout = QVBoxLayout(self)

        self.view = QWidget(self)
        self.view.setObjectName("imageBox")
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setMinimumSize(0, 0)

        self.lastMousePos = None

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.originImage = None
        self.originImageScaleFactor = 1
        self.url = None

        if enableDrop:
            self.setAcceptDrops(True)
            self.label.setAcceptDrops(True)
            self.dispIcon(FluentIcon.ADD)

        self.enableDrop = enableDrop
        self.enableDrag = False

        # 将 view 子控件添加到布局管理器中
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.label.move(self.view.x() // 2, self.view.y() // 2)

        self.show()

    def setImage(self, url):
        if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", "jpeg", ".png"]:
            self.url = url
            self.originImage = QImage(url)
            self.label.setPixmap(QPixmap.fromImage(self.originImage))
            self.label.setGeometry(QtCore.QRect(0, 0, self.label.pixmap().width(), self.label.pixmap().height()))
            self.originImageScaleFactor = 1
            self.moveLabelToCenter()
            self.enableDrag = True
        elif os.path.isdir(url):
            self.url = url
            self.originImage = None
            self.originImageScaleFactor = 1
            self.enableDrag = False
            self.dispIcon(FluentIcon.FOLDER)

    def clearImage(self):
        self.url = None
        self.label.clear()
        self.originImage = None
        self.originImageScaleFactor = 1
        self.enableDrag = False
        if self.enableDrop:
            self.dispIcon(FluentIcon.ADD)
        else:
            self.dispIcon(FluentIcon.PHOTO)

    def dispIcon(self, icon: FluentIcon):
        self.label.setPixmap(QPixmap(icon.path()))
        self.moveLabelToCenter()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) is 1:
                url = urls[0].toLocalFile()
                if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", ".jpeg", ".png"]:
                    self.url = url
                    self.originImage = QImage(url)
                    self.label.setPixmap(QPixmap.fromImage(self.originImage))
                    self.label.setGeometry(
                        QtCore.QRect(0, 0, self.label.pixmap().width(), self.label.pixmap().height()))
                    self.originImageScaleFactor = 1
                    self.moveLabelToCenter()
                    self.enableDrag = True
                    event.accept()
                elif os.path.isdir(url):
                    self.url = url
                    self.originImage = None
                    self.originImageScaleFactor = 1
                    self.enableDrag = False
                    self.label.setPixmap(QPixmap(FluentIcon.FOLDER.path()))
                    self.moveLabelToCenter()
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    # 滚轮缩放
    def wheelEvent(self, event):
        if self.enableDrag and self.originImage is not None:
            mousePos = event.pos()
            prevPos = self.label.pos()

            if event.angleDelta().y() > 0:
                self.originImageScaleFactor *= 1.1
                newPosX = mousePos.x() - (mousePos.x() - prevPos.x()) * 1.1
                newPosY = mousePos.y() - (mousePos.y() - prevPos.y()) * 1.1
            elif event.angleDelta().y() < 0:
                self.originImageScaleFactor /= 1.1
                newPosX = mousePos.x() - (mousePos.x() - prevPos.x()) / 1.1
                newPosY = mousePos.y() - (mousePos.y() - prevPos.y()) / 1.1
            else:
                newPosX = prevPos.x()
                newPosY = prevPos.y()

            self.label.setPixmap(
                QPixmap.fromImage(self.originImage).scaled(self.originImage.width() * self.originImageScaleFactor,
                                                           self.originImage.width() * self.originImageScaleFactor,
                                                           Qt.KeepAspectRatio,
                                                           Qt.SmoothTransformation))

            self.label.setGeometry(QtCore.QRect(newPosX,
                                                newPosY,
                                                self.label.pixmap().width(),
                                                self.label.pixmap().height()))

            event.accept()

    def mousePressEvent(self, event):
        if self.enableDrag and self.originImage is not None:
            if event.button() == Qt.LeftButton:
                self.lastMousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.enableDrag and self.originImage is not None and self.label.geometry().contains(self.lastMousePos):
            if event.buttons() & Qt.LeftButton:
                # 计算鼠标移动的距离
                offset = event.pos() - self.lastMousePos

                # 更新图片的位置
                self.label.move(self.label.pos() + offset)

                # 更新上一次记录的鼠标位置
                self.lastMousePos = event.pos()

    def moveLabelToCenter(self):
        self.label.move((self.view.width() - self.label.width()) // 2, (self.view.height() - self.label.height()) // 2)

    def resizeEvent(self, event):
        self.moveLabelToCenter()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # 创建主窗口
    window = ImageBox(None, True)
    window.setWindowTitle("My PyQt App")

    # 显示主窗口
    window.show()

    # 运行应用程序事件循环
    sys.exit(app.exec_())
