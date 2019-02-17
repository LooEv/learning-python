import itertools


class InvalidConnClass(Exception):
    pass


class ConnectionPool:
    def __init__(self, connection_class=None, min_cached=0, max_cached=0,
                 max_connections=0, blocking=False, *connection_args,
                 **connection_kwargs):
        self.connection_class = connection_class
        self.min_cached = min_cached
        self.max_cached = max_cached
        self.max_connections = max_connections
        self.blocking = blocking
        self.connection_args = connection_args
        self.connection_kwargs = connection_kwargs

        if connection_class is None:
            raise InvalidConnClass("connection class can't be none!")

        if max_cached and max_cached < min_cached:
            self.max_cached = min_cached

        if max_connections and max_cached > max_connections:
            self.max_connections = max_cached

        self.active_connections = set()
        self.idle_connections = []
        self.idle_connections = [self.new_connection(*self.connection_args,
                                                     **self.connection_kwargs)
                                 for _ in range(min_cached)]

    def get_connection(self):
        try:
            connection = self.idle_connections.pop()
        except IndexError:
            connection = self.new_connection()
        self.active_connections.add(connection)
        return connection

    def new_connection(self, *args, **kwargs):
        count = len(self.active_connections) + len(self.idle_connections)
        if count > self.max_connections:
            raise Exception("Too many connections")
        return self.connection_class(*args, **kwargs)

    def release(self, connection, error=False):
        if not error:
            self.active_connections.remove(connection)
            self.idle_connections.append(connection)
        else:
            try:
                connection.close()
            except AttributeError:
                pass
            self.active_connections.remove(connection)

    def disconnect(self):
        acs, self.active_connections = self.active_connections, set()
        ics, self.idle_connections = self.idle_connections, []
        for connection in itertools.chain(acs, ics):
            connection.close()

    close = disconnect


if __name__ == '__main__':
    from pymongo import MongoClient

    mongo_pool = ConnectionPool(MongoClient, 5, 5, 10, False, '127.0.0.1', 27017)
    mongo_pool.disconnect()