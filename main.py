import sys
from PyQt5.QtWidgets import QApplication

from app.view.mainWindow import MainWindow


def main():
    # 创建一个 PyQt 应用程序
    app = QApplication(sys.argv)

    # 创建主窗口
    window = MainWindow()

    # 显示主窗口
    window.show()

    # 运行应用程序事件循环
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
