#!/usr/bin/python3

from xmindparser import xmind_to_dict
from icecream import ic 
import logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
import os
import sys

TITLE = "title"
TOPICS = "topics"

log_tree_example = {TITLE:"root",TOPICS:[{TITLE:"a",TOPICS:[{TITLE:"b", TOPICS:[{TITLE:"c"}]}]}, {TITLE:"1",TOPICS:[{TITLE:"2"}, {TITLE:"3"}]}]}
line_list = ["abc", "bd", "cfg"]

class LogTree:
    def __init__(self, log_tree:dict) -> None:
        logging.debug("LogTree init by dict: %s", log_tree)
        self.root = log_tree
        self.current_position = log_tree
        self._current_keys = list() 
        self._update_current_keys()
    def get_current_keys(self) -> list:
        return self._current_keys
    def _update_current_keys(self) -> None:
        self._current_keys.clear()
        if isinstance(self.current_position, dict):
            if TITLE in self.current_position:
                self._current_keys.append(self.current_position[TITLE])
        elif isinstance(self.current_position, list):
            for item in self.current_position:
                if TITLE in item:
                    self._current_keys.append(item[TITLE])
    def update_position(self, key:str):
        if isinstance(self.current_position, dict):
            if TOPICS in self.current_position:
                logging.info("update %s in branch root", key)
                self.current_position = self.current_position[TOPICS]
                self._update_current_keys()
        elif isinstance(self.current_position, list):
            for item in self.current_position:
                if TITLE in item and item[TITLE] == key:
                    if TOPICS in self.current_position:
                        logging.info("update in %s branch", key)
                        self.current_position = self.current_position[TOPICS]
                    else:
                        logging.info("%s is the end of branch", key)
                        self.current_position = self.root
                    self._update_current_keys()
                    break
    def split_branch(self) -> list:
        log_tree_list = list()
        if TOPICS in self.root:
            for item in self.root[TOPICS]:
                log_tree_list.append(LogTree(item))
        return log_tree_list

def get_xmind_data(xmind_node:list)->list:
    if not isinstance(xmind_node, list):
        return None
    data_list = list()
    for item in xmind_node:
        node = dict()
        if TITLE in item:
            node[TITLE] = item[TITLE]
        if TOPICS in item:
            node[TOPICS] = get_xmind_data(item[TOPICS])
        data_list.append(node)
    return data_list

def xmind_list_to_log_tree(xmind_list:list)->list:
    # return get_xmind_data(xmind_list[0]["topic"][TOPICS])
    return xmind_list[0]["topic"]

def xmind_file_to_log_tree(file_path:str)->list:
    if not os.path.exists(file_path):
        return None
    #xmind文件转换成python dict
    xmind_list = xmind_to_dict(file_path)
    #xmind格式的python dict转换成log tree需要的dict
    return xmind_list_to_log_tree(xmind_list)

def find_subtree(root:list, line:str):
    if not isinstance(root, list) or not isinstance(line, str):
        ic("find_subtree params error: root: ", type(root), "line", type(line))
        return (None, None)
    for item in root:
        if TITLE in item and line.find(item[TITLE]) != -1:
            #find subtree!
            return (item[TITLE], item)
    else:
        return (None, None)

#根据lines内容，确定root的指定路径；若root未结束，lines先结束，则提示内容不完整；
#返回值：lines中命中root的key列表，以及root最底层key对应的内容
def find_leaf(root:list, lines:iter):
    sub_tree = root
    tree_branch = list()
    for line in lines:
        if not isinstance(line, str):
            print("iter member is not str")
            return tree_branch, sub_tree
        (k, t) = find_subtree(sub_tree, line)
        if k and t:
            # key exist in line
            tree_branch.append(k)
            if TOPICS in t:
                sub_tree = t[TOPICS]
            else:
                print("find leaf: ", k, t)
                return tree_branch, t
    else:
        print("imcomplete log")
        return tree_branch,sub_tree

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: xmind2json.py input_file")
        exit()

    out = xmind_file_to_log_tree(sys.argv[1])
    print(out)
    #print(find_leaf(log_tree, line_list))
