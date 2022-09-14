"""
#功能说明：运行后显示弹窗，鼠标点击文件后，获取到文件路径
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
app = QApplication([])
fileDir = QFileDialog.getOpenFileNames(QMainWindow(), "test")
print(fileDir)
"""
from fileinput import filelineno
from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QDesktopWidget
from PySide2.QtWidgets import QBoxLayout, QGridLayout, QVBoxLayout, QHBoxLayout
from PySide2.QtWidgets import QPushButton, QLabel
from PySide2.QtWidgets import QFrame, QFileDialog
import sys, os
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt

from window_xmind2json import Window_Xmind2json
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
     sys.path.append(parent_path)
import my_util

class Window(QMainWindow):
    def __init__(self):
        super().__init__()
        #self.setGeometry(300, 300, 800, 600)
        #self.show()
        self.ui = QUiLoader().load(os.path.realpath(os.curdir)+"/gui/layout/main2.ui")
        self.center()
        self.create_menu()
        self.create_main()
        self.ui.show()

    def create_main(self):
        self.ui.setWindowTitle("日志分析")
        self.create_plug_layout()

    def create_plug_layout(self):
        self.ui.label_2.setAlignment(Qt.AlignCenter)
        #self.ui.frame.setStyleSheet('border-width: 1px;border-style: solid;border-color: rgb(255, 170, 0);')
        self.ui.pushButton.clicked.connect(self.add_item)
        self.plug_files = list()
        self.plug_matrix = list()

    def add_item(self, file_path:str):
        item_box = QHBoxLayout()
        delete_btn = QPushButton("x")
        file_lable = QLabel(my_util.get_file_name(file_path))
        file_lable.setToolTip(file_path)

        item_box.addWidget(delete_btn)
        item_box.addWidget(file_lable)
        self.ui.gridLayout.addLayout(item_box)

    def choose_file(self):
        fileDir = QFileDialog.getOpenFileNames(self.ui, "choose file")
        print(fileDir[0][0])
        self.file_path = fileDir[0][0]
        self.ui.label.setText(self.file_path.split('/')[-1])

    def create_menu(self):
        mainMenu = self.ui.menuBar()
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
        self.ui.move(qRect.topLeft())

myApp = QApplication([])
window = Window()
myApp.exec_()