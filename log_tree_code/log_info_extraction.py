#!/usr/bin/python3
from xmind_to_log_tree import LogTree
from xmind_to_log_tree import xmind_file_to_log_tree
from enum import Enum
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import sys  #used in main for test

class LogTreeObject:
    def __init__(self, log_tree:dict) -> None:
        self.source = LogTree(log_tree) 
        self.current_nodes = self.source.split_branch()

class LogInfoLevel(Enum):
    IGNORE = 0
    TRIGGER = 1
    PROCESS = 2
    END = 3
    WARNING = 4
    ERROR = 5

class LogInfoExtraction:
    def __init__(self, log_tree:dict = None) -> None:
        logging.debug("log info extraction input content is dict")
        self.log_tree_list = list()
        self.register(log_tree)
        self.count = 0
        self.level_convert = {"priority-1":LogInfoLevel.TRIGGER,"priority-2":LogInfoLevel.PROCESS,"priority-3":LogInfoLevel.END,"priority-4":LogInfoLevel.WARNING,"priority-5":LogInfoLevel.ERROR}
    def register(self, log_tree):
        if log_tree is not None:
            self.log_tree_list.append(LogTreeObject(log_tree))
    def analysis(self, line:str) -> (LogInfoLevel, str):
        if line is None:
            logging.warn("input line is None, no analysis")
            return (LogInfoLevel.IGNORE, None)
        return self._analysis(line)

    def _analysis(self, line:str) -> (LogInfoLevel, str):
        for log_tree in self.log_tree_list:
            for node in log_tree.current_nodes:
                current_keys = node.get_current_keys()
                for key in current_keys:
                    ret = line.find(key)
                    if ret != -1:
                        logging.info("%d:%s", self.count, line)
                        logging.info("find key: [%s]", key)
                        key_info = node.key_info_in_current_position(key)
                        logging.info("key info: [%s]", key_info)
                        self.count = self.count + 1
                        node.update_position(key)
                        return self._key_info_convert(key_info)
        return (LogInfoLevel.IGNORE, None)
    def _key_info_convert(self, key_info) -> (LogInfoLevel, str):
        level = LogInfoLevel.IGNORE
        desc = ""
        marks = "makers"
        if key_info is None:
            logging.debug("key info: is none")
            return (level, None)
        if "note" in key_info:
            desc = key_info["note"]
        if marks in key_info:
            for m in key_info[marks]:
                if m in self.level_convert:
                    level = self.level_convert[m]
                    break
                else:
                    logging.warn("%s level is not support", m)
        return (level, desc)

 
if __name__=="__main__":
    if len(sys.argv) < 3:
        print("usage: log_info_extraction.py input.xmind input.log")
        exit()
    lt = xmind_file_to_log_tree(sys.argv[1])
    lie = LogInfoExtraction(lt)
    lie.analysis()