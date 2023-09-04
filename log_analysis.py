#!/usr/bin/python3

from fileinput import filelineno
from adb_run import AdbDataHandle
from file_read import FileDataRead
import json
import queue
import time
import sys

#from xmind2json import FileConvert

class AnalysisConfig:
    def __init__(self, file_path) -> None:
        self.file_path = file_path
        self.analysis_source_load(file_path)
        self._update_current_position()

    def update(self, file_path) -> None:
        self.file_path = file_path
        self.analysis_source_load(file_path)
        self._update_current_position()

    def analysis(self, content:str):
        key_list = self._get_current_keys()
        #print(key_list)
        if len(key_list) == 0:
            self._log_analysis_end()
            key_list = self._get_current_keys()
        for key in key_list:
            ret = content.find(key)
            #结果分类：1.content不包含key；
            # 2.content包含key，且key是最终的成功结果；
            # 3.content包含key，且key是最终的失败结果；
            # 4.content包含key，且key是中间节点；
            if ret != -1:
                print(content)
                self._update_current_position(key)
                if self._is_position_end():
                    #结果分类2和3
                    ret = dict()
                    ret['key'] = key
                    ret['result'] = self._current_result()
                    return ret
                else:
                    #结果分类4
                    ret = dict()
                    ret['key'] = key
                    return ret
        #结果分类1
        return None

    def _is_position_end(self) -> bool:
        key_list = self._get_current_keys()
        if len(key_list) > 0:
            return False
        else:
            return True
    def _update_current_position(self, key=None):
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
        self.log_data = self.__data_loader(file_path)
        return 
        if self.__data_check(data) == 0:
            return data
        else:
            return None

    def _get_current_keys(self):
        key_list = self.__get_position_keys(self.current_position)
        if len(key_list) > 0 and self.current_position != self.log_data:
            #获取trigger关键字
            key_list += self.__get_position_keys(self.log_data)
        return key_list 

    def _get_trigger_keys(self):
        return self.__get_position_keys(self.log_data)

    def __get_position_keys(self, position):
        default_keys = ["eof_info", "box", "next", "extract", "statusCode", "statusInfo"]
        ret = list()
        for k in position:
            if k not in default_keys:
                ret.append(k)
        return ret

    def _current_result(self):
        return self.current_position['extract']

    def _log_analysis_end(self):
        if "extract" in self.current_position:
            print("result:", self.current_position['extract']['statusInfo'])
        self._update_current_position()

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


class LogAnalysis:
    def __init__(self, file_list:list):
        self.file_list = file_list
        self.plug_list = list()
        self.log_plug_update(0)
        self.step_result = None
    
    def log_plug_update(self, index):
        if index >= len(self.file_list):
            print(index, "is out of range")
            return
        self.plug_list.clear()
        self.file_list_index = index
        for f in self.file_list[self.file_list_index]:
            self.plug_list.append(AnalysisConfig(f))

    def log_analysis(self, line_str):
        #print("INPUT DATA: ", line_str)
        self.step_result = None
        for plug in self.plug_list:
            result = plug.analysis(line_str)
            if result != None:
                self.step_result = result
                #print("analysis result: ", result)
                break
        if self.step_result == None:
            return None
        elif 'result' in self.step_result and self.step_result['result']['statusCode'] == 0:
            #插件运行一轮结束，结果为成功；更新plug_list到下一个
            self.file_list_index += 1
            if self.file_list_index >= len(self.file_list):
                #插件列表已经到结尾，从头开始
                self.file_list_index = 0
            self.log_plug_update(self.file_list_index)
            print("RESULT: ", self.step_result)
        elif 'result' in self.step_result and self.step_result['result']['statusCode'] != 0:
            #插件运行一轮结束，结果为失败；一轮整体分析流程结束，从头开始
            self.file_list_index = 0
            self.log_plug_update(self.file_list_index)
            print("RESULT: ", self.step_result)
        elif 'key' in self.step_result:
            #命中了此插件的一个流程分支，但是未到最终流程
            print("MARK: ", self.step_result)
            pass
        return self.step_result

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: log_analysis json_file log_file")
        exit()

    """
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
    """
    #file_path = "./log_dir/orb.log"
    file_path = sys.argv[2]
    file_log = FileDataRead()
    file_log.init(file_path)
    file_log.start()

    #source_path = "./source/device_control.json"
    source_path = sys.argv[1]
    print("source_path ", source_path)
    param = list()
    first_node = set()
    first_node.add(source_path)
    param.append(first_node)
    analysis = LogAnalysis(param)
    start_time = time.time()
    count = 0
    fd = open("./time_test.txt", "a+")
    while True:
        log_str = file_log.get()
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
    file_log.quit()
