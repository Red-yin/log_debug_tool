#!/usr/bin/python3

from base64 import encode
import xmind
import sys
import json

class FileConvert:
    def __init__(self):
        pass
    def _get_xmind_default_info(self, topic):
        ret = {"extract":{}}
        if 'label' in topic and topic['label'] is not None:
            ret['extract']['statusInfo'] = topic['label']
        if 'comment' in topic and topic['comment'] is not None:
            ret['extract']['statusCode'] = int(topic['comment'])
        if 'note' in topic and topic['note'] is not None:
            ret['extract']['solve'] = topic['note']
        return ret

    def _get_xmind_info(self, topics):
        if topics is None:
            return None
        ret = dict()
        for item in topics:
            if 'title' not in item:
                print(item, "has no title")
                continue
            #print(item['title'])
            if 'topics' in item:
                ret[item['title']] = self._get_xmind_info(item['topics'])
            else:
                ret[item['title']] = self._get_xmind_default_info(item)
            #print(ret)
        return ret

    def xmind2json(self, input):
        try:
            workbook = xmind.load(input)
            data = workbook.getData()
            #print(data)
            self.json_data = dict()
            for item in data:
                self.json_data = self._get_xmind_info(item['topic']['topics'])
            #print(json_data)
            return self.json_data
        except Exception as e:
            print(input, "convert to json failed: ", e)
    def save(self, output):
        try:
            with open(output, 'w', encoding='utf-8') as f:
                f.write(json.dumps(self.json_data, ensure_ascii=False))
        except Exception as e:
            print(input, "save failed: ", e)

#workbook = xmind.load("./test.xmind")
#data = workbook.getData()
#print(data)
#print(workbook.to_prettify_json())

if __name__=="__main__":
    if len(sys.argv) < 2:
        print("usage: xmind2json.py input_file output_file")
        exit()

    fc = FileConvert()
    fc.xmind2json(sys.argv[1])
    fc.save(sys.argv[2])
