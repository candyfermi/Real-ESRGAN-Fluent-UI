import os.path
import re
import shutil

from PyQt5.QtCore import pyqtSignal, Qt, QTimer, QThread, QUrl
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QFrame, QWidget, QHBoxLayout, QVBoxLayout, QLabel, QGridLayout, QFileDialog
from qfluentwidgets import (ScrollArea, PushButton, FluentIcon, LineEdit, ToolButton, MessageDialog, InfoBar,
                            InfoBarPosition)

from app.common.config import cfg
from app.common.styleSheet import StyleSheet
from app.componets.imageBox import ImageBox
from app.componets.paramsDialog import ParamsDialog
from app.componets.progressTip import ProgressTip
from process.realesrganProcess import realesrganProcess

from app.common import resource


class ProcessThread(QThread):
    done = pyqtSignal(bool, str)
    progressChange = pyqtSignal(float)

    def __init__(self, inputPath: str, outputPath: str):
        super().__init__()
        self.__inputPath = inputPath
        self.__outputPath = outputPath
        self.__stopFlag = False

    def run(self):
        if os.path.isdir(self.__inputPath) and not os.path.exists(self.__outputPath):
            os.mkdir(self.__outputPath)

        p = realesrganProcess(
            f"\"{self.__inputPath}\"",
            f"\"{self.__outputPath}\"",
            modelName=cfg.modelName.value,
            enableTTA=cfg.modelEnableTTA.value,
            outputFormat=None if cfg.modelFormat.value == "Auto" else cfg.modelFormat.value
        )
        pattern = r'(\d+\.\d+)%'

        while p.poll() is None:
            if self.__stopFlag:
                p.kill()
                p.wait()
                return
            else:
                line = p.stdout.readline()
                line = line.strip()
                if line:
                    match = re.search(pattern, line.decode())
                    if match:
                        percentage = match.group(1)
                        self.progressChange.emit(float(percentage))
        if p.returncode == 0:
            self.done.emit(True, self.__outputPath)
        else:
            self.done.emit(False, "")

    def stop(self):
        self.__stopFlag = True


