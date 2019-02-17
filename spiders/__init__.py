from selectors import DefaultSelector, EVENT_READ, EVENT_WRITE
import socket
from types import coroutine
from urllib.parse import urlparse
import asyncio


@coroutine
def until_readable(fileobj):
    yield fileobj, EVENT_READ


@coroutine
def until_writable(fileobj):
    yield fileobj, EVENT_WRITE


async def connect(sock, address):
    try:
        sock.connect(address)
    except BlockingIOError:
        await until_writable(sock)


async def recv(fileobj):
    result = b''
    while True:
        try:
            data = fileobj.recv(4096)
            if not data:
                return result
            result += data
        except BlockingIOError:
            await until_readable(fileobj)


async def send(fileobj, data):
    while data:
        try:
            sent_bytes = fileobj.send(data)
            data = data[sent_bytes:]
        except BlockingIOError:
            await until_writable(fileobj)


async def fetch_url(url):
    parsed_url = urlparse(url)
    if parsed_url.port is None:
        port = 443 if parsed_url.scheme == 'https' else 80
    else:
        port = parsed_url.port

    with socket.socket() as sock:
        sock.setblocking(0)
        await connect(sock, (parsed_url.hostname, port))
        path = parsed_url.path if parsed_url.path else '/'
        path_with_query = '{}?{}'.format(path, parsed_url.query) if parsed_url.query else path
        await send(sock, 'GET {} HTTP/1.1\r\nHost: {}\r\nConnection: Close\r\n\r\n'.format(path_with_query,
                                                                                           parsed_url.netloc).encode())
        content = await recv(sock)
        print('{}: {}'.format(url, content[:10]))


def main():
    urls = ['http://www.baidu.com/s?wd={}'.format(i) for i in range(10)]
    tasks = [fetch_url(url) for url in urls]  # 将任务定义成协程对象

    with DefaultSelector() as selector:
        while tasks or selector.get_map():  # 有要做的任务，或者有等待的 IO 事件
            events = selector.select(0 if tasks else 1)  # 如果有要做的任务，立刻获得当前已就绪的 IO 事件，否则最多等待 1 秒
            for key, event in events:
                task = key.data
                tasks.append(task)  # IO 事件已就绪，可以执行新 task 了
                selector.unregister(key.fileobj)  # 取消注册，避免重复执行

            for task in tasks:
                try:
                    fileobj, event = task.send(None)  # 开始或继续执行 task
                except StopIteration:
                    pass
                else:
                    selector.register(fileobj, event, task)  # task 还未执行完，需要等待 IO，将 task 注册为 key.data

            tasks.clear()


# main()
# loop = asyncio.get_event_loop()
# loop.run_until_complete(fetch_url('www.baidu.com'))

import asyncio


# 一个对future进行赋值的函数
async def slow_operation(future):
    print('sdfsdfd')
    await asyncio.sleep(1)
    # 给future赋值
    future.set_result('Future is done!')


loop = asyncio.get_event_loop()
# 创建一个future
future1 = asyncio.Future()
# 使用ensure_future 创建Task
f1 = asyncio.ensure_future(slow_operation(future1))
future2 = asyncio.Future()
f2 = asyncio.ensure_future(slow_operation(future2))
# gather Tasks，并通过run_uniti_complete来启动、终止loop
# loop.run_until_complete(asyncio.gather(f1, f2))
loop.run_until_complete(asyncio.gather(future1, f2))
print(future1.result())
print(future2.result())
loop.close()
