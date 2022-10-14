#!/usr/bin/python3
import subprocess
import threading
import queue

from data_input import DataInput

class FileDataRead(DataInput):
    def __init__(self, file_path = None):
        super().__init__(args=file_path)

    def init(self, file_path):
        if file_path == None:
            return
        self.set_file_path(file_path)

    def read(self):
        data_str = self.handle.readline()
        if not data_str:
            data_str = 'EOF'
        return data_str

    def set_file_path(self, file_path):
        try:
            self.handle = open(file_path, 'r', encoding="utf-8", errors='ignore')
        except Exception as e:
            print(e)
    
    """
    def _dataHandle(self):
        try:
            self.handle = open(self.file_path, encoding="utf-8")
        except Exception as e:
            print(e)
            exit(1)

        count = 0
        while True:
            try:
                data_str = self.handle.readline()
                count = count + 1
                if not data_str:
                    #file read end
                    data_str = 'EOF'
                    self.queue.put(data_str, block=True)
                    #print("line count: ", count)
                    break
                #print(data_str)
                if self.keyWords is not None:
                    for word in self.keyWords:
                        #ret = str(data_str, encoding='utf-8',errors='ignore').find(word[0])
                        ret = data_str.find(word[0])
                        if ret != -1:
                            print(word[0])
                            word[1](word[2])
                elif self.queue is not None:
                    try:
                        #self.queue.put(str(data_str,encoding='utf-8',errors='ignore'), block=True)
                        self.queue.put(data_str, block=True)
                    except queue.Full:
                        print("ERROR: ", self.queue.maxsize, " is full")
            except Exception as e:
                print("exception : ", e)
                print("line count: ", count)
                break

    def run(self):
        t = threading.Thread(target=self._dataHandle)
        t.setDaemon(True)
        t.start()
    """

def test(val):
    val += 1
    print('adb data test: ', val)

if __name__=="__main__":
    file_path = "./source/82626ee729b543ad8578cca4dc07b89a_2022-07-28_16_23_34.log"
    fd = FileDataRead(file_path, keyWords)
    fd.run()
