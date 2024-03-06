import os

from PyQt5 import QtCore
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QSizePolicy, QVBoxLayout
from PyQt5.QtGui import QPixmap, QImage, QDropEvent
from PyQt5.QtCore import Qt, QMimeData, pyqtSignal, QBuffer, QIODevice, QUrl, QPoint
from qfluentwidgets import FluentIcon, Theme, RoundMenu, Action, MenuAnimationType
import hashlib
from bs4 import BeautifulSoup

from app.common.config import cfg
from app.common.networkUtil import ImageDownloader


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
        self.__lastMousePos = QPoint(self.view.x() // 2, self.view.y() // 2)

        self.clipboard = QApplication.clipboard()
        self.setFocusPolicy(Qt.StrongFocus)

        self.imageDownloader = ImageDownloader()

    def url(self):
        return self.__url

    def lock(self):
        return self.__lock

    def setLock(self, lock: bool):
        self.__lock = lock

    def setImage(self, url: str | bytes | os.PathLike[str] | os.PathLike[bytes]):
        if self.__lock:
            return
        if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", "jpeg", ".png", ".bmp", ".webp"]:
            self.__url = url
            self.__originImage = QImage(url)
            self.__label.setPixmap(QPixmap.fromImage(self.__originImage))
            self.__label.setGeometry(
                QtCore.QRect(
                    0,
                    0,
                    self.__label.pixmap().width(),
                    self.__label.pixmap().height()
                )
            )
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

    # 直接输入QImage, 先存到tmp目录, 目前统一保存为png格式
    def __setImageFromImage(self, image: QImage) -> bool:
        if self.__lock:
            return False
        # 计算图片数据的MD5作为文件名
        buffer = QBuffer()
        buffer.open(QIODevice.ReadWrite)
        image.save(buffer, format="PNG")
        md5 = hashlib.md5(buffer.data()).hexdigest()
        url = f"{cfg.get(cfg.tmpFolder)}/{md5.lower()}.png"
        if image.save(url, format="PNG"):
            self.__url = url
            self.__originImage = image
            self.__label.setPixmap(QPixmap.fromImage(self.__originImage))
            self.__label.setGeometry(
                QtCore.QRect(
                    0,
                    0,
                    self.__label.pixmap().width(),
                    self.__label.pixmap().height()
                )
            )
            self.__originImageScaleFactor = 1
            self.moveLabelToCenter()
            self.__enableDrag = True
            self.__updateInfoLabel()
            self.dropSignal.emit(url)
            self.setPreferredImageSize()
            return True
        else:
            return False

    def __setImageFromHtml(self, html: str) -> bool:
        if self.__lock:
            return False
        soup = BeautifulSoup(html, "html.parser")
        img = soup.find("img")
        if img is None:
            return False
        src = img.get("src")
        if src is None:
            return False
        self.imageDownloader.downloadImage(src)
        self.imageDownloader.downloadFinished.connect(self.__setImageFromImage)
        self.imageDownloader.downloadError.connect(lambda err: print(err))

    def __setUrls(self, urls: list) -> bool:
        if self.__lock:
            return False
        if len(urls) == 1:
            url = urls[0].toLocalFile()
            if os.path.isfile(url) and os.path.splitext(url)[1] in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                self.__url = url
                self.__originImage = QImage(url)
                self.__label.setPixmap(QPixmap.fromImage(self.__originImage))
                self.__label.setGeometry(
                    QtCore.QRect(
                        0,
                        0,
                        self.__label.pixmap().width(),
                        self.__label.pixmap().height()
                    )
                )
                self.__originImageScaleFactor = 1
                self.moveLabelToCenter()
                self.__enableDrag = True
                self.__updateInfoLabel()
                self.dropSignal.emit(url)
                self.setPreferredImageSize()
                return True
            elif self.__acceptDir and os.path.isdir(url):
                self.__url = url
                self.__originImage = None
                self.__originImageScaleFactor = 1
                self.__enableDrag = False
                self.__label.setPixmap(QPixmap(FluentIcon.FOLDER.path()))
                self.moveLabelToCenter()
                self.__updateInfoLabel()
                self.dropSignal.emit(url)
                return True
            else:
                return False
        else:
            return False

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
        if (
            event.mimeData().hasUrls() or
            event.mimeData().hasImage() or
            event.mimeData().hasHtml()
        ):
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        if self.__lock:
            event.ignore()
            return
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if self.__setUrls(urls):
                event.accept()
                return
        if event.mimeData().hasImage():
            image = QImage(event.mimeData().imageData())
            if self.__setImageFromImage(image):
                event.accept()
                return
        if event.mimeData().hasHtml():
            html = event.mimeData().html()
            if self.__setImageFromHtml(html):
                event.accept()
                return
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
                QPixmap.fromImage(self.__originImage).scaled(
                    int(self.__originImage.width() * self.__originImageScaleFactor),
                    int(self.__originImage.width() * self.__originImageScaleFactor),
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation
                )
            )

            self.__label.setGeometry(
                QtCore.QRect(
                    int(newPosX),
                    int(newPosY),
                    int(self.__label.pixmap().width()),
                    int(self.__label.pixmap().height())
                )
            )

            self.imgGeometryChange.emit(
                self.__label.x(),
                self.__label.y(),
                self.__label.pixmap().width(),
                self.__label.pixmap().height()
            )

            self.__updateInfoLabel()

            event.accept()

    def mousePressEvent(self, event):
        if self.__enableDrag and self.__originImage is not None:
            if event.button() == Qt.LeftButton:
                self.__lastMousePos = event.pos()

    def mouseMoveEvent(self, event):
        if (
            self.__enableDrag and
            self.__originImage is not None and
            self.__label.geometry().contains(self.__lastMousePos)
        ):
            if event.buttons() & Qt.LeftButton:
                # 计算鼠标移动的距离
                offset = event.pos() - self.__lastMousePos

                # 更新图片的位置
                self.__label.move(self.__label.pos() + offset)

                self.imgGeometryChange.emit(
                    self.__label.x(),
                    self.__label.y(),
                    self.__label.pixmap().width(),
                    self.__label.pixmap().height()
                )

                # 更新上一次记录的鼠标位置
                self.__lastMousePos = event.pos()

    # 快捷键
    def keyPressEvent(self, e):
        if e.modifiers() == Qt.ControlModifier:
            if e.key() == Qt.Key_C and self.__originImage is not None:
                self.copyImage()
            elif (
                e.key() == Qt.Key_V and
                self.__enableDrop and
                (
                    self.clipboard.mimeData().hasImage() or
                    self.clipboard.mimeData().hasUrls() or
                    self.clipboard.mimeData().hasHtml()
                ) and
                not self.lock()
            ):
                self.pasteImage()
        e.accept()

    def contextMenuEvent(self, e):
        menu = RoundMenu(parent=self)

        resizeAction = Action(FluentIcon.ZOOM, self.tr("调整至合适大小"))
        resizeAction.triggered.connect(self.setPreferredImageSize)
        if self.__originImage is None:
            resizeAction.setEnabled(False)

        copyAction = Action(FluentIcon.COPY, self.tr("复制"))
        copyAction.triggered.connect(self.copyImage)
        if self.__originImage is None:
            copyAction.setEnabled(False)

        pasteAction = Action(FluentIcon.PASTE, self.tr("粘贴"))
        pasteAction.triggered.connect(self.pasteImage)
        if (
            not self.__enableDrop or
            not (
                self.clipboard.mimeData().hasImage() or
                self.clipboard.mimeData().hasUrls() or
                self.clipboard.mimeData().hasHtml()
            ) or
            self.lock()
        ):
            pasteAction.setEnabled(False)

        menu.addAction(copyAction)
        menu.addAction(pasteAction)
        menu.addSeparator()
        menu.addAction(resizeAction)

        menu.exec(e.globalPos(), aniType=MenuAnimationType.DROP_DOWN)

    def moveLabelToCenter(self):
        self.__label.move(
            (self.view.width() - self.__label.width()) // 2,
            (self.view.height() - self.__label.height()) // 2
        )

    def __updateInfoLabel(self):
        if self.__originImage is not None:
            self.infoChange.emit(
                f"{self.__originImage.width()}x{self.__originImage.height()}, "
                f"{self.__originImageScaleFactor * 100:.1f}%"
            )
        else:
            self.infoChange.emit("")

    def copyImage(self):
        if self.__originImage is not None:
            mimeData = QMimeData()
            mimeData.setUrls([QUrl.fromLocalFile(self.__url)])
            self.clipboard.setMimeData(mimeData)

    def pasteImage(self):
        if self.__enableDrop is True:
            if self.clipboard.mimeData().hasUrls():
                urls = self.clipboard.mimeData().urls()
                if self.__setUrls(urls):
                    return
            if self.clipboard.mimeData().hasImage():
                image = QImage(self.clipboard.mimeData().imageData())
                if self.__setImageFromImage(image):
                    return
            if self.clipboard.mimeData().hasHtml():
                html = self.clipboard.mimeData().html()
                if self.__setImageFromHtml(html):
                    return

    def setPreferredImageSize(self):
        if self.__originImage is not None:
            widthScale = self.view.width() / self.__originImage.width()
            heightScale = self.view.height() / self.__originImage.height()
            self.__originImageScaleFactor = widthScale if widthScale < heightScale else heightScale

            self.__label.setPixmap(
                QPixmap.fromImage(self.__originImage).scaled(
                    int(self.__originImage.width() * self.__originImageScaleFactor),
                    int(self.__originImage.width() * self.__originImageScaleFactor),
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation
                )
            )

            self.__label.setGeometry(
                QtCore.QRect(
                    0,
                    (self.view.height() - self.__label.pixmap().height()) // 2,
                    self.__label.pixmap().width(),
                    self.__label.pixmap().height()
                )
            )

            self.imgGeometryChange.emit(
                self.__label.x(),
                self.__label.y(),
                self.__label.pixmap().width(),
                self.__label.pixmap().height()
            )

            self.__updateInfoLabel()

    def updateImgGeometry(self, x: int, y: int, width: int, height: int):
        if self.__originImage is not None:
            self.__originImageScaleFactor = width / self.__originImage.width()
            self.__label.setPixmap(
                QPixmap.fromImage(self.__originImage).scaled(
                    width,
                    height,
                    Qt.KeepAspectRatio,
                    Qt.FastTransformation
                )
            )
            self.__label.setGeometry(
                QtCore.QRect(
                    x,
                    y,
                    width,
                    height
                )
            )

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
