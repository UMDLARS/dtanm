import os
from redis import Redis
from mongoengine import connect


def redis_conn():
    return Redis(host=os.environ.get('REDIS_HOST', 'localhost'),
                 port=os.environ.get('REDIS_PORT', 6379),
                 db=os.environ.get('REDIS_DB', 0))


def connect_mongo():
    connect(db=os.environ.get('MONGO_DB', 'scorer'),
            host=os.environ.get('MONGO_HOST', 'localhost'),
            port=os.environ.get('MONGO_PORT', 27017))