class ImageProcessInterface(ScrollArea):
    processDone = pyqtSignal(bool)

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
        self.rightImgOutputLayout = QGridLayout(self.imgGridLayout.widget())
        self.consoleGridLayout = QGridLayout(self.vBoxLayout.widget())

        self.leftImgBox = ImageBox(self.imgGridLayout.widget(), True)
        self.rightImgBox = ImageBox(self.imgGridLayout.widget(), False)

        self.leftImgInfoWidget = QWidget(self.imgGridLayout.widget())
        self.leftImgInfoLabel = QLabel(self.leftImgInfoWidget)
        self.leftImgInfoLabel.setObjectName("infoLabel")
        self.rightImgInfoWidget = QWidget(self.imgGridLayout.widget())
        self.rightImgInfoLabel = QLabel(self.rightImgInfoWidget)
        self.rightImgInfoLabel.setObjectName("infoLabel")

        self.leftImgInput = LineEdit(self.leftImgInputLayout.widget())
        self.leftImgInput.setPlaceholderText(self.tr("选择一张图片或一个目录"))
        self.leftImgInput.setClearButtonEnabled(True)

        self.leftImgInputImageButton = ToolButton(self.leftImgInputLayout.widget())
        self.leftImgInputImageButton.setIcon(FluentIcon.PHOTO)
        self.leftImgInputImageButton.setToolTip(self.tr("选择一张图片"))
        self.leftImgInputDirButton = ToolButton(self.leftImgInputLayout.widget())
        self.leftImgInputDirButton.setIcon(FluentIcon.FOLDER)
        self.leftImgInputDirButton.setToolTip(self.tr("选择一个目录"))

        self.rightImgPathLine = LineEdit(self.rightImgOutputLayout.widget())
        self.rightImgPathLine.setEnabled(False)

        self.rightImgOutputSaveButton = ToolButton(self.rightImgOutputLayout.widget())
        self.rightImgOutputSaveButton.setIcon(FluentIcon.SAVE_AS)
        self.rightImgOutputSaveButton.setToolTip(self.tr("将结果移动到"))
        self.rightImgPathOpenButton = ToolButton(self.rightImgOutputLayout.widget())
        self.rightImgPathOpenButton.setIcon(FluentIcon.FOLDER)
        self.rightImgPathOpenButton.setToolTip(self.tr("打开输出文件临时存储目录"))
        self.rightImgOutputSaveButton.setEnabled(False)

        self.separator = QFrame(self.vBoxLayout.widget())
        self.separator.setFrameShape(QFrame.HLine)
        self.separator.setObjectName("separator")

        self.paramsButton = PushButton(self.tr("调整参数"), self.consoleGridLayout.widget(), FluentIcon.MORE)

        self.processButton = PushButton(self.tr("开始"), self.consoleGridLayout.widget(), FluentIcon.SEND_FILL)

        self.__processThread = None

        self.progressTip = None

        self.__initWidget()

    def __initWidget(self):
        self.__initLayout()

        self.leftImgInfoWidget.setFixedHeight(25)
        self.leftImgInfoLabel.setMinimumWidth(200)
        self.rightImgInfoWidget.setFixedHeight(25)
        self.rightImgInfoLabel.setMinimumWidth(200)

        self.imgGridLayout.addWidget(self.leftImgBox, 0, 0, 1, 1)
        self.imgGridLayout.addWidget(self.leftImgInfoWidget, 1, 0, 1, 1)
        self.imgGridLayout.addLayout(self.leftImgInputLayout, 2, 0, 1, 1)

        spaceItem = QWidget(self.imgGridLayout.widget())
        spaceItem.setFixedWidth(10)
        self.imgGridLayout.addWidget(spaceItem, 0, 2, 3, 1)

        self.imgGridLayout.addWidget(self.rightImgBox, 0, 3, 1, 1)
        self.imgGridLayout.addWidget(self.rightImgInfoWidget, 1, 3, 1, 1)
        self.imgGridLayout.addLayout(self.rightImgOutputLayout, 2, 3, 1, 1)

        self.leftImgInputLayout.addWidget(self.leftImgInput, 0, 0, 1, 3)
        self.leftImgInputLayout.addWidget(self.leftImgInputImageButton, 0, 3, 1, 1)
        self.leftImgInputLayout.addWidget(self.leftImgInputDirButton, 0, 4, 1, 1)

        self.rightImgOutputLayout.addWidget(self.rightImgPathLine, 0, 0, 1, 3)
        self.rightImgOutputLayout.addWidget(self.rightImgOutputSaveButton, 0, 3, 1, 1)
        self.rightImgOutputLayout.addWidget(self.rightImgPathOpenButton, 0, 4, 1, 1)

        self.consoleGridLayout.addWidget(self.paramsButton)
        self.consoleGridLayout.addWidget(self.processButton)

        self.vBoxLayout.addLayout(self.imgGridLayout)
        self.vBoxLayout.addWidget(self.separator)
        self.vBoxLayout.addLayout(self.consoleGridLayout)

        self.__connectSignalToSlot()

    def __initLayout(self):
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)
        self.imgGridLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)
        self.consoleGridLayout.setSizeConstraint(QHBoxLayout.SetMinimumSize)

        self.vBoxLayout.setContentsMargins(20, 20, 20, 20)

        self.imgGridLayout.setContentsMargins(0, 0, 0, 10)
        self.imgGridLayout.setSpacing(5)

        self.leftImgInputLayout.setContentsMargins(0, 5, 0, 0)
        self.leftImgInputLayout.setSpacing(5)

        self.rightImgOutputLayout.setContentsMargins(0, 5, 0, 0)
        self.rightImgOutputLayout.setSpacing(5)

        self.consoleGridLayout.setContentsMargins(0, 10, 0, 0)
        self.consoleGridLayout.setSpacing(10)

    def __connectSignalToSlot(self):
        self.leftImgInput.textChanged.connect(self.__onInputUrlChanged)
        self.leftImgBox.dropSignal.connect(self.__onInputDrop)

        self.leftImgInputImageButton.clicked.connect(self.__openSelectInputImageDialog)
        self.leftImgInputDirButton.clicked.connect(self.__openSelectInputDirDialog)

        self.rightImgPathOpenButton.clicked.connect(self.__openTmpDir)
        self.rightImgOutputSaveButton.clicked.connect(self.__saveOutput)

        self.leftImgBox.infoChange.connect(self.__onLeftImgInfoChanged)
        self.rightImgBox.infoChange.connect(self.__onRightImgInfoChange)
        self.leftImgBox.imgGeometryChange.connect(self.rightImgBox.updateImgGeometry)
        self.rightImgBox.imgGeometryChange.connect(self.leftImgBox.updateImgGeometry)

        self.paramsButton.clicked.connect(self.__changeParams)
        self.processButton.clicked.connect(self.__startProcess)

    def isProcessing(self):
        return self.__processThread is not None

    def __openSelectInputImageDialog(self):
        fileDialog = QFileDialog()
        fileDialog.setFileMode(QFileDialog.ExistingFile)
        fileDialog.setWindowTitle(self.tr("选择一张图片"))
        fileDialog.setNameFilter(self.tr("图片文件 (*.jpg *.jpeg *.png *.bmp *.webp)"))
        fileDialog.setDirectory(".")
        if fileDialog.exec_():
            urls = fileDialog.selectedUrls()
            self.leftImgInput.setText(urls[0].toLocalFile())

    def __openSelectInputDirDialog(self):
        url = QFileDialog.getExistingDirectory(self,
                                               self.tr("选择一个目录"),
                                               "")
        if url:
            self.leftImgInput.setText(url)

    def __openTmpDir(self):
        QDesktopServices.openUrl(QUrl.fromLocalFile(cfg.get(cfg.tmpFolder)))

    def __saveOutput(self):
        if self.rightImgBox.url() is not None:
            sourceUrl = self.rightImgBox.url()
            if os.path.isfile(sourceUrl):
                fileDialog = QFileDialog()
                fileDialog.setAcceptMode(QFileDialog.AcceptSave)
                fileDialog.setFileMode(QFileDialog.AnyFile)
                destUrl, _ = fileDialog.getSaveFileName(self,
                                                        self.tr("另存为"),
                                                        os.path.basename(sourceUrl),
                                                        self.tr("图片 (*.jpg *.jpeg *.png *.bmp *.webp)"))
                if destUrl:
                    shutil.move(sourceUrl, destUrl)
                    InfoBar.success(
                        title=self.tr("保存成功"),
                        content=self.tr("将图片保存至: ") + destUrl,
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )
            else:
                destUrl = QFileDialog.getExistingDirectory(self,
                                                           self.tr("保存到"),
                                                           os.path.basename(sourceUrl),
                                                           QFileDialog.ShowDirsOnly)
                if destUrl:
                    shutil.move(sourceUrl, destUrl)
                    InfoBar.success(
                        title=self.tr("保存成功"),
                        content=self.tr("将目录保存至: ") + destUrl,
                        orient=Qt.Horizontal,
                        isClosable=True,
                        position=InfoBarPosition.TOP,
                        duration=2000,
                        parent=self
                    )

    def __onInputUrlChanged(self, text):
        if len(text) == 0:
            self.leftImgBox.clearImage()
        else:
            self.leftImgBox.setImage(text)
        self.rightImgBox.clearImage()
        self.rightImgPathLine.setText("")
        self.rightImgOutputSaveButton.setEnabled(False)

    def __onInputDrop(self, url):
        self.leftImgInput.setText(url)

    def __onLeftImgInfoChanged(self, info):
        self.leftImgInfoLabel.setText(info)

    def __onRightImgInfoChange(self, info):
        self.rightImgInfoLabel.setText(info)

    def __lockInputAndOutput(self, lock: bool):
        self.paramsButton.setEnabled(not lock)
        self.processButton.setEnabled(not lock)
        self.leftImgBox.setLock(lock)
        self.leftImgInput.setEnabled(not lock)
        self.leftImgInputImageButton.setEnabled(not lock)
        self.leftImgInputDirButton.setEnabled(not lock)
        self.rightImgOutputSaveButton.setEnabled(not lock)

    def __changeParams(self):
        paramsDialog = ParamsDialog(self.tr("调整参数"), self.window())
        paramsDialog.exec()

    def __startProcess(self):
        url = self.leftImgBox.url()
        if url is not None:
            self.progressTip = ProgressTip(self.tr("正在处理"), self.window())
            self.progressTip.closeButton.clicked.connect(self.__stopProcessConfirm)
            self.progressTip.move(self.progressTip.getSuitablePos())
            self.progressTip.show()
            self.__lockInputAndOutput(True)
            outputPath = f"{cfg.get(cfg.tmpFolder)}/{os.path.basename(url)}"
            outputPathWtoExt, origExt = os.path.splitext(outputPath)
            outputPath = f"{outputPathWtoExt}_4X{origExt}"
            if cfg.modelFormat.value != "Auto":
                outputPath = f"{outputPathWtoExt}_4X.{cfg.modelFormat.value}"
            self.__processThread = ProcessThread(url, outputPath)
            self.__processThread.done.connect(self.__onProcessDone)
            self.__processThread.progressChange.connect(self.__onProcessProgressChanged)
            self.__processThread.start()

    def __onProcessDone(self, success: bool, outputPath: str):
        self.progressTip.closeButton.clicked.disconnect(self.__stopProcessConfirm)
        self.progressTip.setState(True)
        self.progressTip = None
        if success:
            QTimer.singleShot(1000, lambda: self.rightImgBox.setImage(outputPath))
            QTimer.singleShot(1000, lambda: self.rightImgPathLine.setText(outputPath))
            QTimer.singleShot(1000, lambda: self.rightImgOutputSaveButton.setEnabled(True))
            QTimer.singleShot(1000, lambda: InfoBar.success(
                title=self.tr("处理完成"),
                content=self.tr("快看看吧，别忘了保存结果哦"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            ))
        else:
            QTimer.singleShot(1000, lambda: InfoBar.error(
                title=self.tr("糟糕"),
                content=self.tr("出错了"),
                orient=Qt.Horizontal,
                isClosable=True,
                position=InfoBarPosition.TOP,
                duration=2000,
                parent=self
            ))
        self.processDone.emit(success)
        self.__processThread.done.disconnect(self.__onProcessDone)
        self.__processThread.progressChange.disconnect(self.__onProcessProgressChanged)
        self.__processThread = None
        self.__lockInputAndOutput(False)

    def __onProcessProgressChanged(self, progress: float):
        if self.progressTip is not None:
            self.progressTip.setTitle(self.tr("正在处理") + f": {progress}%")
            self.progressTip.setProgress(progress)

    def __stopProcessConfirm(self):
        if self.isProcessing():
            closeDialog = MessageDialog(self.tr("停止处理"),
                                        self.tr("图像处理进程正在后台运行，此时停止可能导致结果丢失，确定要停止吗"),
                                        self.window())
            closeDialog.yesButton.clicked.connect(self.stopProcess)
            closeDialog.cancelButton.clicked.connect(lambda: self.progressTip.show())
            closeDialog.exec()

    def stopProcess(self):
        if self.__processThread is not None:
            self.__processThread.stop()
            self.__processThread.done.disconnect(self.__onProcessDone)
            self.__processThread.progressChange.disconnect(self.__onProcessProgressChanged)
            self.__processThread.quit()
            self.__processThread.wait()
            self.__processThread = None
            self.progressTip.closeButton.clicked.disconnect(self.__stopProcessConfirm)
            self.progressTip = None
            self.__lockInputAndOutput(False)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self.progressTip is not None:
            self.progressTip.move(self.progressTip.getSuitablePos())

