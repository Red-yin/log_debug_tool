"""
#功能说明：运行后显示弹窗，鼠标点击文件后，获取到文件路径
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
app = QApplication([])
fileDir = QFileDialog.getOpenFileNames(QMainWindow(), "test")
print(fileDir)
"""
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QDesktopWidget
import sys
from PySide2.QtGui import QIcon

from window_xmind2json import Window_Xmind2json

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("test")
        self.setGeometry(300, 300, 800, 600)
        self.center()
        self.create_menu()
        self.show()

    def create_menu(self):
        mainMenu = self.menuBar()
        menuFunc = mainMenu.addMenu("功能")
        
        action_xmind2json = QAction("xmind转json", self)
        menuFunc.addAction(action_xmind2json)

        action_xmind2json.triggered.connect(self.run_xmind2json)
        self.window_xmind2json = Window_Xmind2json()

    def run_xmind2json(self):
        self.window_xmind2json.ui.show()

    #设置主窗帘位置到屏幕中央
    def center(self):
        qRect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.move(qRect.topLeft())

myApp = QApplication([])
window = Window()
myApp.exec_()