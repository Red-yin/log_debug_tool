#!/usr/bin/python3

from adb_run import AdbDataHandle
from file_read import FileDataRead
import json
import queue
import time
import sys

from xmind2json import FileConvert

class LogAnalysis:
    def __init__(self, file_path, queue=None):
        self.file_path = file_path 
        self.log_data = self.analysis_source_load(file_path)
        self.update_current_position()
        self.queue = queue
    
    def log_analysis(self, line_str):
        key_list = self.__get_position_keys(self.current_position)
        #print(key_list)
        if len(key_list) > 0:
            #获取trigger关键字
            if self.current_position != self.log_data:
                key_list += self.__get_position_keys(self.log_data)
            for key in key_list:
                ret = line_str.find(key)
                if ret != -1:
                    print(line_str)
                    self.update_current_position(key)
                    return key
        else:
            self.log_analysis_end()
        return None

    def __get_position_keys(self, position):
        default_keys = ["eof_info", "box", "next", "extract"]
        ret = list()
        for k in position:
            if k not in default_keys:
                ret.append(k)
        return ret

    def log_analysis_end(self):
        if "extract" in self.current_position:
            print("result:", self.current_position['extract']['statusInfo'])
        self.update_current_position()

    def update_current_position(self, key=None):
        if key == None:
            self.current_position = self.log_data
        else:
            if self.current_position is None:
                print("ERROR: current_position is None")
                return None
            elif key in self.current_position:
                self.current_position = self.current_position[key]
            elif key in self.log_data:
                print("ERROR:", self.current_position, "interrupted by ", key)
                self.current_position = self.log_data[key]
            else:
                print("ERROR:", key, "is not exist in ", self.current_position)

    def analysis_source_load(self, file_path):
        data = self.__data_loader(file_path)
        return data
        if self.__data_check(data) == 0:
            return data
        else:
            return None

    def __data_loader(self, file_path):
        with open(file_path, 'r', errors='ignore', encoding='utf-8') as f:
            data = f.read()
            json_data = json.loads(data)
            #print(self.data)
            return json_data

    def __data_check(self, data):
        if not isinstance(data, dict):
            print(data, " is not dict")
            return -1
        q = queue.Queue(10240)
        q.put(data)
        while q.qsize() > 0:
            d = q.get()
            if 0 != self.__data_syntax_detection(d):
                print(d, " syntax error")
                return -1
            if 'next' in d:
                for key in d['next']:
                    try:
                        if isinstance(d[key], dict):
                            q.put(d[key], block=False)
                        elif isinstance(d[key], list):
                            q.put(d[d[key][-1]], block=False)
                    except queue.Full:
                        print("ERROR: ", q.maxsize, " is full")
        print(self.file, ": json check ok")
        return 0

    def __data_syntax_detection(self, data):
        if isinstance(data, dict):
            if "next" in data:
                for key in data['next']:
                    if key not in data:
                        print(key, " is not in ", data)
                        return -1
                    elif isinstance(data[key], list):
                        if len(data[key]) == 0:
                            print(key, " has no member")
                            return -1
                        elif data[key][-1] not in data:
                            print(data[key][-1], " is not in ", data)
                            return -1
            if "extract" not in data:
                print(data, " has no extract")
                return -1
        return 0

    def run(self):
        log_str = self.queue.get()
        self.log_analysis(log_str)


if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: log_analysis file")
        exit()

    fc = FileConvert()
    fc.xmind2json("./source/device_control.xmind", "./source/device_control.json")
    q = queue.Queue(10240)

    if sys.argv[1] == "adb":
        cmd = 'adb shell tail -F /tmp/orb.log'
        adb_log = AdbDataHandle(cmd, queue=q)
        adb_log.run()
    else:
        #file_path = "./log_dir/orb_log_uncompressed.txt"
        file_path = sys.argv[1]
        file_log = FileDataRead(file_path, queue=q)
        file_log.run()

    source_path = "./source/device_control.json"
    print("source_path ", source_path)
    analysis = LogAnalysis(source_path, q)
    start_time = time.time()
    count = 0
    fd = open("./time_test.txt", "a+")
    while True:
        """
        analysis.run()
        """
        log_str = q.get()
        count = count + 1
        if log_str != 'EOF':
            analysis.log_analysis(log_str)
        else:
            end_time = time.time()
            time_use = end_time - start_time
            time_use_per_line = time_use*1000000/count
            print("time use: ", time_use, "s")
            print("time use per line: ", time_use_per_line, "us")
            s = "line number: " + str(count) + ", time use: " + str(time_use) + "s, time use per line:" + str(time_use_per_line) + "us\n"
            fd.write(s)
            break