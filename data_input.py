from abc import abstractclassmethod, abstractmethod
import threading
import queue
class DataInput:
    def __init__(self, line_buffer:int = None, args = None):
        if line_buffer == None or line_buffer == 0:
            line_buffer = 10240
        self.q = queue.Queue(line_buffer)
        self.init(args)
        self.stop_flag = 0
        self.pause_flag = 0

    def put(self, data, block: bool = True):
        self.q.put(data, block)

    def get(self):
        return self.q.get()

    @abstractmethod
    def init(self, args = None):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def deinit(self):
        pass

    def quit(self):
        self.stop_flag = 1
        self.pause_flag = 0
        self.event.set()
        self.q.task_done

    def pause(self):
        self.pause_flag = 1

    def resume(self):
        self.pause_flag = 0
        self.event.set()

    def _read_data(self):
        while True:
            if self.stop_flag == 1:
                break
            if self.pause_flag == 1:
                self.event.wait()
            data = self.read()
            #print("read data: ", data)
            if not data:
                break
            else:
                self.put(data)
        print("thread run break")
        self.deinit()

    def run(self):
        self.stop_flag = 0
        self.t = threading.Thread(target=self._read_data)
        self.t.setDaemon(True)
        self.t.start()
        self.event = threading.Event()

