from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QHBoxLayout
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QMimeData, QEasingCurve
from PyQt5.uic.properties import QtGui
from qfluentwidgets import SmoothScrollArea, PixmapLabel
import sys


class ImageBox(SmoothScrollArea):
    def __init__(self, enableDrag=False):
        super().__init__()

        self.label = PixmapLabel(self)

        # customize scroll animation
        self.setScrollAnimation(Qt.Vertical, 400, QEasingCurve.OutQuint)
        self.setScrollAnimation(Qt.Horizontal, 400, QEasingCurve.OutQuint)

        self.horizontalScrollBar().setValue(1900)
        self.setWidget(self.label)
        self.resize(1200, 800)

        self.label.setStyleSheet("QLabel { border: 1px solid black; }")
        self.label.resize(1200, 800)

        if enableDrag:
            self.setAcceptDrops(True)
            self.label.setAcceptDrops(True)

    def dragEnterEvent(self, event):
        print("dragEnter")
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event):
        print("drop")
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            file_path = urls[0].toLocalFile()
            self.label.setPixmap(QPixmap(file_path))

            event.accept()
        else:
            event.ignore()
