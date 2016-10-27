#!/usr/bin/env python
#  coding=utf-8

__author__ = 'Loo'

import re
import sys
from handlers import *
from rules import *
from util import *


class Parser:
    def __init__(self, handler):
        self.handler = handler
        self.rules = []
        self.filters = []
        self.last_element = None
        self.current_element = None

    def addRule(self, rule):
        self.rules.append(rule)

    def addFilter(self, pattern, name):
        def filter(element, handler):
            return re.sub(pattern, handler.sub(name), element)

        self.filters.append(filter)

    def parse(self, file):
        self.handler.start('document')
        for element in elements(file):
            self.last_element = self.current_element
            for filter in self.filters:
                element = filter(element, self.handler)
            for rule in self.rules:
                self.current_element = rule.action(element, self.handler)
                if self.current_element:
                    # 下面if语句是为了处理列表后面紧挨着代码块的情况，如果不处理，会出现代码块显示在列表前面的现象！
                    if self.last_element == 'list' and self.current_element == 'code':
                        self.rules[1].action(element, self.handler)
                    break
        self.handler.end('document')


class SimpleMarkdownParser(Parser):
    def __init__(self, handler):
        Parser.__init__(self, handler)
        self.addRule(CodeRule())
        self.addRule(ListRule())
        self.addRule(HeadingRule())
        self.addRule(ParagraphRule())

        self.addFilter(r'\*(.+?)\*{1,2}', 'emphasis_or_strong')
        self.addFilter(r'!\[(.*?)\]\((.+?)\)', 'image')
        self.addFilter(r'\[(.*?)\]\((.+?)\)', 'url')
        self.addFilter(r'(\w+?@[a-zA-Z]+?\.[a-zA-Z]+)', 'mail')


handler = HTMLRenderer()
parser = SimpleMarkdownParser(handler)
parser.parse(sys.stdin)
