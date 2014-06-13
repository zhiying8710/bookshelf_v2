from util import log, conns_helper, settings
import logging
import time

class base_spider(object):

    def __init__(self):
        self.rconn = conns_helper.get_redis_conn()

    def put_respotitory_info2redis(self, info):
        self.rconn.rpush(settings.repository_item_queue, info)

    def put_analysis_spider_info2redis(self, url, _exec):
        self.rconn.sadd(settings.spider_info_queue, {'url' :  url, '_exec' : _exec})

    def sleep(self, seconds):
        time.sleep(seconds)

    def log(self, msg, level=logging.INFO):
        if level == logging.INFO:
            log.logger.info(msg)
        if level == logging.WARNING:
            log.logger.warn(msg)
        if level == logging.DEBUG:
            log.logger.debug(msg)
        if level == logging.ERROR:
            log.logger.error(msg)

class respotitory_info(object):

    def __init__(self, info):
        self.info = info

    def get(self, k):
        if k in self.info:
            return self.info[k]
        else:
            return None

    def set(self, k, v):
        self.info[k] = v

    def __str__(self):
        return str(self.info)

class analysis_spider_info(object):

    def __init__(self, **kwargs):
        self.info = kwargs

    def get(self, k):
        if k in self.info:
            return self.info[k]
        else:
            return None

    def set(self, k, v):
        self.info[k] = v

    def __str__(self):
        return str(self.info)
