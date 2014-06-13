# encoding: utf-8
# Created on 2014-5-13
# @author: binge

import traceback
from util import settings, log
import redis
import pymongo

def get_redis_conn():
    return redis.Redis(host=settings.redis_host, port=settings.redis_port, db=settings.redis_def_db)

def close_redis_conn(rconn):
    if rconn:
        del rconn

def get_mongo():
    return pymongo.Connection(settings.mongo_host, settings.mongo_port)

def close_mongo(mongo):
    if mongo:
        mongo.close()

def redis_exec(rconn):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(rconn=rconn, *args, **kwargs)
            except:
                log.logger.error(traceback.format_exc())
            finally:
                close_redis_conn(rconn)
        return _exec
    return wrapper

def mongo_exec(mongo):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(mongo=mongo, *args, **kwargs)
            except:
                log.logger.error(traceback.format_exc())
            finally:
                close_mongo(mongo)
        return _exec
    return wrapper

def redis_mongo_exec(rconn, mongo):
    def wrapper(fn):
        def _exec(*args, **kwargs):
            try:
                return fn(rconn=rconn, mongo=mongo, *args, **kwargs)
            except:
                log.logger.error(traceback.format_exc())
            finally:
                close_redis_conn(rconn)
                close_mongo(mongo)
        return _exec
    return wrapper
