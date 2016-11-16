# encoding=utf-8
# author=Loo

import platform
import time
import functools
import subprocess
import threading
import Queue
import multiprocessing
import socket

ip_prefix = ['180.97.33.', '14.17.32.']
length_of_ip_suffix = 256
ip_suffix = map(str, range(length_of_ip_suffix))
available_ip = []
port_opened = []

if platform.system().lower() == "windows":
    timer = time.clock
else:
    timer = time.time


def used_time(name):
    name = 'Using the {0} to scan ip '.format(name)

    def wrapper(func):
        @functools.wraps(func)
        def _wrapper(*args, **kwargs):
            global available_ip
            start_time = timer()
            func(*args, **kwargs)
            the_time_used = timer() - start_time
            print_available_ip()
            available_ip = []
            print name + "takes {:.3f} seconds".format(the_time_used)

        return _wrapper

    return wrapper


def ping(host):
    """Returns True if host responds to a ping request"""
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    return subprocess.call("ping " + ping_str + " " + host, shell=True) == 0


def ping_worker(prefix, queue, manager_list=None):
    result = []
    while not queue.empty():
        try:
            ip = prefix + str(queue.get(False))
            if ping(ip):
                if manager_list is None:
                    available_ip.append(ip)
                else:
                    result.append(ip)
        except Exception, e:
            print e

    if manager_list is not None:
        temp = manager_list
        temp.extend(result)
        manager_list = temp


def ping_worker2(prefix, some_ip_suffix):
    """some_ip_suffix represent some parts of the ip_suffix slicing by the number of threads"""
    # for suffix in some_ip_suffix:
    #     ip = prefix + suffix
    #     if ping(ip):
    #         available_ip.append(ip)
    judgement = [(prefix + suffix) for suffix in some_ip_suffix if ping(prefix + suffix)]
    available_ip.extend(judgement)


@used_time('threads')
def threads_scan_ip():
    """I use 64 threads,you can change it base on your situation"""
    q = Queue.Queue()
    for prefix in ip_prefix:
        map(q.put, xrange(length_of_ip_suffix))
        threads = [threading.Thread(target=ping_worker, args=(prefix, q, None)) for i in xrange(64)]
        # or you can use the ping_worker2,just pay attention to the usage of args. 256/64 = 4
        # threads =
        # [threading.Thread(target=ping_worker2, args=(prefix, ip_suffix[i*4 : (i+1)*4],)) for i in range(64)]
        map(lambda t: t.start(), threads)
        map(lambda t: t.join(), threads)


@used_time('multiprocess')
def multiprocess_scan_ip():
    """
    note that on Windows the subprocesses will import (i.e. execute) the main module at start.
    If the freeze_support() line is omitted then trying to run the frozen executable will raise RuntimeError.
    """
    multiprocessing.freeze_support()  # On windows,you had better use it.
    manager = multiprocessing.Manager()
    global manager_list, available_ip
    manager_list = manager.list()  # share
    q = multiprocessing.Queue()
    for prefix in ip_prefix:
        map(q.put, xrange(length_of_ip_suffix))
        jobs = [multiprocessing.Process(target=ping_worker, args=(prefix, q, manager_list)) for i in xrange(64)]
        map(lambda x: x.start(), jobs)
        map(lambda x: x.join(), jobs)
    available_ip = manager_list


@used_time('gevent')
def gevent_scan_ip():
    from gevent import monkey
    monkey.patch_all()
    import gevent
    from gevent.queue import Queue
    q = Queue()
    for prefix in ip_prefix:
        map(q.put, xrange(length_of_ip_suffix))
        coroutines = [gevent.spawn(ping_worker, prefix, q, None) for i in xrange(64)]
        gevent.joinall(coroutines)


def scan_port(ip, port):
    s = socket.socket()
    s.settimeout(0.1)
    if s.connect_ex((ip, port)) == 0:
        port_opened.append(port)
    s.close()


def port_worker(queue, ip):
    while not queue.empty():
        try:
            port = queue.get(False)
            scan_port(ip, port)
        except Exception, e:
            print e


def threads_scan_port():
    query_ip = 'localhost'
    q = Queue.Queue()
    map(q.put, xrange(1, 65535))
    threads = [threading.Thread(target=port_worker, args=(q, query_ip)) for i in range(100)]
    map(lambda t: t.start(), threads)
    map(lambda t: t.join(), threads)
    print "the {} has some open ports as follows:".format(query_ip)
    for port in port_opened:
        print port


def print_available_ip():
    print "The following ip addresses(%d) are available:" % len(available_ip)
    if len(ip_prefix) > 1:
        # group available_ip by the ip_prefix
        ip_set = [[ip for ip in available_ip if prefix in ip] for prefix in ip_prefix]
    else:
        ip_set = available_ip
    for index, ips in enumerate(ip_set):
        print ip_prefix[index], "has %d available ip addresses:" % len(ips)
        for ip in sorted(ips, key=lambda x: int(x.split('.')[-1])):
            print '\t', ip
        print


if __name__ == '__main__':
    threads_scan_ip()
    multiprocess_scan_ip()
    gevent_scan_ip()
    threads_scan_port()
    raw_input()
