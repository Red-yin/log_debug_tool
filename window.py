"""
#功能说明：运行后显示弹窗，鼠标点击文件后，获取到文件路径
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
app = QApplication([])
fileDir = QFileDialog.getOpenFileNames(QMainWindow(), "test")
print(fileDir)
"""