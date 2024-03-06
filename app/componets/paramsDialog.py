from typing import Union, List

from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from PyQt5.QtGui import QColor, QIcon
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFrame, QLabel, QPushButton, QHBoxLayout, QButtonGroup
from qfluentwidgets import ScrollArea, ExpandLayout, SettingCardGroup, OptionsSettingCard, FluentIcon, RangeSettingCard, \
    SwitchSettingCard, FluentStyleSheet, PrimaryPushButton, PushButton, ComboBoxSettingCard, RadioButton, \
    FluentIconBase, ExpandSettingCard, OptionsConfigItem, qconfig
from qfluentwidgets.components.dialog_box.mask_dialog_base import MaskDialogBase

from app.common.styleSheet import StyleSheet
from app.common.config import cfg


class MOptionsSettingCard(ExpandSettingCard):
    """ setting card with a group of options """

    optionChanged = pyqtSignal(OptionsConfigItem)

    def __init__(self, configItem, icon: Union[str, QIcon, FluentIconBase], title, content=None, texts=None, tips=None, parent=None):
        """
        Parameters
        ----------
        configItem: OptionsConfigItem
            options config item

        icon: str | QIcon | FluentIconBase
            the icon to be drawn

        title: str
            the title of setting card

        content: str
            the content of setting card

        texts: List[str]
            the texts of radio buttons

        parent: QWidget
            parent window
        """
        super().__init__(icon, title, content, parent)
        self.texts = texts or []
        self.configItem = configItem
        self.configName = configItem.name
        self.choiceLabel = QLabel(self)
        self.buttonGroup = QButtonGroup(self)

        self.addWidget(self.choiceLabel)

        # create buttons
        self.viewLayout.setSpacing(19)
        self.viewLayout.setContentsMargins(48, 18, 0, 18)
        for text, tip, option in zip(texts, tips, configItem.options):
            button = RadioButton(text, self.view)
            button.setToolTip(tip)
            self.buttonGroup.addButton(button)
            self.viewLayout.addWidget(button)
            button.setProperty(self.configName, option)

        self._adjustViewSize()
        self.setValue(qconfig.get(self.configItem))
        configItem.valueChanged.connect(self.setValue)
        self.buttonGroup.buttonClicked.connect(self.__onButtonClicked)

    def __onButtonClicked(self, button: RadioButton):
        """ button clicked slot """
        if button.text() == self.choiceLabel.text():
            return

        value = button.property(self.configName)
        qconfig.set(self.configItem, value)

        self.choiceLabel.setText(button.text())
        self.choiceLabel.adjustSize()
        self.optionChanged.emit(self.configItem)

    def setValue(self, value):
        """ select button according to the value """
        qconfig.set(self.configItem, value)

        for button in self.buttonGroup.buttons():
            isChecked = button.property(self.configName) == value
            button.setChecked(isChecked)

            if isChecked:
                self.choiceLabel.setText(button.text())
                self.choiceLabel.adjustSize()


class MSettingCardGroup(SettingCardGroup):

    def adjustSize(self):
        h = self.cardLayout.heightForWidth(self.width()) + 20
        return self.resize(self.width(), h)


