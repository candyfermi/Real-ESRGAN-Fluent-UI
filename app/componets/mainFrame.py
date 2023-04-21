from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout

from app.componets.imageBox import ImageBox


class MainFrame(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # upper
        self.upperPart = QHBoxLayout()
        self.upperPart.addWidget(ImageBox(True))
        self.upperPart.addWidget(ImageBox())

        self.layout.addLayout(self.upperPart)

        # lower
        self.lowerPart = QHBoxLayout()



