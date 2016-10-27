#!/usr/bin/env python
# coding=utf-8

__author__ = 'Loo'


# import fileinput


def lines(file):
    # for line in fileinput.input(file):
    for line in file:
        yield line


def elements(file):
    line_feed = False
    for line in lines(file):
        if line.strip():
            if line_feed:
                yield '\n'
                line_feed = False
            yield line.rstrip()
        else:
            line_feed = True
    yield '\n'  # 确保最后一个元素能够被处理
