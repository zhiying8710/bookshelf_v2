# Created on 2014-5-7
# @author: binge

import datetime
import lxml.etree;
from util import log, settings
from util.conns_helper import redis_exec, get_redis_conn

import base64
import os
import traceback
# import md5
try:
    from hashlib import md5
except ImportError:
    from md5 import md5

def _md5(s):
    return md5(s).hexdigest()

def _base64(s, e=True):
    if e:
        return base64.encodestring(s)
    else:
        return base64.decodestring(s)

class TimeHelper():

    @staticmethod
    def time_2_str(t=datetime.datetime.now(), frt='%Y-%m-%d %H:%M:%S', delta=None, delta_unit=None):
        '''
            this function parse time obj to str by frt parameter,
            parameter t is default datetime.datetime.now(),
            and parameter frt default %Y-%m-%d %H:%M:%S.
            delta_unit:
                        seconds
                        minutes
                        hours
                        days
                        ...
        '''
        if delta and delta_unit:
            delta_time_dict = {
                               'microseconds': lambda t, delta : t + datetime.timedelta(microseconds=delta),
                               'milliseconds': lambda t, delta : t + datetime.timedelta(milliseconds=delta),
                               'seconds' : lambda t, delta : t + datetime.timedelta(seconds=delta),
                               'minutes' : lambda t, delta : t + datetime.timedelta(minutes=delta),
                               'hours' : lambda t, delta : t + datetime.timedelta(hours=delta),
                               'days' : lambda t, delta : t + datetime.timedelta(days=delta),
                               'weeks' : lambda t, delta : t + datetime.timedelta(weeks=delta)
                               }
            t = delta_time_dict[delta_unit](t, delta)
        return t.strftime(frt)

def create_dom(data, parser=None):
    if not parser:
        parser = lxml.etree.HTMLParser()  # @UndefinedVariable
    return lxml.etree.fromstring(data, parser);  # @UndefinedVariable

@redis_exec(rconn=get_redis_conn())
def put_spider_info2queue(url, _exec, referer=None, rconn=None):
    rconn.sadd(settings.spider_info_queue, {'url' :  url, '_exec' : _exec, 'referer' : referer})

@redis_exec(rconn=get_redis_conn())
def get_last_crawl_time(spider_name, rconn=None):
    return rconn.hget(settings.last_crawl_time_key, spider_name)

@redis_exec(rconn=get_redis_conn())
def set_next_crawl_time(spider_name, time, rconn=None):
    rconn.hset(settings.last_crawl_time_key, spider_name, time)

def analysis():
    def wrapper(fn):
        def _exec(spider):
            f = None
            try:
                f = open(spider.fn)
                spider.content = f.read()
            except:
                log.logger.error('open spider %s file %s error.\n%s' % (spider.name, spider.fn, traceback.format_exc()))
            finally:
                if f:
                    f.close()
                if os.path.exists(spider.fn):
                    os.remove(spider.fn)
            if hasattr(spider, 'content'):
                ress = fn(spider)
                if ress:
                    for res in ress:
                        yield res
        return _exec
    return wrapper

def load_object(path):
    """Load an object given its absolute object path, and return it.

    object can be a class, function, variable o instance.
    path ie: 'scrapy.contrib.downloadermiddelware.redirect.RedirectMiddleware'
    """

    try:
        dot = path.rindex('.')
    except ValueError:
        raise ValueError, "Error loading object '%s': not a full path" % path

    module, name = path[:dot], path[dot+1:]
    try:
        mod = __import__(module, {}, {}, [''])
    except ImportError, e:
        raise ImportError, "Error loading object '%s': %s" % (path, e)

    try:
        obj = getattr(mod, name)
    except AttributeError:
        raise NameError, "Module '%s' doesn't define any object named '%s'" % (module, name)

    return obj
