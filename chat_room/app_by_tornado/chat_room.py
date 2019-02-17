import tornado.ioloop
from tornado.web import RequestHandler, Application

route_list = []


def route(path):
    def inner(cls):
        route_list.append((path, cls))
        return cls

    return inner


@route(r'/')
class Home(RequestHandler):
    def get(self, *args, **kwargs):
        self.write("Hello world")


def make_app():
    app = Application(route_list)
    # app = Application([(r'/', Home)])
    return app


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
