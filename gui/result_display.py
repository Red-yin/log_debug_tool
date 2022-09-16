from PySide2.QtUiTools import QUiLoader
from PySide2.QtWidgets import *
import sys, os
import threading
import time
import queue

from log_analysis import LogAnalysis

class ResultDisplayWindow(QDialog):
    def __init__(self, queue:queue, analysis:LogAnalysis):
        super().__init__()
        self.q = queue
        self.analysis = analysis
        self.create_main()

    def create_main(self):
        self.ui = QUiLoader().load(os.path.realpath(os.curdir)+"/gui/layout/result_display.ui")
        self.ui.setWindowTitle("结果显示")
        self.ui.setMinimumWidth(800)
        self.ui.textBrowser.setMinimumWidth(600)
        self.ui.textBrowser.append("append test")
        t = threading.Thread(target=self.update_text_display)
        t.setDaemon(True)
        t.start()

    def update_text_display(self):
        start_time = time.time()
        count = 0
        while True:
            log_str = self.q.get()
            count = count + 1
            if log_str != 'EOF':
                ret = self.analysis.log_analysis(log_str)
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