import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsPixmapItem, QSizePolicy, QFrame, QStyleOption, QStyle, QVBoxLayout
from PyQt5.QtGui import QPixmap, QWheelEvent, QImage, QPainter
from PyQt5.QtCore import Qt, QMimeData, QEasingCurve, QEvent, pyqtSignal, QObject
from PyQt5.uic.properties import QtGui
from qfluentwidgets import SmoothScrollArea, PixmapLabel, FluentIcon, Theme
import sys

from app.common.config import cfg


class ImageBox(QWidget):
    dropSignal = pyqtSignal(str)
    infoChange = pyqtSignal(str)
    imgGeometryChange = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None, enableDrop=False, acceptDir=True):
        super().__init__(parent=parent)

        # 创建垂直布局管理器
        layout = QVBoxLayout(self)

        self.view = QWidget(self)
        self.view.setObjectName("imageBox")
        self.view.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.view.setMinimumSize(0, 0)

        self.__lastMousePos = None

        self.__label = QLabel(self)
        self.__label.setAlignment(Qt.AlignCenter)
        self.__label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.__originImage = None
        self.__originImageScaleFactor = 1
        self.__url = None

        if enableDrop:
            self.setAcceptDrops(True)
            self.__label.setAcceptDrops(True)
            self.dispIcon(FluentIcon.ADD)
        else:
            self.dispIcon(FluentIcon.PHOTO)

        self.__enableDrop = enableDrop
        self.__enableDrag = False
        self.__acceptDir = acceptDir
        self.__lock = False

        cfg.themeChanged.connect(self.__onThemeChanged)

        # 将 view 子控件添加到布局管理器中
        layout.addWidget(self.view)
        layout.setContentsMargins(0, 0, 0, 0)

        self.__label.move(self.view.x() // 2, self.view.y() // 2)

        self.show()

    def url(self):
        return self.__url

    def lock(self):
        return self.__lock

    def setLock(self, lock: bool):
        self.__lock = lock

    def setImage(self, url):
        if self.__lock:
            return
        if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", "jpeg", ".png", ".bmp"]:
            self.__url = url
            self.__originImage = QImage(url)
            self.__label.setPixmap(QPixmap.fromImage(self.__originImage))
            self.__label.setGeometry(QtCore.QRect(0, 0, self.__label.pixmap().width(), self.__label.pixmap().height()))
            self.__originImageScaleFactor = 1
            self.moveLabelToCenter()
            self.__updateInfoLabel()
            self.setPreferredImageSize()
            self.__enableDrag = True
        elif self.__acceptDir and os.path.isdir(url):
            self.__url = url
            self.__originImage = None
            self.__originImageScaleFactor = 1
            self.__enableDrag = False
            self.__updateInfoLabel()
            self.dispIcon(FluentIcon.FOLDER)

    def clearImage(self):
        self.__url = None
        self.__label.clear()
        self.__originImage = None
        self.__originImageScaleFactor = 1
        self.__enableDrag = False
        self.__updateInfoLabel()
        if self.__enableDrop:
            self.dispIcon(FluentIcon.ADD)
        else:
            self.dispIcon(FluentIcon.PHOTO)

    def dispIcon(self, icon: FluentIcon, theme: Theme = Theme.AUTO):
        self.__label.setPixmap(QPixmap(icon.path(theme)))
        self.moveLabelToCenter()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        if self.__lock:
            event.ignore()
            return
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) is 1:
                url = urls[0].toLocalFile()
                if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", ".jpeg", ".png", ".bmp"]:
                    self.__url = url
                    self.__originImage = QImage(url)
                    self.__label.setPixmap(QPixmap.fromImage(self.__originImage))
                    self.__label.setGeometry(
                        QtCore.QRect(0, 0, self.__label.pixmap().width(), self.__label.pixmap().height()))
                    self.__originImageScaleFactor = 1
                    self.moveLabelToCenter()
                    self.__enableDrag = True
                    self.__updateInfoLabel()
                    self.dropSignal.emit(url)
                    self.setPreferredImageSize()
                    event.accept()
                elif self.__acceptDir and os.path.isdir(url):
                    self.__url = url
                    self.__originImage = None
                    self.__originImageScaleFactor = 1
                    self.__enableDrag = False
                    self.__label.setPixmap(QPixmap(FluentIcon.FOLDER.path()))
                    self.moveLabelToCenter()
                    self.__updateInfoLabel()
                    self.dropSignal.emit(url)
                    event.accept()
                else:
                    event.ignore()
            else:
                event.ignore()
        else:
            event.ignore()

    # 滚轮缩放
    def wheelEvent(self, event):
        if self.__enableDrag and self.__originImage is not None:
            mousePos = event.pos()
            prevPos = self.__label.pos()

            if event.angleDelta().y() > 0:
                self.__originImageScaleFactor *= 1.1
                newPosX = mousePos.x() - (mousePos.x() - prevPos.x()) * 1.1
                newPosY = mousePos.y() - (mousePos.y() - prevPos.y()) * 1.1
            elif event.angleDelta().y() < 0:
                self.__originImageScaleFactor /= 1.1
                newPosX = mousePos.x() - (mousePos.x() - prevPos.x()) / 1.1
                newPosY = mousePos.y() - (mousePos.y() - prevPos.y()) / 1.1
            else:
                newPosX = prevPos.x()
                newPosY = prevPos.y()

            self.__label.setPixmap(
                QPixmap.fromImage(self.__originImage).scaled(self.__originImage.width() * self.__originImageScaleFactor,
                                                             self.__originImage.width() * self.__originImageScaleFactor,
                                                             Qt.KeepAspectRatio,
                                                             Qt.FastTransformation))

            self.__label.setGeometry(QtCore.QRect(newPosX,
                                                  newPosY,
                                                  self.__label.pixmap().width(),
                                                  self.__label.pixmap().height()))

            self.imgGeometryChange.emit(self.__label.x(),
                                        self.__label.y(),
                                        self.__label.pixmap().width(),
                                        self.__label.pixmap().height())

            self.__updateInfoLabel()

            event.accept()

    def mousePressEvent(self, event):
        if self.__enableDrag and self.__originImage is not None:
            if event.button() == Qt.LeftButton:
                self.__lastMousePos = event.pos()

    def mouseMoveEvent(self, event):
        if self.__enableDrag and self.__originImage is not None and self.__label.geometry().contains(
                self.__lastMousePos):
            if event.buttons() & Qt.LeftButton:
                # 计算鼠标移动的距离
                offset = event.pos() - self.__lastMousePos

                # 更新图片的位置
                self.__label.move(self.__label.pos() + offset)

                self.imgGeometryChange.emit(self.__label.x(),
                                            self.__label.y(),
                                            self.__label.pixmap().width(),
                                            self.__label.pixmap().height())

                # 更新上一次记录的鼠标位置
                self.__lastMousePos = event.pos()

    def moveLabelToCenter(self):
        self.__label.move((self.view.width() - self.__label.width()) // 2,
                          (self.view.height() - self.__label.height()) // 2)

    def __updateInfoLabel(self):
        if self.__originImage is not None:
            self.infoChange.emit(
                f"{self.__originImage.width()}x{self.__originImage.height()}, "
                f"{self.__originImageScaleFactor * 100:.1f}%"
            )
        else:
            self.infoChange.emit("")

    def setPreferredImageSize(self):
        if self.__originImage is not None:
            widthScale = self.view.width() / self.__originImage.width()
            heightScale = self.view.height() / self.__originImage.height()
            self.__originImageScaleFactor = widthScale if widthScale < heightScale else heightScale

            self.__label.setPixmap(
                QPixmap.fromImage(self.__originImage).scaled(self.__originImage.width() * self.__originImageScaleFactor,
                                                             self.__originImage.width() * self.__originImageScaleFactor,
                                                             Qt.KeepAspectRatio,
                                                             Qt.FastTransformation))

            self.__label.setGeometry(QtCore.QRect(0,
                                                  (self.view.height() - self.__label.pixmap().height()) // 2,
                                                  self.__label.pixmap().width(),
                                                  self.__label.pixmap().height()))

            self.imgGeometryChange.emit(self.__label.x(),
                                        self.__label.y(),
                                        self.__label.pixmap().width(),
                                        self.__label.pixmap().height())

            self.__updateInfoLabel()

    def updateImgGeometry(self, x: int, y: int, width: int, height: int):
        if self.__originImage is not None:
            self.__originImageScaleFactor = width / self.__originImage.width()
            self.__label.setPixmap(
                QPixmap.fromImage(self.__originImage).scaled(width,
                                                             height,
                                                             Qt.KeepAspectRatio,
                                                             Qt.FastTransformation))
            self.__label.setGeometry(QtCore.QRect(x,
                                                  y,
                                                  width,
                                                  height))

            self.__updateInfoLabel()

    def __onThemeChanged(self, theme):
        if self.__url is None:
            if self.__enableDrop:
                self.dispIcon(FluentIcon.ADD)
            else:
                self.dispIcon(FluentIcon.PHOTO)
        elif os.path.isdir(self.__url):
            self.dispIcon(FluentIcon.FOLDER)

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
