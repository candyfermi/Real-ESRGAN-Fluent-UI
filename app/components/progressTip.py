# coding:utf-8
from PyQt5.QtCore import QPropertyAnimation, Qt, QTimer, pyqtSignal, QPoint, QRectF
from PyQt5.QtGui import QPainter
from PyQt5.QtWidgets import QLabel, QWidget, QToolButton, QGraphicsOpacityEffect
from qfluentwidgets import isDarkTheme, Theme, FluentIcon, ProgressBar

from app.common.styleSheet import StyleSheet


class StateCloseButton(QToolButton):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(12, 12)
        self.isPressed = False
        self.isEnter = False

    def enterEvent(self, e):
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        self.isEnter = False
        self.isPressed = False
        self.update()

    def mousePressEvent(self, e):
        self.isPressed = True
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.isPressed = False
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        if self.isPressed:
            painter.setOpacity(0.6)
        elif self.isEnter:
            painter.setOpacity(0.8)

        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT
        FluentIcon.CLOSE.render(painter, self.rect(), theme)


class ProgressTip(QWidget):
    """ State tooltip """

    closedSignal = pyqtSignal()

    def __init__(self, title, parent=None):
        """
        Parameters
        ----------
        title: str
            title of tooltip

        parant:
            parent window
        """
        super().__init__(parent)
        self.title = title

        self.titleLabel = QLabel(self.title, self)
        self.rotateTimer = QTimer(self)
        self.progressBar = ProgressBar(self)

        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.animation = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.closeButton = StateCloseButton(self)

        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 20

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setGraphicsEffect(self.opacityEffect)
        self.opacityEffect.setOpacity(1)
        self.rotateTimer.setInterval(50)

        self.progressBar.setFixedWidth(max(self.titleLabel.width(), 128))

        # connect signal to slot
        self.closeButton.clicked.connect(self.__onCloseButtonClicked)
        self.rotateTimer.timeout.connect(self.__rotateTimerFlowSlot)

        self.__setQss()
        self.__initLayout()

        self.rotateTimer.start()

    def __initLayout(self):
        """ initialize layout """
        self.setFixedSize(self.progressBar.width() + 56, 51)
        self.titleLabel.move(32, 9)
        self.progressBar.move(12, 32)
        self.closeButton.move(self.width() - 24, 19)

    def __setQss(self):
        """ set style sheet """
        self.titleLabel.setObjectName("titleLabel")

        StyleSheet.PROGRESS_TIP.apply(self)

        self.titleLabel.adjustSize()

    def setTitle(self, title: str):
        """ set the title of tooltip """
        self.title = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setState(self, isDone=False):
        """ set the state of tooltip """
        self.isDone = isDone
        self.update()
        if isDone:
            QTimer.singleShot(1000, self.__fadeOut)

    def __onCloseButtonClicked(self):
        """ close button clicked slot """
        self.closedSignal.emit()
        self.hide()

    def __fadeOut(self):
        """ fade out """
        self.rotateTimer.stop()
        self.animation.setDuration(200)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def __rotateTimerFlowSlot(self):
        """ rotate timer time out slot """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def getSuitablePos(self):
        """ get suitable position in main window """
        for i in range(10):
            dy = i*(self.height() + 16)
            pos = QPoint(self.parent().width() - self.width() - 20, 60+dy)
            widget = self.parent().childAt(pos + QPoint(2, 2))
            if isinstance(widget, ProgressTip) and widget is not self:
                pos += QPoint(0, self.height() + 16)
            else:
                break

        return pos

    def setProgress(self, progress: float):
        self.progressBar.setVal(progress)

    def paintEvent(self, e):
        """ paint state tooltip """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        theme = Theme.DARK if isDarkTheme() else Theme.LIGHT

        if not self.isDone:
            painter.translate(19, 18)
            painter.rotate(self.rotateAngle)
            FluentIcon.SYNC.render(painter, QRectF(-8, -8, 16, 16), theme)
            self.progressBar.paintEvent(e)
        else:
            FluentIcon.COMPLETED.render(painter, QRectF(11, 10, 16, 16), theme)
            self.progressBar.setVal(100)
            self.progressBar.paintEvent(e)

