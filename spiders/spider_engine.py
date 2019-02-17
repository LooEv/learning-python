import asyncio
import re
import types
import traceback

from aiohttp.client import ClientSession
from collections import deque
from urllib.parse import urljoin

from fetchman.spider.spider_core import SeleniumDownLoader
from scrapy.selector import Selector
from scrapy.crawler import CrawlerProcess, CrawlerRunner


class Request:
    def __init__(self, url, method='GET', callback=None, errback=None,
                 body=None, header=None, is_async=True, dont_filter=False):
        self.url = url
        self.method = method
        self.callback = callback
        self.errback = errback
        self.body = b'' if body is None else body.encode()
        self.header = header
        self.is_async = is_async
        self.dont_filter = dont_filter

    def __str__(self):
        return "<Request [%s] [%s]>" % (self.method, self.url)

    __repr__ = __str__


class Response:
    def __init__(self, request, text, status=200):
        self.request = request
        self.url = request.url
        self.text = text
        self.status = int(status)

    def __getattribute__(self, name):
        if name == 'xpath':
            return Selector(text=self.text).xpath
        elif name == 'css':
            return Selector(text=self.text).css
        return super().__getattribute__(name)

    def urljoin(self, url):
        return urljoin(self.url, url)

    def __str__(self):
        return "<Response [%s] [%s]>" % (self.status, self.url)

    __repr__ = __str__


class SpiderEngine:
    session = None

    def __init__(self, spider, downloader):
        self.spider = spider
        self.downloader = downloader

    async def init_session(self, **kwargs):
        self.session = await ClientSession(**kwargs).__aenter__()

    async def run(self):
        nextrequest = next(self.spider.crawl())
        if isinstance(nextrequest, Request):
            nextrequest = [nextrequest]
        while 1:
            responses = await self.request(nextrequest)
            nextrequest = self.nextrequest(nextrequest, responses)
            if not nextrequest:
                break
        await self.session.close()

    async def request(self, request_list):
        tasks = [self.get_html(self.session, request) for request in request_list]
        responses = await asyncio.gather(*tasks)
        return responses

    async def get_html(self, session, request):
        try:
            # async with session.get(request.url) as req:
            #     text = await req.text()
            #     return Response(request, text, req.status)
            return await self.downloader.fetch(request, session)
        except Exception:
            print('request {} failed'.format(request.url), traceback.format_exc())
        return Response(request, '', 404)

    def nextrequest(self, request, response):
        req_list = []

        for index, req in enumerate(request):
            future_result = req.callback(response[index])
            if isinstance(future_result, types.GeneratorType):
                for _req in future_result:
                    req_list.append(_req)
            else:
                pass
        return req_list


class DownLoader:
    def __init__(self, use_proxy=False):
        self._use_proxy = use_proxy
        self._cookies = None

    @property
    def use_proxy(self):
        return self._use_proxy

    @use_proxy.setter
    def use_proxy(self, flag: bool):
        self._use_proxy = flag

    async def fetch(self, request: Request, session: ClientSession):
        if self.use_proxy:
            # method, url, *,
            # params = None,
            # data = None,
            # json = None,
            # headers = None,
            # skip_auto_headers = None,
            # auth = None,
            # allow_redirects = True,
            # max_redirects = 10,
            # compress = None,
            # chunked = None,
            pass
        try:
            biu = session.request(request.method, request.url,
                                  headers=request.header,
                                  data=request.body)
            async with biu as req:
                text = await req.text()
                return Response(request, text, req.status)
        except Exception:
            pass


class Scheduler:
    def __init__(self):
        self.queue = deque()

    def start(self, engine):
        pass


class Spider:
    urls_seen = set()

    def crawl(self):
        url = 'http://cd96527.cdta.gov.cn/list-29-1.html'
        # url = 'http://www.gsxt.gov.cn/%7BAD0F0239CA69F3B4261DA80B991A4FBC87AFFD6FCCE4675E53F0033810965368DDF5764F42E1B3F404F7B04012A7F55681706D589CB99F95B0ADB1BB9E9FD7C3813381338195D765D765D765D7E65465DB695869DBDDECEADB8397180C2CD58006EF4AD85B0E79CC3FAD003100BEAA3E6C2BDB89A1F466CBFA48FA48FA48-1547212708217%7D'
        print('start to request %s' % url)
        yield Request(url, callback=self.parse)

    def parse(self, response):
        print('start to parse {}'.format(response.url))
        yield from self.parse_list(response)
        pages_text = response.xpath('//a[text()="末页"]/@href').extract_first()
        pages = int(re.search(r'list-29-(\d+)\.html', pages_text).group(1))
        base_url = urljoin(response.url, re.sub(r'list-29-\d+\.html', 'list-29-{}.html', pages_text))
        print('it has {} pages'.format(pages))

        for page in range(2, pages + 1):
            print('start to request page({})'.format(page))
            url = base_url.format(page)
            yield Request(url, callback=self.parse_list)

    def parse_list(self, response):
        try:
            url_list = response.xpath('//div[@class="data"]//span[@class="title"]//a/@href').extract()
            print('it fetches {} urls in {}'.format(len(url_list), response.url))
            for url in url_list:
                url = urljoin(response.url, url.strip())
                print('start to request url: {}'.format(url))
                yield Request(url, callback=self.parse2)
                break
        except Exception:
            print('failed to get list page!', traceback.format_exc())

    def parse2(self, response):
        # url = 'http://icanhazip.com/'
        # print('start to request %s' % url)
        # yield Request(url, callback=self.get_ip)
        print(response)
        print(''.join(response.xpath('//div[@class="con-title"]//text()').extract()))

    def get_ip(self, reponse):
        print(reponse.text)


import time

t = time.time()
spider = Spider()
spider_engine = SpiderEngine(spider, DownLoader())
loop = asyncio.get_event_loop()
loop.run_until_complete(spider_engine.init_session())
loop.run_until_complete(spider_engine.run())
print(time.time() - t)
