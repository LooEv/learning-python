from six import with_metaclass
from pymongo import MongoClient

mongo_client = MongoClient()


class ModelMetaClass(type):
    __collection__ = None

    def __init__(cls, name, bases, attrs):
        super(ModelMetaClass, cls).__init__(name, bases, attrs)
        cls.db = mongo_client.get_database('some_db')
        if cls.__collection__:
            cls.collection = cls.db.get_collection(cls.__collection__)


class Model(with_metaclass(ModelMetaClass, object)):
    __collection__ = 'model_base'

    @classmethod
    def insert(cls, **kwargs):
        doc = cls.collection.insert_one(kwargs)
        return doc


class Account(Model):
    __collection__ = 'account'


Account.insert(name='ql', age=27, location='cd')
