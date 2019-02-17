import tornado.gen
import tornado.ioloop
from tornado.web import RequestHandler, Application

from utils.path_util import get_file_size, file_is_in_dir

route_list = []
DOWNLOAD_DIR = __file__ + '../..'


def read_file(file_path):
    chunk_size = 1024 * 64
    with open(file_path, 'rb') as f:
        while 1:
            chunk = f.read(chunk_size)
            if chunk:
                yield chunk
            else:
                break


def route(path):
    def inner(cls):
        route_list.append((path, cls))
        return cls

    return inner


@route(r'/download/(.*)')
class DownloadHandler(RequestHandler):

    @tornado.gen.coroutine
    def get(self, file_name, *args, **kwargs):
        # file_name = self.get_argument('file_name')
        file_path = DOWNLOAD_DIR + file_name
        if not file_is_in_dir(DOWNLOAD_DIR, file_path):
            self.write("can't find the file of %s" % file_name)
            return

        self.set_header("Content-Length", get_file_size(file_path))
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', 'attachment; filename=' + file_name)
        for content in read_file(file_path):
            self.write(content)
            yield self.flush()
        self.finish()


def make_app():
    _app = Application(route_list)
    return _app


if __name__ == '__main__':
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
