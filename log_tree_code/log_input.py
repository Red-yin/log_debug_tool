#!/usr/bin/python3
import os
# from icecream import ic 
import logging
logging.basicConfig(level=logging.INFO, filename="logging.txt", format='[%(levelname)s][%(filename)s:%(lineno)s] %(message)s')
from enum import Enum
import sys  #used in main for test
from log_info_extraction import LogInfoExtraction #used in main for test
from xmind_to_log_tree import xmind_file_to_log_tree

class LogReadError(Enum):
    SUCCESS = 0
    EOF = 1 #END OF FILE
    EOD = 2 #END OF DIR
    EXCEPTION = 3 #没有文件可读
class LogInput:
    def __init__(self, path = None) -> None:
        if path is None:
            logging.debug("LogInput has no input when init")
            return
        self.__input_path_init(path)
    def input(self, path) -> None:
        self.__input_path_init(path)
    def __input_path_init(self, path):
        if not os.path.exists(path):
            logging.error("%s not exist", path)
            return
        self.input_path = path
        filelist = list()
        if os.path.isdir(path):
            for f in os.listdir(path):
                if self.__is_log_file(f):
                    filelist.append(path + "/" + f)
        elif os.path.isfile(path):
            filelist.append(path)
        else:
            logging.error(path, "is not file or path")
            return
        self.filelist = iter(filelist)
        while True:
            try:
                self.current_file = next(self.filelist)
                logging.debug("current file: %s", self.current_file)
                if self.__is_log_file(self.current_file):
                    break
            except StopIteration:
                self.current_file = None
                logging.error(path, " no log file exist")
                return
        
    def __is_log_file(self, file) -> bool: 
        return True

    def readline(self) -> (str, LogReadError):
        if self.current_file is None:
            logging.error("current file is None: EOF or not init")
            return (None, LogReadError.EXCEPTION)
        if not hasattr(self, "fd") or self.fd is None:
            self.fd = open(str(self.current_file), 'r', encoding="utf-8", errors='ignore')
        data_str = self.fd.readline()
        if not data_str:
            #读取到当前文件结尾时，切换到文件列表中的下一个文件
            self.fd.close()
            self.fd = None
            try:
                self.current_file = next(self.filelist)
                #当前文件已经读完，切换到下一个文件继续读
                logging.debug("end of file")
                return (None, LogReadError.EOF)
            except StopIteration:
                #读完文件夹中所有文件
                logging.debug("%s is finished", self.input_path)
                return (None, LogReadError.EOD)
        return (data_str, LogReadError.SUCCESS)

if __name__=="__main__":
    if len(sys.argv) < 2:
        # print("usage: log_input.py input_path")
        logging.error("usage: log_input.py input.xmind input.log")
        exit()
    
    lie = LogInfoExtraction(xmind_file_to_log_tree(sys.argv[1]))
    input_data = LogInput()
    input_data.input(sys.argv[2])
    while True:
        (data, errno) = input_data.readline()
        if errno == LogReadError.SUCCESS:
            logging.debug("read data: %s", data)
            lie.analysis(data)
            pass
        elif errno == LogReadError.EOF:
            logging.debug("file end")
        elif errno == LogReadError.EOD:
            logging.debug("%s EOD", input_data.input_path)
            break