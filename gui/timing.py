#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : timing.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-08-12 23:06:57
@History :
@Desc    :
"""

import tkinter as tk
import tkinter.messagebox

from datetime import datetime

ROOT_WINDOW_WIDTH = 600
ROOT_WINDOW_HEIGHT = 400

HOUR = MINUTE = SECOND = 0
START_TIME = datetime.now()
START = False

label_start_x = 85
label_start_y = 100

TIMING_LABEL_LIST = []


def center_window(width=800, height=500):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()

    x = (screen_width / 2) - (width / 2)
    y = (screen_height / 2) - (height / 2)
    root.geometry('%dx%d+%d+%d' % (width, height, x, y))  # 设定窗口的大小(长 * 宽)


def timing():
    global label_start_y, HOUR, MINUTE, SECOND, START_TIME, START
    if START:
        a_label = tk.Label(root, bg=None, fg='black', font=('Arial', 14), width=20, height=1)
        a_label.place(x=label_start_x, y=label_start_y)
        diff_time = datetime.now() - START_TIME
        a_label.configure(text=str(diff_time))
        TIMING_LABEL_LIST.append(a_label)
        label_start_y += 30
    else:
        if timing_button.cget('text') != '复位':
            tkinter.messagebox.showerror('Error', '请先点击"开始"按钮')
        else:
            HOUR = MINUTE = SECOND = 0
        for label in TIMING_LABEL_LIST:
            label.destroy()
        label_start_y = 100


def set_time():
    global HOUR, MINUTE, SECOND, START_TIME, START
    if START:
        SECOND += 1
        if SECOND >= 60:
            SECOND = 0
            MINUTE += 1
            if MINUTE >= 60:
                MINUTE = 0
                HOUR += 1
    time_label.configure(text=f"{HOUR:0>2}:{MINUTE:0>2}:{SECOND:0>2}")
    root.after(1000, set_time)


def init_time():
    global HOUR, MINUTE, SECOND, START_TIME, START
    if not START:
        START = True
        HOUR = MINUTE = SECOND = 0
        START_TIME = datetime.now()
        start_button.configure(text='暂停')
        timing_button.configure(text='计时')
    else:
        START = False
        start_button.configure(text='开始')
        timing_button.configure(text='复位')


root = tk.Tk()

root.title('ClockT')
center_window(ROOT_WINDOW_WIDTH, ROOT_WINDOW_HEIGHT)
root.resizable(0, 0)  # 固定窗口大小

start_button = tk.Button(root, text='开始', font=('Arial', 14), width=5, height=1, command=init_time)
start_button.place(x=ROOT_WINDOW_WIDTH - 200, y=40)

timing_button = tk.Button(root, text='计时', font=('Arial', 14), width=5, height=1, command=timing)
timing_button.place(x=ROOT_WINDOW_WIDTH - 100, y=40)

time_label = tk.Label(root, text='00:00:00', bg=None, fg='black', font=('Arial', 16), width=20, height=1)
time_label.place(x=50, y=40)

root.after(0, set_time)
root.mainloop()
