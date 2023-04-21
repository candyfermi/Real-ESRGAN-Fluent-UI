import sys
from PyQt5.QtWidgets import QApplication

from app.view.mainWindow import MainWindow

# 创建一个 PyQt 应用程序
app = QApplication(sys.argv)

# 创建主窗口
window = MainWindow()
window.setWindowTitle("My PyQt App")

# 显示主窗口
window.show()

# 运行应用程序事件循环
sys.exit(app.exec_())
