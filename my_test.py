import asyncio
from asyncio import TimeoutError


async def func(n):
    if n == 5:
        raise TypeError('')
    await asyncio.sleep(0.5)
    return n


async def gather():
    # result = await asyncio.wait([func(i) for i in range(1, 9)])
    result = await asyncio.gather(*[func(i) for i in range(1, 9)], return_exceptions=True)
    print(result)


loop = asyncio.get_event_loop()
loop.run_until_complete(gather())
loop.close()
