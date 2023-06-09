from PyQt5.QtCore import QEasingCurve, pyqtSignal, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QApplication, QMessageBox
from qfluentwidgets import PopUpAniStackedWidget, NavigationInterface, NavigationItemPosition, MessageBox, FluentIcon, \
    MessageDialog, qrouter, ScrollArea
from qframelesswindow import FramelessWindow

from app.common.signalBus import signalBus
from app.common.styleSheet import StyleSheet
from app.componets.customTitleBar import CustomTitleBar

from app.view.imageProcessInterface import ImageProcessInterface

from app.common import resource
from app.view.settingInterface import SettingInterface


class StackedWidget(QFrame):
    """ Stacked widget """

    currentWidgetChanged = pyqtSignal(QWidget)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.view = PopUpAniStackedWidget(self)

        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.view)

        self.view.currentChanged.connect(
            lambda i: self.currentWidgetChanged.emit(self.view.widget(i)))

    def addWidget(self, widget):
        """ add widget to view """
        self.view.addWidget(widget)

    def setCurrentWidget(self, widget, popOut=False):
        widget.verticalScrollBar().setValue(0)
        if not popOut:
            self.view.setCurrentWidget(widget, duration=300)
        else:
            self.view.setCurrentWidget(
                widget, True, False, 200, QEasingCurve.InQuad)

    def setCurrentIndex(self, index, popOut=False):
        self.setCurrentWidget(self.view.widget(index), popOut)


class MainWindow(FramelessWindow):
    def __init__(self):
        super().__init__()

        self.setTitleBar(CustomTitleBar(self))
        self.hBoxLayout = QHBoxLayout(self)
        self.widgetLayout = QHBoxLayout()

        self.stackWidget = StackedWidget(self)
        self.navigationInterface = NavigationInterface(self, True, True)

        self.imageProcessInterface = ImageProcessInterface(self)
        self.settingInterface = SettingInterface(self)

        # initialize layout
        self.initLayout()

        # add items to navigation interface
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addLayout(self.widgetLayout)
        self.hBoxLayout.setStretchFactor(self.widgetLayout, 1)

        self.widgetLayout.addWidget(self.stackWidget)
        self.widgetLayout.setContentsMargins(0, 48, 0, 0)

        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)
        self.titleBar.raise_()

    def initNavigation(self):
        self.addSubInterface(
            self.imageProcessInterface, "imageProcessInterface", FluentIcon.ZOOM, self.tr("超分辨率"),
            NavigationItemPosition.TOP
        )
        self.addSubInterface(
            self.settingInterface, "settingInterface", FluentIcon.SETTING, self.tr("设置"),
            NavigationItemPosition.BOTTOM
        )

        qrouter.setDefaultRouteKey(self.stackWidget, self.imageProcessInterface.objectName())

        self.stackWidget.currentWidgetChanged.connect(
            lambda w: self.navigationInterface.setCurrentItem(w.objectName())
        )
        self.navigationInterface.setCurrentItem(
            self.imageProcessInterface.objectName()
        )
        self.stackWidget.setCurrentIndex(0)

    def addSubInterface(self, interface: QWidget, objectName: str, icon, text: str,
                        position=NavigationItemPosition.SCROLL):
        interface.setObjectName(objectName)
        self.stackWidget.addWidget(interface)
        self.navigationInterface.addItem(
            routeKey=objectName,
            icon=icon,
            text=text,
            onClick=lambda t: self.switchTo(interface, t),
            position=position
        )

    def initWindow(self):
        self.resize(960, 780)
        self.setMinimumWidth(800)
        self.setMinimumHeight(500)
        self.setWindowIcon(QIcon(':/res/image/icon.png'))
        self.setWindowTitle('RealESRGAN Fluent UI')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w // 2 - self.width() // 2, h // 2 - self.height() // 2)

        StyleSheet.MAIN_WINDOW.apply(self)

    def switchTo(self, widget, triggerByUser=True):
        self.stackWidget.setCurrentWidget(widget, not triggerByUser)

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width() - 46, self.titleBar.height())

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

    def onCurrentWidgetChanged(self, widget: QWidget):
        self.navigationInterface.setCurrentItem(widget.objectName())
        qrouter.push(self.stackWidget, widget.objectName())

    def __close(self):
        self.imageProcessInterface.stopProcess()
        self.close()
