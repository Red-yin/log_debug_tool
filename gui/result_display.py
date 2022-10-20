from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QMessageBox, QVBoxLayout
from PySide2.QtGui import QCloseEvent
import sys, os
import threading
import time

from task_manage import Task

class ResultDisplayWindow(QWidget):
    def __init__(self, task:Task):
        super().__init__()
        self.task = task
        self.update_data()
        self.create_window()

    def create_window(self):
        main_layout = QVBoxLayout()
        set_layout = QHBoxLayout()
        self.select_btn = QPushButton("选择")
        self.select_btn.clicked.connect(self.choose_input)
        self.select_label = QLabel()
        set_layout.addWidget(self.select_btn)
        set_layout.addWidget(self.select_label)
        main_layout.addLayout(set_layout)

        display_layout = QHBoxLayout()
        text_layout = QVBoxLayout()
        text_label = QLabel("输入数据")
        self.text_browser = QTextBrowser()
        text_layout.addWidget(text_label)
        text_layout.addWidget(self.text_browser)
        display_layout.addLayout(text_layout)
        text1_layout = QVBoxLayout()
        text1_label = QLabel("分析结果")
        self.text1_browser = QTextBrowser()
        text1_layout.addWidget(text1_label)
        text1_layout.addWidget(self.text1_browser)
        display_layout.addLayout(text1_layout)
        main_layout.addLayout(display_layout)

        control_layout = QHBoxLayout()
        self.start_btn = QPushButton("开始")
        self.pause_btn = QPushButton("暂停")
        self.save_btn = QPushButton("保存")
        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.pause_btn)
        control_layout.addWidget(self.save_btn)
        main_layout.addLayout(control_layout)
        self.setLayout(main_layout)

    def create_main(self):
        self.ui = QUiLoader().load(os.path.realpath(os.curdir)+"/gui/layout/result_display.ui")
        self.ui.setWindowTitle("结果显示")
        self.ui.setMinimumWidth(800)
        self.ui.textBrowser.setMinimumWidth(600)
        self.ui.textBrowser.append("append test")
        self.ui.pushButton_5.clicked.connect(self.choose_input)

    def closeEvent(self, event:QCloseEvent):
        print("close event")
        self.task.stop()
        event.accept()
    
    def start_task(self):
        self.task.resume()

    def pause_task(self):
        self.task.pause()

    def save_task_result(self):
        pass

    def choose_input(self):
        if self.input_type == "files":
            fileDir = QFileDialog.getOpenFileNames(self, "choose file")
            print(fileDir[0][0])
            self.select_label.setText(fileDir[0][0])
            self.task.data_input.init(fileDir[0][0])
            self.task.data_input.start()
        elif self.input_type == "adb":
            pass

    def set_input_type(self, type):
        self.input_type = type
        self.select_btn.setText(type)

    def update_data(self):
        self.t = threading.Thread(target=self._run)
        self.t.setDaemon(True)
        self.t.start()

    def _run(self):
        while True:
            result = self.task.get_task_result()
            print(result)
            self.text1_browser.append(str(result))