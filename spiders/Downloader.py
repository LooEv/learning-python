#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    : Downloader.py
@Author  : qloo
@Version : v1.0
@Time    : 2019-05-09 22:42:09
@History :
@Desc    :
"""

import logging
from requests import Session, Request
from requests.cookies import merge_cookies
from requests.exceptions import *

REQUEST_EXCEPTIONS_SET = (HTTPError, ConnectionError, ProxyError,
                          SSLError, Timeout, TooManyRedirects)

logger = logging.getLogger('spider')


class SyncDownLoader:
    def __init__(self, session=None, max_retry=5, timeout=60,
                 allow_redirects=True, use_proxy=True):
        self.session = session or Session()
        self.max_retry = max_retry
        self.timeout = timeout
        self.allow_redirects = allow_redirects
        self.use_proxy = use_proxy
        self.dont_raise_http_status_code_set = set()

    def request(self, url, method='GET', **kwargs):
        proxies = kwargs.pop('proxies', {})
        stream = kwargs.pop('stream', False)
        verify = kwargs.pop('verify', False)
        cert = kwargs.pop('cert', None)
        retry_times = kwargs.pop('retry_times', self.max_retry)
        dont_raise_http_status_code = kwargs.pop(
            'dont_raise_http_status_code', self.dont_raise_http_status_code_set
        )

        req = Request(method=method, url=url, **kwargs)
        prep = self.session.prepare_request(req)

        send_kwargs = {
            'timeout': kwargs.pop('timeout', self.timeout),
            'allow_redirects': kwargs.pop('allow_redirects', self.allow_redirects),
        }

        # TODO add get proxy
        # if self.use_proxy and not proxies:
        #     proxies = get_proxy()
        # elif not self.use_proxy:
        #     proxies = {}

        settings = self.session.merge_environment_settings(url, proxies, stream, verify, cert)
        send_kwargs.update(settings)
        retry_count = 0
        while retry_count <= retry_times:
            retry_count += 1
            try:
                response = self.session.send(prep, **send_kwargs)
                if response.status_code == 200:
                    return response
                elif response.status_code in dont_raise_http_status_code:
                    return response
                else:
                    logger.warning(f'response status_code: {response.status_code}')
            except REQUEST_EXCEPTIONS_SET:
                logger.exception(f'Error when request url: {url} ==> ')

            if retry_count <= retry_times:
                logger.warning(f'Retry {retry_count} times about url: {url}')

    def get(self, url, **kwargs):
        return self.request(url, 'GET', **kwargs)

    def post(self, url, data=None, json=None, **kwargs):
        return self.request(url, 'POST', data=data, json=json, **kwargs)

    def silence_http_status_code(self, status_code):
        self.dont_raise_http_status_code_set.add(status_code)

    def get_cookies(self):
        return self.session.cookies

    def update_cookies(self, cookie_dict):
        merge_cookies(self.session.cookies, cookie_dict)


