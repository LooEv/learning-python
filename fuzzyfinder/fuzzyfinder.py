#!/usr/bin/env python
# encoding: utf-8
# Email: exyloolq@gmail.com
# Author: LooEv

import os
import sys
import platform
import re


def where_to_find():
    collections = {}
    while 1:
        path = raw_input(u"请输入你想查找的路径：".encode(encoding))
        if os.path.exists(path):
            break
        else:
            print u"路径不存在！"
    for parent, _, filenames in os.walk(path):
        if filenames:
            for fn in filenames:
                collections.setdefault(parent, []).append(fn)
    return collections


def system_detect():
    system = platform.system()
    # 此处只考虑这几种常见的情况
    systems = {'Windows': ('gbk', True), 'Linux': ('utf-8', False), 'Darwin': ('utf-8', True)}
    return systems[system]


def fuzzy_finder(keyword, collections):
    suggestions = []
    if ignore:
        keyword = keyword.lower()
    user_input = keyword.decode(sys.stdin.encoding)
    pattern = '.*?'.join(user_input.encode(encoding))
    regex = re.compile(pattern)
    for parent, filenames in collections.iteritems():
        for fn in filenames:
            if ignore:
                match = regex.search(fn.lower())
            else:
                match = regex.search(fn)
            if match:
                if len(match.group(0)) < (len(keyword) + 5):
                    the_path_of_file = os.path.join(parent, fn)
                    # len(match.group(0)反应匹配的紧凑程度，match.start()反应匹配到的起始位置
                    suggestions.append((len(match.group(0)), match.start(), the_path_of_file))
    return [fn for _, _, fn in sorted(suggestions)]


def main():
    global encoding
    global ignore  # ignore表示是否区分文件名大小写
    encoding, ignore = system_detect()
    while 1:
        collections = where_to_find()
        keyword = raw_input(u"请输入你想查询的文件名里面包含的一些字符（支持中文）：".encode(encoding))
        result = fuzzy_finder(keyword, collections)
        if result:
            print u"查询结果如下："
            for res in result:
                print res.decode('gbk')
        else:
            print u"没找到相关文件！"
        query = raw_input(u"是否继续查询？输入'no'停止查询，输入其他字符表示继续查询：".encode(encoding))
        if query == 'no':
            break


if __name__ == '__main__':
    main()
