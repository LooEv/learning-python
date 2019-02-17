from abc import ABC, abstractmethod


class DBManagerBase(ABC):
    @abstractmethod
    def get(self, *args, **kwargs):
        pass

    @abstractmethod
    def insert(self, *args, **kwargs):
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass


class DBManager(DBManagerBase):
    def __init__(self, db_conn_pool=None):
        if db_conn_pool is None:
            raise Exception("")

    def insert(self, *args, **kwargs):
        pass

    def get(self, *args, **kwargs):
        pass

    def update(self, *args, **kwargs):
        pass

    def delete(self, *args, **kwargs):
        pass
