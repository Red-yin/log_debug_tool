#!/usr/bin/python3

from xmindparser import xmind_to_dict
from icecream import ic 
import os

from base64 import encode
import sys
import json

def xmind_dict_to_log_tree(xmind_dict:dict)->dict:
    if not isinstance(xmind_dict, dict):
        ic(type(xmind_dict))
        return None
    log_tree = dict()
    return xmind_dict['topic']


def xmind_to_log_tree(file_path:str)->dict:
    if not os.path.exists(file_path):
        return None
    xmind_dict = xmind_to_dict(file_path)
    ic(xmind_dict)
    xmind_dict_to_log_tree(xmind_dict[0])

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: xmind2json.py input_file")
        exit()

    out = xmind_to_log_tree(sys.argv[1])
