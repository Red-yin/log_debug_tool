from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QDesktopWidget
from PySide2.QtWidgets import QBoxLayout, QGridLayout, QVBoxLayout, QHBoxLayout
from PySide2.QtWidgets import QPushButton, QLabel, QComboBox
from PySide2.QtWidgets import QFrame, QFileDialog
import sys, os
from PySide2.QtGui import QIcon
from PySide2.QtUiTools import QUiLoader
from PySide2.QtCore import Qt
from test import TestWindow

from window_xmind2json import Window_Xmind2json
from result_display import ResultDisplayWindow
parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
     sys.path.append(parent_path)
import my_util
from adb_run import AdbDataHandle
from log_analysis import LogAnalysis
from file_read import FileDataRead
from task_manage import Task

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
        #self.ui.comboBox.currentIndexChanged.connect(self.choose_input)
        #self.ui.comboBox.activated.connect(self.choose_input)

    def start_log_analysis(self):
        self.plug_list = list()
        column = self.ui.gridLayout.columnCount()
        row = self.ui.gridLayout.rowCount()
        for c in range(column):
            plug_group = set()
            for r in range(row):
                item = self.ui.gridLayout.itemAtPosition(r, c)
                if item is not None and item.layout() is not None and item.layout().count() > 1:
                    print("count:", item.layout().count())
                    print("text:", item.layout().itemAt(1).widget().toolTip())
                    plug_group.add(item.layout().itemAt(1).widget().toolTip())
            if len(plug_group) > 0:
                self.plug_list.append(plug_group)
        print(self.plug_list)
        #self.start_feed_data()
        self.log_analysis_window()

    def log_analysis_window(self):
        self.task = self.create_task(self.plug_list, self.ui.comboBox.currentText())

        self.result_window = ResultDisplayWindow(self.task)
        self.result_window.set_input_type(self.ui.comboBox.currentText())
        self.result_window.show()

    def create_task(self, plug_list: list, data_input_type: str):
        if plug_list is None:
            print("create Task failed: plug_list is None")
            return None

        analysis = LogAnalysis(plug_list)
        data_source = None
        if data_input_type == 'adb':
            cmd = 'adb shell tail -F /tmp/orb.log'
            data_source = AdbDataHandle()
            data_source.init(cmd)
            data_source.start()
        elif data_input_type == 'files':
            data_source = FileDataRead()
        else:
            print("create Task failed:", data_input_type, "is not exist")
            return None

        task = Task(analysis, data_source)
        return task

    def create_plug_layout(self):
        self.ui.label_2.setAlignment(Qt.AlignCenter)
        #self.ui.frame.setStyleSheet('border-width: 1px;border-style: solid;border-color: rgb(255, 170, 0);')
        self.ui.pushButton.clicked.connect(self.choose_file)

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
        #删除layout时，需要把layout下所有的widget清空
        clicked_item = self.ui.gridLayout.itemAtPosition(clicked_row, clicked_column)
        for i in range(clicked_item.count()):
            child = clicked_item.itemAt(i).widget()
            if child:
                child.deleteLater()
        #只有通过被删除layout的上一层级调用removeItem才能删掉layout，否则在清空layout下的widget后，layout仍然会保留，影响当前位置的布局
        self.ui.gridLayout.removeItem(clicked_item)
        clicked_item.setParent(None)
        bottom_btn = self.ui.gridLayout.itemAtPosition(clicked_row+1, clicked_column)
        self.ui.gridLayout.addWidget(bottom_btn.widget(), clicked_row, clicked_column)
        if clicked_row == 0:
            right_btn = self.ui.gridLayout.itemAtPosition(clicked_row, clicked_column+1)
            right_btn.widget().deleteLater()

    #获取插件文件路径并显示，增加“添加”按键，支持横向和纵向添加文件
    def add_item(self, file_path:str):
        item_box = QHBoxLayout()
        item_box.setObjectName("file display box")
        delete_btn = QPushButton("-")
        delete_btn.setObjectName("delete button")
        delete_btn.clicked.connect(self.delete_item)
        file_lable = QLabel(my_util.get_file_name(file_path))
        file_lable.setToolTip(file_path)

        item_box.addWidget(delete_btn)
        item_box.addWidget(file_lable)
        index = self.ui.gridLayout.indexOf(self.sender())
        position = self.ui.gridLayout.getItemPosition(index)
        print("add item in position: ", position)
        clicked_btn = self.ui.gridLayout.itemAtPosition(position[0], position[1])
        print("click btn:", clicked_btn)
        print("add layout in position: ", position)
        self.ui.gridLayout.addLayout(item_box, position[0], position[1])
        #self.ui.gridLayout.addItem(clicked_btn, position[0]+1, position[1], 1, 1)
        print("add layout in position: ", position)
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

    def choose_input(self):
        if self.ui.comboBox.currentText() == 'adb':
            print("adb choosed")
            pass
        elif self.ui.comboBox.currentText() == 'files':
            print("file choosed")
            file_dir = QFileDialog.getOpenFileNames(self.ui, "choose file")
            self.source_file = file_dir[0][0]
            print("source file:", self.source_file)

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
        self.setCentralWidget(QDesktopWidget())
        """
        qRect = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        qRect.moveCenter(centerPoint)
        self.ui.move(qRect.topLeft())
        """

myApp = QApplication([])
window = Window()
myApp.exec_()