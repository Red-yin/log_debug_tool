#!/usr/bin/python3
import sys
import logging
logging.basicConfig(level=logging.INFO, format='[%(levelname)s][%(filename)s:%(lineno)s] %(message)s')
# 逐行读取文件，对每行数据提取关键信息
# 每行数据格式如下：
# 02:54:35.613 I/NO_TAG [voice_ser](epi_voice_service.c:934) - recv msg: asr ASR_MSG_WAKEUP
def line_handle(data_str):
    logging.debug("%s%s", data_str[0:12], data_str[61:])
    # 将时间转换为ms的int值
    time_str = data_str[0:12]
    time_sec_array = time_str.split(".")
    time_hour_array = time_sec_array[0].split(":")
    time = int(time_hour_array[0])*3600*1000 + int(time_hour_array[1])*60*1000 + int(time_hour_array[2])*1000 + int(time_sec_array[1])
    # 打印时间
    logging.debug("time: %d", time)
    # 如果data_str以recv msg: asr ASR_MSG_WAKEUP结尾，则返回(0, time)
    # 否则返回(1, time)
    # test_str = "wakeup triggered 326 dsp_enable:1 \n"
    test_str = "recv msg: asr ASR_MSG_WAKEUP\n"
    if data_str.endswith(test_str):
        return (0, time)
    else:
        return (1, time)

if __name__=="__main__":
    if len(sys.argv) < 2:
        logging.error("usage: time_diff.py input.log")
        exit()
    # 使用一个数组保存每行数据的time
    data_array = list()
    time = 0
    with open(sys.argv[1], 'r', encoding="utf-8", errors='ignore') as fd:
        while True:
            data_str = fd.readline()
            if not data_str:
                break
            (l_flag, l_time) = line_handle(data_str)
            if l_flag == 0:
                # 如果flag为0，则将time赋值给time
                time = l_time
            else:
                # 如果flag为1，则将time减去l_time
                time_diff = l_time -  time
                logging.debug("time diff: %d", time_diff)
                # 将time_diff保存到数组中
                data_array.append(time_diff)
    # 求数组中所有元素的平均值
    data_array_len = len(data_array)
    data_array_sum = 0
    for i in range(data_array_len):
        data_array_sum = data_array_sum + data_array[i]
    data_array_avg = data_array_sum/data_array_len
    logging.info("data_array_avg: %d", data_array_avg)
