from abc import abstractclassmethod, abstractmethod
import threading
import queue
class DataInput:
    def __init__(self, line_buffer:int = None):
        if line_buffer == None or line_buffer == 0:
            line_buffer = 10240
        self.q = queue.Queue(line_buffer)
        self.pause()
        self.run()

    def put(self, data, block: bool = True):
        self.q.put(data, block)

    def get(self):
        return self.q.get(block=True)

    @abstractmethod
    def init(self, args = None):
        pass

    @abstractmethod
    def read(self):
        pass

    def quit(self):
        self.stop_flag = 1
        self.pause_flag = 0
        self.event.set()
        print("data input task done")
        self.q.task_done()
        print("data input join")
        if self.t.is_alive():
            self.t.join()
        print("data input end")

    def pause(self):
        self.stop_flag = 0
        self.pause_flag = 1

    def start(self):
        self.stop_flag = 0
        self.pause_flag = 0
        self.event.set()

    def _read_data(self):
        while True:
            #print("thread run", self.stop_flag, self.pause_flag)
            if self.stop_flag == 1:
                break
            if self.pause_flag == 1:
                self.event.wait()
            data = self.read()
            #print("read data: ", data)
            if not data:
                break
            self.put(data)
            if data == 'EOF':
                break
        print("thread run break")

    def run(self):
        self.stop_flag = 0
        self.event = threading.Event()
        self.t = threading.Thread(target=self._read_data)
        #self.t.setDaemon(True)
        self.t.start()

