#!/usr/bin/python3
from xmind_to_log_tree import LogTree
from xmind_to_log_tree import xmind_file_to_log_tree
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import sys  #used in main for test

"""
class LogTreeRoot:
    def __init__(self, log_tree:LogTree) -> None:
        self.root = log_tree
        self.current_position = log_tree
        self.current_keys = list() 
        self._update_current_keys()
    def update(self, key:str) -> None:
        for item in self.current_position:
            if TITLE in item and item[TITLE] == key:
                if TOPICS in self.current_position:
                    logging.debug("update in %s branch", key)
                    self.current_position = self.current_position[TOPICS]
                else:
                    logging.info("%s is the end of branch", key)
                    self.current_position = self.root
                self._update_current_keys()
                break
    def _update_current_keys(self):
        self.current_keys.clear()
        for item in self.current_position:
            self.current_keys.append(item[TITLE])
            
"""

class LogTreeObject:
    def __init__(self, log_tree:dict) -> None:
        self.source = LogTree(log_tree) 
        self.current_nodes = self.source.split_branch()

class LogInfoExtraction:
    def __init__(self, log_tree:dict = None) -> None:
        logging.debug("log info extraction input content is dict")
        self.log_tree_list = list()
        self.register(log_tree)
        self.count = 0
    def register(self, log_tree):
        if log_tree is not None:
            self.log_tree_list.append(LogTreeObject(log_tree))
    def analysis(self, line:str):
        if line is None:
            logging.warn("input line is None, no analysis")
            return
        self._analysis(line)
    def result_show(self):
        pass

    def _analysis(self, line:str):
        for log_tree in self.log_tree_list:
            for node in log_tree.current_nodes:
                current_keys = node.get_current_keys()
                for key in current_keys:
                    ret = line.find(key)
                    if ret != -1:
                        logging.info("%d:%s", self.count, line)
                        logging.info("find key: [%s]", key)
                        self.count = self.count + 1
                        node.update_position(key)
                        return
 
if __name__=="__main__":
    if len(sys.argv) < 3:
        print("usage: log_info_extraction.py input.xmind input.log")
        exit()
    lt = xmind_file_to_log_tree(sys.argv[1])
    lie = LogInfoExtraction(lt)
    lie.analysis()