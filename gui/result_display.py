from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
from PySide2.QtWidgets import QApplication, QWidget, QTextEdit, QPushButton, QMessageBox, QVBoxLayout
from PySide2.QtGui import QCloseEvent
from PySide2.QtCore import QThread
import sys, os
import threading
import time
import queue
from data_input import DataInput

from log_analysis import LogAnalysis

class ResultDisplayWindow(QWidget, QThread):
    def __init__(self, data_source:DataInput, analysis:LogAnalysis):
        super().__init__()
        QThread.__init__(self)
        self.data_source = data_source
        self.analysis = analysis
        self.create_main()

    def create_main(self):
        self.ui = QUiLoader().load(os.path.realpath(os.curdir)+"/gui/layout/result_display.ui")
        self.ui.setWindowTitle("结果显示")
        self.ui.setMinimumWidth(800)
        self.ui.textBrowser.setMinimumWidth(600)
        self.ui.textBrowser.append("append test")
        self.ui.pushButton_5.clicked.connect(self.choose_input)
        self.start()
        #t = threading.Thread(target=self.update_text_display)
        #t.setDaemon(True)
        #t.start()

    def closeEvent(self, event:QCloseEvent):
        print("close event")
        event.accept()

    def choose_input(self):
        if self.input_type == "files":
            fileDir = QFileDialog.getOpenFileNames(self.ui, "choose file")
            print(fileDir[0][0])
            self.data_source.set_file_path(fileDir[0][0])
            self.data_source.run()
        elif self.input_type == "adb":
            pass

    def set_input_type(self, type):
        self.input_type = type
        self.ui.pushButton_5.setText(type)

    def run(self):
        start_time = time.time()
        count = 0
        while True:
            log_str = self.data_source.get()
            count = count + 1
            if log_str != 'EOF':
                ret = self.analysis.log_analysis(log_str)
                self.ui.textBrowser_2.append(log_str)
                if ret != None:
                    self.ui.textBrowser.append(ret + ":" + log_str)
            else:
                end_time = time.time()
                time_use = end_time - start_time
                time_use_per_line = time_use*1000000/count
                print("time use: ", time_use, "s")
                print("time use per line: ", time_use_per_line, "us")
                s = "line number: " + str(count) + ", time use: " + str(time_use) + "s, time use per line:" + str(time_use_per_line) + "us\n"
                self.ui.textBrowser.append(s)
                break