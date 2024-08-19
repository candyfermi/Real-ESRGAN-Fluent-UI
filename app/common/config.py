from enum import Enum

from PyQt5.QtCore import QLocale
from qfluentwidgets import (qconfig, QConfig, ConfigItem, OptionsConfigItem, BoolValidator, OptionsValidator,
                            RangeConfigItem, RangeValidator, FolderValidator, ConfigSerializer)

from process.modelConst import ModelName


class Language(Enum):
    """ Language enumeration """

    CHINESE_SIMPLIFIED = QLocale(QLocale.Chinese, QLocale.China)
    CHINESE_TRADITIONAL = QLocale(QLocale.Chinese, QLocale.HongKong)
    ENGLISH = QLocale(QLocale.English)
    AUTO = QLocale()


class LanguageSerializer(ConfigSerializer):
    """ Language serializer """

    def serialize(self, language):
        return language.value.name() if language != Language.AUTO else "Auto"

    def deserialize(self, value: str):
        return Language(QLocale(value)) if value != "Auto" else Language.AUTO


class Config(QConfig):
    """ Config of application """

    # folders
    tmpFolder = ConfigItem(
        "Folders", "Temp", "tmp", FolderValidator()
    )

    # 可执行文件目录
    exePos = ConfigItem(
        "Exe", "ExePos", "process/realesrgan-ncnn-vulkan-20220424-windows", FolderValidator()
    )

    # main window
    dpiScale = OptionsConfigItem(
        "MainWindow", "DpiScale", "Auto", OptionsValidator([1, 1.25, 1.5, 1.75, 2, "Auto"]), restart=True
    )
    language = OptionsConfigItem(
        "MainWindow", "Language", Language.AUTO, OptionsValidator(Language), LanguageSerializer(), restart=True
    )

    # 模型参数
    modelFormat = OptionsConfigItem(
        "Model", "Format", "Auto", OptionsValidator(["jpg", "png", "webp", "Auto"])
    )

    modelName = OptionsConfigItem(
        "Model", "ModelName", ModelName.REALESRGAN_X4PLUS.value,
        OptionsValidator([ModelName.REALESRGAN_X4PLUS.value, ModelName.REALESRGAN_X4PLUS_ANIME.value])
    )

    modelEnableTTA = ConfigItem(
        "Model", "EnableTTA", False, BoolValidator()
    )

    # Material
    blurRadius = RangeConfigItem("Material", "AcrylicBlurRadius", 15, RangeValidator(0, 40))

    # software update
    checkUpdateAtStartUp = ConfigItem("Update", "CheckUpdateAtStartUp", True, BoolValidator())


YEAR = 2024
AUTHOR = "Candy Fermi"
VERSION = "v0.1.2"
REPO_URL = "https://github.com/candyfermi/Real-ESRGAN-Fluent-UI"

cfg = Config()
qconfig.load('config/config.json', cfg)
