#!/usr/bin/env python
#  coding=utf-8

__author__ = 'Loo'

import re


class Rule(object):
    strip = None

    def action(self, element, handler, *args):
        handler.start(self.type, *args)
        handler.feed(element.strip(self.strip))
        handler.end(self.type, *args)
        return True


class HeadingRule(Rule):
    type = 'heading'
    level = 0

    def condition(self, element):
        if element.startswith('#'):
            self.strip = '#'
            for char in element[:6]:
                if char == '#':
                    self.level += 1
                else:
                    break
            return True

    def action(self, element, handler, *args):
        if self.condition(element):
            Rule.action(self, element, handler, self.level)
            self.level = 0
            return True


class ListRule(Rule):
    type = 'list_item'
    list_type = ''
    flag = ['* ', '- ', '+ ']
    list_item_inside = False
    content = []

    def list_break(self, element):
        if element.startswith('\t') or element.startswith('    '):
            if self.list_item_inside:
                return True

    def condition(self, element):
        if element[:2] in self.flag:
            self.strip = element[:2]
            self.list_type = 'ulist'
            self.list_item_inside = True
            return True
        match = re.match(r'\d{1,2}\. ', element)
        if match:
            self.strip = match.group(0)
            self.list_type = 'olist'
            self.list_item_inside = True
            return True
        if self.list_break(element):
            return True

    def action(self, element, handler, *args):
        if self.condition(element):
            if element.startswith('\t') or element.startswith('    '):
                self.content.append(element)
            else:
                self.content.append(element.strip(self.strip))
            return 'list'
        if self.content:
            handler.start(self.list_type)  # 有序列表或者无序列表开始标签
            handler.start(self.type)
            handler.feed(self.content[0])
            for line in self.content[1:]:
                if line[0] != ' ' and not line.startswith('\t'):
                    handler.end(self.type)
                    handler.start(self.type)
                    handler.feed(line)
                else:
                    handler.start('break')
                    handler.feed(line.strip())
            handler.end(self.type)
            handler.end(self.list_type)  # 有序列表或者无序列表结束标签
            self.content = []
            self.list_item_inside = False


class CodeRule(Rule):
    type = 'code'
    inside = False
    content = []

    def condition(self, element):
        if element.startswith("```"):
            self.inside = not self.inside
            return True
        if self.inside:
            return True

    def action(self, element, handler, *args):
        if self.condition(element):
            self.content.append(element)
            return 'code'
        if self.content:
            handler.start(self.type)
            for line in self.content[1:-1]:
                handler.feed(line)
            handler.end(self.type)
            self.content = []


class ParagraphRule(Rule):
    type = 'paragraph'

    def condition(self, element):
        return True