class ParamsCard(ScrollArea):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.view = QWidget()
        self.paramsLayout = ExpandLayout(self.view)

        self.paramsGroup = MSettingCardGroup(
            "", self.view
        )

        self.formatBox = ComboBoxSettingCard(
            cfg.modelFormat,
            FluentIcon.EDIT,
            self.tr("输出格式"),
            self.tr("输出图片的文件格式"),
            texts=[
                "jpg", "png", "webp", self.tr("跟随输入")
            ],
            parent=self.paramsGroup
        )

        self.modelNameBox = MOptionsSettingCard(
            cfg.modelName,
            FluentIcon.BASKETBALL,
            self.tr("模型"),
            self.tr("使用的超分辨率模型"),
            texts=[
                "RealESRGAN-X4Plus",
                "RealESRGAN-X4Plus_Anime"
            ],
            tips=[
                self.tr("4倍超分辨率模型"),
                self.tr("4倍超分辨率模型, 适用于动漫风格图片")
            ],
            parent=self.paramsGroup
        )

        self.enableTTABox = SwitchSettingCard(
            FluentIcon.FONT,
            self.tr("启用TTA模式"),
            self.tr("以8倍处理时间换取微小质量提升"),
            cfg.modelEnableTTA,
            parent=self.paramsGroup
        )

        self.recoverDefaultButton = PushButton(self.tr("恢复默认"), self.view)
        self.recoverDefaultButton.clicked.connect(self.recoverDefault)

        self.__initWidget()

    def __initWidget(self):
        self.setMinimumSize(600, 300)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 0, 0, 0)
        self.setWidget(self.view)
        self.setWidgetResizable(True)

        self.view.setObjectName("view")
        StyleSheet.PARAMS_DIALOG.apply(self)

        self.__initLayout()

    def __initLayout(self):
        self.paramsGroup.titleLabel.setFixedHeight(0)

        self.paramsGroup.addSettingCard(self.formatBox)
        self.paramsGroup.addSettingCard(self.modelNameBox)
        self.paramsGroup.addSettingCard(self.enableTTABox)

        self.paramsLayout.setSpacing(20)
        self.paramsLayout.setContentsMargins(10, 0, 10, 0)
        self.paramsLayout.addWidget(self.paramsGroup)
        self.paramsLayout.addWidget(self.recoverDefaultButton)

    def recoverDefault(self):
        cfg.set(cfg.modelFormat, cfg.modelFormat.defaultValue)
        cfg.set(cfg.modelName, cfg.modelName.defaultValue)
        cfg.set(cfg.modelEnableTTA, cfg.modelEnableTTA.defaultValue)


class ParamsDialog(MaskDialogBase):
    yesSignal = pyqtSignal()

    def __init__(self, title: str, parent=None):
        super().__init__(parent=parent)
        self.paramsCard = ParamsCard(self)
        self._setUpUi(title, self.paramsCard, self.widget)

        self.setShadowEffect(60, (0, 10), QColor(0, 0, 0, 50))
        self.setMaskColor(QColor(0, 0, 0, 76))
        self._hBoxLayout.removeWidget(self.widget)
        self._hBoxLayout.addWidget(self.widget, 1, Qt.AlignCenter)

        self.buttonGroup.setMinimumWidth(280)
        self.widget.setFixedSize(
            max(self.content.width(), self.titleLabel.width()) + 48,
            self.content.y() + self.content.height() + 105
        )

    def eventFilter(self, obj, e: QEvent):
        if obj is self.window():
            if e.type() == QEvent.Resize:
                pass

        return super().eventFilter(obj, e)

    def _setUpUi(self, title, content, parent):
        self.content = content
        # self.content.setParent(parent)
        self.titleLabel = QLabel(title, parent)

        self.buttonGroup = QFrame(parent)
        self.yesButton = PrimaryPushButton(self.tr("确定"), self.buttonGroup)

        self.vBoxLayout = QVBoxLayout(parent)
        self.textLayout = QVBoxLayout()
        self.buttonLayout = QHBoxLayout(self.buttonGroup)

        self.__initWidget()

    def __initWidget(self):
        self.__setQss()
        self.__initLayout()

        # fixes https://github.com/zhiyiYo/PyQt-Fluent-Widgets/issues/19
        self.yesButton.setAttribute(Qt.WA_LayoutUsesWidgetRect)

        self.yesButton.setFocus()
        self.buttonGroup.setFixedHeight(81)

        self.yesButton.clicked.connect(self.__onYesButtonClicked)

    def __initLayout(self):
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(self.textLayout, 1)
        self.vBoxLayout.addWidget(self.buttonGroup, 0, Qt.AlignBottom)
        self.vBoxLayout.setSizeConstraint(QVBoxLayout.SetMinimumSize)

        self.textLayout.setSpacing(12)
        self.textLayout.setContentsMargins(24, 24, 24, 24)
        self.textLayout.addWidget(self.titleLabel, 0, Qt.AlignTop)
        self.textLayout.addWidget(self.content)

        self.buttonLayout.setSpacing(12)
        self.buttonLayout.setContentsMargins(24, 24, 24, 24)
        self.buttonLayout.addWidget(self.yesButton, 1, Qt.AlignVCenter)

    def __onYesButtonClicked(self):
        self.accept()
        self.yesSignal.emit()

    def __setQss(self):
        self.titleLabel.setObjectName("titleLabel")
        self.buttonGroup.setObjectName('buttonGroup')

        FluentStyleSheet.DIALOG.apply(self)

        self.buttonGroup.setStyleSheet("border-bottom-left-radius: 8px;"
                                       "border-bottom-right-radius: 8px;")

        self.yesButton.adjustSize()
