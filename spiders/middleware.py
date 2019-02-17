from collections import defaultdict


def process_chain(method_list, obj, *args):
    for method in method_list:
        method(obj, *args)


class MiddlewareManager:
    component_name = 'foo middleware'

    def __init__(self, *middlewares):
        self.middlewares = middlewares
        self.methods = defaultdict(list)
        for mw in middlewares:
            self._add_middleware(mw)

    @classmethod
    def _get_mwlist_from_settings(cls, settings):
        raise NotImplementedError

    @classmethod
    def from_settings(cls, settings, crawler=None):
        pass
        # return cls(*middlewares)

    @classmethod
    def from_crawler(cls, crawler):
        return cls.from_settings(crawler.settings, crawler)

    def _add_middleware(self, mw):
        if hasattr(mw, 'process_request'):
            self.methods['process_request'].append(mw.open_spider)
        if hasattr(mw, 'process_response'):
            self.methods['process_response'].insert(0, mw.close_spider)

    def _process_chain(self, methodname, obj, *args):
        return process_chain(self.methods[methodname], obj, *args)

    def process_request(self, spider):
        return self._process_chain('process_request', spider)

    def process_response(self, spider):
        return self._process_chain('process_response', spider)
