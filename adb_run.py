#!/usr/bin/python3
from codecs import ignore_errors
import subprocess
import threading
import queue

class AdbDataHandle:
    def __init__(self, cmd, keyWords=None, queue=None):
        self.cmd = cmd
        self.keyWords = keyWords
        self.queue = queue

    def _dataHandle(self):
        try:
            self.handle = subprocess.Popen(args=self.cmd, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        except Exception as e:
            print(e)
            exit(1)

        adbstr = self.handle.stdout.readline()
        print('read:', adbstr)
        ret = str(adbstr, encoding='utf-8', errors='ignore').find('error')
        if ret != -1:
            print("command error")
            exit(1)
        while True:
            adbstr = self.handle.stdout.readline()
            #print(adbstr)
            if self.keyWords is not None:
                for word in self.keyWords:
                    ret = str(adbstr, encoding='utf-8',errors='ignore').find(word[0])
                    if ret != -1:
                        print(word[0])
                        word[1](word[2])
            elif self.queue is not None:
                try:
                    self.queue.put(str(adbstr,encoding='utf-8',errors='ignore'), block=False)
                except queue.Full:
                    print("ERROR: ", self.queue.maxsize, " is full")

    def run(self):
        t = threading.Thread(target=self._dataHandle)
        t.setDaemon(True)
        t.start()
        #self._dataHandle()

def test(val):
    val += 1
    print('adb data test: ', val)

if __name__=="__main__":
    cmd = 'adb shell tail -F /tmp/orb.log'
    count = 0
    keyWords = [['RECV DEVICE CTRL CMD', test, count]]
    adb = AdbDataHandle(cmd, keyWords)
    adb.run()
