#!/usr/bin/env python
# coding=utf-8

__author__ = 'Loo'


class Handler(object):
    def callback(self, prefix, name, *args):
        method = getattr(self, prefix + name, None)  # 当调用的方法不存在的时候将method的值设为 None
        # if callable(method):
        if hasattr(method, '__call__'):  # 推荐使用这种方式
            return method(*args)

    def start(self, name, *args):
        self.callback('start_', name, *args)

    def end(self, name, *args):
        self.callback('end_', name, *args)

    def sub(self, name):
        def substitution(match):
            result = self.callback('sub_', name, match)
            if result is None:
                result = match.group(0)
            return result

        return substitution


class HTMLRenderer(Handler):
    document = """<!DOCTYPE html>
                    <html>
                    <head>
                    <title>Home
                    </title>
                    <style type="text/css">
                    body {background-color: lightcyan;}
                    div {width: 55%;text-align:left;margin:auto;}
                    pre, code {
                      font-size: 14px;font-family: Consolas, "Liberation Mono", Courier, monospace;}

                    code {
                      margin: 0 0px;padding: 0px 0px;white-space: nowrap;
                      border: 1px solid #eaeaea;background-color: #f8f8f8;
                      border-radius: 3px;}

                    pre>code {
                      margin: 0;padding: 0;white-space: pre;
                      border: none;background: transparent;}

                    pre {
                      background-color: #f8f8f8;border: 1px solid #ccc;
                      font-size: 13px;line-height: 19px;overflow: auto;
                      padding: 6px 10px;border-radius: 3px;}

                    pre code {background-color: transparent;border: none;}
                    </style>
                    </head>
                    <body>
                    <div>
                """

    def start_document(self):
        print self.document

    def end_document(self):
        print '</div></body></html>'

    def start_paragraph(self):
        print '<p>'

    def end_paragraph(self):
        print '</p>'

    def start_heading(self, *args):
        print '<h%d>' % args[0]

    def end_heading(self, *args):
        print '</h%d>' % args[0]

    def start_ulist(self):
        print '<ul>'

    def end_ulist(self):
        print '</ul>'

    def start_olist(self):
        print '<ol>'

    def end_olist(self):
        print '</ol>'

    def start_list_item(self):
        print '<li>'

    def end_list_item(self):
        print '</li>'

    def start_code(self):
        print '<pre><code>'

    def end_code(self):
        print '</code></pre>'

    def start_break(self):
        print '<br>'

    def sub_emphasis_or_strong(self, match):
        if match.group(0).startswith('**'):
            return '<strong>%s</strong>' % match.group(1).strip('*')
        return '<em>%s</em>' % match.group(1)

    def sub_url(self, match):
        text = match.group(1) if match.group(1) else ''
        return '<a href="%s">%s</a>' % (match.group(2), text)

    def sub_mail(self, match):
        return '<a href="mailto:%s">%s</a>' % (match.group(1), match.group(1))

    def sub_image(self, match):
        alt_text = match.group(1) if match.group(1) else ''
        return '<img src=%s alt=%s style="max-width:100%%;">' % (match.group(2), alt_text)

    def feed(self, data):
        print data
