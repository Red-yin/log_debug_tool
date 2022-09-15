"""
#功能说明：运行后显示弹窗，鼠标点击文件后，获取到文件路径
from PySide2.QtWidgets import QApplication, QMainWindow, QFileDialog
app = QApplication([])
fileDir = QFileDialog.getOpenFileNames(QMainWindow(), "test")
print(fileDir)
"""
from audioop import add
from cgi import test
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
        self.ui.pushButton_3.clicked.connect(self.start_log_analysis)

    def start_log_analysis(self):
        column = self.ui.gridLayout.columnCount()
        row = self.ui.gridLayout.rowCount()
        for c in range(column):
            for r in range(row):
                item = self.ui.gridLayout.itemAtPosition(r, c)
                if item is not None and item.layout() is not None and item.layout().count() > 1:
                    print("count:", item.layout().count())
                    print("text:", item.layout().itemAt(1).widget().toolTip())


    def create_plug_layout(self):
        self.ui.label_2.setAlignment(Qt.AlignCenter)
        #self.ui.frame.setStyleSheet('border-width: 1px;border-style: solid;border-color: rgb(255, 170, 0);')
        self.ui.pushButton.clicked.connect(self.choose_file)
        self.plug_files = list()
        self.plug_matrix = list()

    #删除按键触发所在的组件，移动“添加”按键位置
    def delete_item(self):
        #由于触发的按键嵌套在layout中，无法直接通过触发的按键找到layout外的layout下的座标，因此使用遍历的方式获取坐标
        column = self.ui.gridLayout.columnCount()
        row = self.ui.gridLayout.rowCount()
        clicked_row = -1
        clicked_column = -1
        for c in range(column):
            for r in range(row):
                item = self.ui.gridLayout.itemAtPosition(r, c)
                if item is not None and item.layout() is not None and item.layout().count() > 1:
                    if item.layout().itemAt(0).widget() == self.sender():
                        print("position: ", r, c)
                        clicked_column = c
                        clicked_row = r
                        break
            else:
                continue
            break
        clicked_item = self.ui.gridLayout.itemAtPosition(clicked_row, clicked_column)
        #clicked_item.setParent(None)
        clicked_item.deleteLater()
        bottom_btn = self.ui.gridLayout.itemAtPosition(clicked_row+1, clicked_column)
        self.ui.gridLayout.addWidget(bottom_btn.widget(), clicked_row, clicked_column)
        if clicked_row == 0:
            right_btn = self.ui.gridLayout.itemAtPosition(clicked_row, clicked_column+1)
            right_btn.widget().setParent(None)
       
        """
        print("btn name:",self.sender())
        index = self.ui.gridLayout.indexOf(self.sender().parent())
        print("index:", index)
        position = self.ui.gridLayout.getItemPosition(index)
        print(position)
         """

    #获取插件文件路径并显示，增加“添加”按键，支持横向和纵向添加文件
    def add_item(self, file_path:str):
        item_box = QHBoxLayout()
        item_box.setObjectName("file display box")
        delete_btn = QPushButton("x")
        delete_btn.setObjectName("delete button")
        delete_btn.clicked.connect(self.delete_item)
        file_lable = QLabel(my_util.get_file_name(file_path))
        file_lable.setToolTip(file_path)

        item_box.addWidget(delete_btn)
        item_box.addWidget(file_lable)
        index = self.ui.gridLayout.indexOf(self.sender())
        position = self.ui.gridLayout.getItemPosition(index)
        clicked_btn = self.ui.gridLayout.itemAtPosition(position[0], position[1])
        #self.ui.gridLayout.addItem(item_box, position[0], position[1], 1, 1)
        self.ui.gridLayout.addLayout(item_box, position[0], position[1])
        #self.ui.gridLayout.addItem(clicked_btn, position[0]+1, position[1], 1, 1)
        self.ui.gridLayout.addWidget(clicked_btn.widget(), position[0]+1, position[1])
        if position[0] == 0:
            print("add btn: ", position[0], position[1])
            add_btn = QPushButton("+")
            add_btn.clicked.connect(self.choose_file)
            self.ui.gridLayout.addWidget(add_btn, position[0], position[1]+1)
            #self.ui.gridLayout.addItem(add_btn, position[0], position[1]+1, 1, 1)

    def choose_file(self):
        fileDir = QFileDialog.getOpenFileNames(self.ui, "choose file")
        print(fileDir[0][0])
        self.file_path = fileDir[0][0]
        self.add_item(fileDir[0][0])

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