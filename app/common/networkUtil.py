from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtGui import QImage
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest


class ImageDownloader(QNetworkAccessManager):
    downloadFinished = pyqtSignal(QImage)
    downloadError = pyqtSignal(str)
    downloadProgressChanged = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.networkReply = None

    def downloadImage(self, src):
        url = QUrl(src)
        requests = QNetworkRequest(url)
        self.networkReply = self.get(requests)
        self.networkReply.downloadProgress.connect(self.onDownloadProgress)
        self.finished.connect(self.onDownloadFinished)

    def onDownloadFinished(self, reply):
        if self.networkReply.error() == QNetworkReply.NoError:
            data = self.networkReply.readAll()
            image = QImage()
            if image.loadFromData(data):
                self.downloadFinished.emit(image)
            else:
                self.downloadError.emit(f"Error Loading Image: {self.networkReply.url().url()}")
        else:
            self.downloadError.emit(
                f"Error Downloading Image: {self.networkReply.url().url()} {self.networkReply.error()}"
            )
        self.networkReply.downloadProgress.disconnect(self.onDownloadProgress)
        self.finished.disconnect(self.onDownloadFinished)

    def onDownloadProgress(self, bytesReceived: int, bytesTotal: int):
        self.downloadProgressChanged.emit(bytesReceived, bytesTotal)
