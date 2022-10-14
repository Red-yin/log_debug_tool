
import queue
import threading
import time
from adb_run import AdbDataHandle
from data_input import DataInput
from file_read import FileDataRead
from log_analysis import LogAnalysis

class Task:
    def __init__(self, proc:LogAnalysis, data_input: DataInput ,name:str = None) -> None:
        self.name = name
        self.state = "idle"
        self.analysis = proc
        self.data_input = data_input

        self.t = threading.Thread(target=self._run)
        self.t.setDaemon(True)
        self.t.start()
        self.event = threading.Event()
        self.output_queue = queue.Queue(10240)
    def get_task_result(self):
        return self.output_queue.get()
    def pause_task(self):
        self.state = "pause"
        self.data_input.pause()
    def stop_task(self):
        self.state = "stop"
        self.data_input.quit()
        self.event.set()
    def start_task(self):
        self.state = "start"
        return 0
    def resume_task(self):
        self.state = "resume"
        self.data_input.resume()
    def set_name(self, name:str):
        self.name = name

    def _run(self):
        start_time = time.time()
        count = 0
        fd = open("./time_test.txt", "a+")
        while True:
            if self.state == "pause":
                print("task puased")
                self.event.wait()
            if self.state == "stop":
                print("task stoped")
                break
            log_str = self.data_input.get()
            count = count + 1
            if log_str != 'EOF':
                try:
                    self.output_queue.put(self.analysis.log_analysis(log_str))
                except queue.Full:
                    print("ERROR: ", self.queue.maxsize, " is full")
            else:
                end_time = time.time()
                time_use = end_time - start_time
                time_use_per_line = time_use*1000000/count
                print("time use: ", time_use, "s")
                print("time use per line: ", time_use_per_line, "us")
                s = "line number: " + str(count) + ", time use: " + str(time_use) + "s, time use per line:" + str(time_use_per_line) + "us\n"
                fd.write(s)
                break