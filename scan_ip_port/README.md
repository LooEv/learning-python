## 多线程、多进程、协程扫描ip和可用的端口
此脚本意在学习多线程threading、多进程multiprocessing、协程以及subprocess的使用。使用subprocess调用系统的ping命令检测给定的ip地址是否能ping通，使用socket扫描给定的ip地址有哪些可用的端口。

使用装饰器编写了一个计时器，以便比较多线程、多进程和协程的性能。
```python
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
```
**另外**，在计时方面，在Windows中最好使用time.clock()函数，而在其他平台上最好使用time.time()。
```python
if platform.system().lower() == "windows":
    timer = time.clock
else:
    timer = time.time
```
程序的执行时间总是和运行环境相关的，因为你不能保证程序每一次运行的环境都是相同的，而且不可能运行在一个拥有无限的资源的环境中。在测量运行时间时，多次测量取平均值要比只运行一次得到的结果要更符合事实。

利用subprocess调用系统的ping命令，函数实现如下：
```python
def ping(host):
    """Returns True if host responds to a ping request"""
    ping_str = "-n 1" if platform.system().lower() == "windows" else "-c 1"
    return subprocess.call("ping " + ping_str + " " + host, shell=True) == 0
```