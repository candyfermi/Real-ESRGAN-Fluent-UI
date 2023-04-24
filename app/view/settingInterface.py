# coding:utf-8
from qfluentwidgets import (SettingCardGroup, SwitchSettingCard, FolderListSettingCard,
                            OptionsSettingCard, PushSettingCard,
                            HyperlinkCard, PrimaryPushSettingCard, ScrollArea,
                            ComboBoxSettingCard, ExpandLayout, Theme, CustomColorSettingCard,
                            setTheme, setThemeColor, RangeSettingCard, isDarkTheme, FluentIcon)
from qfluentwidgets import InfoBar
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLabel, QFileDialog

from app.common.config import cfg, AUTHOR, VERSION, YEAR, REPO_URL
from app.common.styleSheet import StyleSheet


class SettingInterface(ScrollArea):

    tmpFolderChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.scrollWidget = QWidget()
        self.expandLayout = ExpandLayout(self.scrollWidget)

        self.settingLabel = QLabel(self.tr("设置"), self)

        # 临时文件存储位置
        self.tmpFolderGroup = SettingCardGroup(
            self.tr("临时文件存储位置"), self.scrollWidget
        )
        self.tmpFolderCard = PushSettingCard(
            self.tr("选择一个目录"),
            FluentIcon.FOLDER,
            self.tr("程序输出将临时存储到此目录，若生成后没有执行移动操作则可以到此目录查看"),
            cfg.get(cfg.tmpFolder),
            self.tmpFolderGroup
        )

        # 个性化
        self.personalizationGroup = SettingCardGroup(
            self.tr("个性化"), self.scrollWidget
        )
        self.themeCard = OptionsSettingCard(
            cfg.themeMode,
            FluentIcon.BRUSH,
            self.tr("应用主题"),
            self.tr("更改应用程序的外观"),
            texts=[
                self.tr("浅色"),
                self.tr("深色"),
                self.tr("跟随系统")
            ],
            parent=self.personalizationGroup
        )
        self.themeColorCard = CustomColorSettingCard(
            cfg.themeColor,
            FluentIcon.PALETTE,
            self.tr("主题颜色"),
            self.tr("更改应用程序的主题色"),
            self.personalizationGroup
        )
        self.zoomCard = OptionsSettingCard(
            cfg.dpiScale,
            FluentIcon.ZOOM,
            self.tr("界面缩放"),
            self.tr("调整部件和字体的大小"),
            texts=[
                "100%",
                "125%",
                "150%",
                "175%",
                "200%",
                self.tr("跟随系统")
            ],
            parent=self.personalizationGroup
        )
        self.languageCard = ComboBoxSettingCard(
            cfg.language,
            FluentIcon.LANGUAGE,
            self.tr('语言'),
            self.tr('选择界面的显示语言'),
            texts=[
                '简体中文',
                '繁體中文',
                'English',
                self.tr('跟随系统')
            ],
            parent=self.personalizationGroup
        )

        # 关于
        self.aboutGroup = SettingCardGroup(
            self.tr("关于"), self.scrollWidget
        )
        self.aboutCard = PrimaryPushSettingCard(
            self.tr("查看代码"),
            FluentIcon.INFO,
            self.tr("关于"),
            '© ' + self.tr('Copyright') + f" {YEAR}, {AUTHOR}. " +
            self.tr('Version') + f" {VERSION[1:]}",
            self.aboutGroup
        )

        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)

        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 80, 0, 20)
        self.setWidget(self.scrollWidget)
        self.setWidgetResizable(True)

        self.scrollWidget.setObjectName('scrollWidget')
        self.settingLabel.setObjectName('settingLabel')
        StyleSheet.SETTING_INTERFACE.apply(self)

        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        self.settingLabel.move(36, 30)

        self.tmpFolderGroup.addSettingCard(self.tmpFolderCard)

        self.personalizationGroup.addSettingCard(self.themeCard)
        self.personalizationGroup.addSettingCard(self.themeColorCard)
        self.personalizationGroup.addSettingCard(self.zoomCard)
        self.personalizationGroup.addSettingCard(self.languageCard)

        self.aboutGroup.addSettingCard(self.aboutCard)

        self.expandLayout.setSpacing(28)
        self.expandLayout.setContentsMargins(36, 10, 36, 0)
        self.expandLayout.addWidget(self.tmpFolderGroup)
        self.expandLayout.addWidget(self.personalizationGroup)
        self.expandLayout.addWidget(self.aboutGroup)

    def __showRestartTooltip(self):
        InfoBar.success(
            self.tr("更改成功"),
            self.tr("更改将在下次重启后生效"),
            duration=1500,
            parent=self
        )

    def __onTmpFolderCardClicked(self):
        folder = QFileDialog.getExistingDirectory(
            self,
            self.tr("选择一个目录"),
            "./"
        )
        if not folder or cfg.get(cfg.tmpFolder) == folder:
            return

        cfg.set(cfg.tmpFolder, folder)
        self.tmpFolderCard.setContent(folder)

    def __connectSignalToSlot(self):
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(setTheme)

        self.tmpFolderCard.clicked.connect(
            self.__onTmpFolderCardClicked
        )

        self.themeColorCard.colorChanged.connect(setThemeColor)

        self.aboutCard.clicked.connect(
            lambda: QDesktopServices.openUrl(QUrl(REPO_URL))
        )