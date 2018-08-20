from redis import Redis
from mongoengine import connect


def redis_conn():
    return Redis()


def connect_mongo():
    connect('scorer')
