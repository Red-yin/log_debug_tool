from PySide2.QtWidgets import QApplication, QMainWindow, QAction, QDialog, QFileDialog
from PySide2.QtUiTools import QUiLoader
import os, sys

parent_path = os.path.dirname(sys.path[0])
if parent_path not in sys.path:
     sys.path.append(parent_path)
from xmind2json import FileConvert

class Window_Xmind2json(QDialog):
    def __init__(self):
        super().__init__()
        self.ui = QUiLoader().load(os.path.realpath(os.curdir)+"/gui/layout/xmind2json.ui")
        self.ui.setWindowTitle('xmind转json')
        self.ui.pushButton.clicked.connect(self.choose_file)
        self.ui.pushButton_2.clicked.connect(self.run_xmind2json)
        self.file_path = None

    def choose_file(self):
        fileDir = QFileDialog.getOpenFileNames(self.ui, "test")
        print(fileDir[0][0])
        self.file_path = fileDir[0][0]
        self.ui.label.setText(self.file_path.split('/')[-1])

    def run_xmind2json(self):
        if self.file_path is None or not os.path.exists(self.file_path):
            return
        fc = FileConvert()
        jsondata = fc.xmind2json(self.file_path)
        print(jsondata)