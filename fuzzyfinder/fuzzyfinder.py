#!/usr/bin/env python
# encoding: utf-8
# Author: LooEv

import os
import sys
import platform
import re


def system_detect():
    system = platform.system()
    # 此处只考虑这几种常见的情况，Windows环境下请使用cmd运行此脚本
    systems = {'Windows': ('gbk', True), 'Linux': ('utf-8', False), 'Darwin': ('utf-8', True)}
    if system in systems:
        return systems[system]
    else:
        raise Exception(
            "your system is out of my consideration,sorry.The Chinese maybe display abnormally!")


def fuzzy_finder():
    suggestions = []
    while 1:
        path = raw_input(u"请输入你想查找的路径：".encode(encoding))
        if os.path.exists(path):
            break
        else:
            print u"路径不存在！"
    keyword = raw_input(u"请输入你想查询的文件名里面包含的一些字符（支持中文）：".encode(encoding))
    user_input = keyword.decode(sys.stdout.encoding)
    if ignore:
        user_input = user_input.lower()
    pattern = '.*?'.join(user_input)
    regex = re.compile(pattern)
    
    for parent, _, filenames in os.walk(path):
        if filenames:
            parent = parent.decode(sys.stdout.encoding)
            for fn in filenames:
                fn = fn.decode(sys.stdout.encoding)
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
        result = fuzzy_finder()
        if result:
            print u"查询结果如下："
            for res in result:
                print res
        else:
            print u"没找到相关文件！"
        query = raw_input(u"是否继续查询？输入'no'停止查询，输入其他字符表示继续查询：".encode(encoding))
        if query == 'no':
            break


if __name__ == '__main__':
    main()
