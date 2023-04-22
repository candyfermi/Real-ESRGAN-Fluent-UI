import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsPixmapItem, QSizePolicy
from PyQt5.QtGui import QPixmap, QWheelEvent, QImage
from PyQt5.QtCore import Qt, QMimeData, QEasingCurve, QEvent
from PyQt5.uic.properties import QtGui
from qfluentwidgets import SmoothScrollArea, PixmapLabel
import sys



class ImageBox(QWidget):
    def __init__(self, parent=None, enableDrop=False, enableDrag=True):
        super().__init__(parent=parent)

        self.lastMousePos = None

        self.label = QLabel(self)
        self.label.setAlignment(Qt.AlignCenter)
        self.originImage = None
        self.originImageScaleFactor = 1

        self.resize(300, 200)

        self.label.resize(300, 200)

        if enableDrop:
            self.setAcceptDrops(True)
            self.label.setAcceptDrops(True)

        self.enableDrag = enableDrag

    def setImage(self, imgUrl):
        if os.path.isfile(imgUrl) and os.path.splitext(imgUrl)[1] in [".jpg", "jpeg", ".png"]:
            self.originImage = QImage(imgUrl)
            self.label.setPixmap(QPixmap.fromImage(self.originImage))
            self.label.setGeometry(QtCore.QRect(0, 0, self.label.pixmap().width(), self.label.pixmap().height()))
            self.originImageScaleFactor = 1

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_path = urls[0].toLocalFile()
            self.originImage = QImage(file_path)
            self.label.setPixmap(QPixmap.fromImage(self.originImage))
            self.label.setGeometry(QtCore.QRect(0, 0, self.label.pixmap().width(), self.label.pixmap().height()))
            self.originImageScaleFactor = 1

            event.accept()
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
