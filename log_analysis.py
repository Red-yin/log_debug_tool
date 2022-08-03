#!/usr/bin/python3

from adb_run import AdbDataHandle
import json
import queue
class LogAnalysis:
    def __init__(self, file_path, queue):
        self.file_path = file_path 
        self.log_data = self.analysis_source_load(file_path)
        self.update_current_position()
        self.queue = queue
    
    def log_analysis(self, line_str):
        key_list = self.__get_current_position_keys()
        if len(key_list) > 0:
            for key in key_list:
                ret = line_str.find(key)
                if ret != -1:
                    print(line_str)
                    self.update_current_position(key)
                    break
        else:
            self.log_analysis_end()
            

    def __get_current_position_keys(self):
        default_keys = ["eof_info", "box", "next", "extract"]
        ret = list()
        for k in self.current_position:
            if k not in default_keys:
                ret.append(k)
        return ret

    def log_analysis_end(self):
        if "extract" in self.current_position:
            print(self.current_position['extract']['statusInfo'])
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
            else:
                print("ERROR: ", key, "is not exist in ", self.current_position)

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
    q = queue.Queue(10240)
    cmd = 'adb shell tail -F /tmp/orb.log'
    log = AdbDataHandle(cmd, queue=q)
    analysis = LogAnalysis("./source/device_control.json", q)
    log.run()
    while True:
        analysis.run()
