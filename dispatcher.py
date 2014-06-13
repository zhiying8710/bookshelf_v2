# encoding: utf-8
# Created on 2014-6-12
# @author: binge

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # @UndefinedVariable

from util import settings, conns_helper, log, common
from downloader import download
import threading
import time
import traceback
import os
import repository
import spiders

def monitor_spider_info_queue():
    rconn = conns_helper.get_redis_conn()
    while 1:
        info = rconn.spop(settings.spider_info_queue)
        try:
            if info:
                download(settings.download_file_dir, eval(info))
                rconn.hdel(settings.spider_info_retry_count_key, info)
        except:
            log.logger.error(traceback.format_exc())
            if 'leval' in eval(info) and eval(info)['level'] == 1:
                rconn.sadd(settings.spider_info_queue, info)
                continue
            i = rconn.hincrby(settings.spider_info_retry_count_key, info, 1)
            if i > settings.spider_info_retry_times: # give up this info
                log.logger.warn('%s is retry %d times, give up!' % (info, settings.spider_info_retry_times))
                rconn.hdel(settings.spider_info_retry_count_key, info)
            else:
                rconn.sadd(settings.spider_info_queue, info)
        finally:
            time.sleep(1)
    conns_helper.close_redis_conn(rconn)

def monitor_download_queue():
    rconn = conns_helper.get_redis_conn()
    while 1:
        info = rconn.lpop(settings.download_info_queue)
        if not info:
            time.sleep(1)
            continue
        try:
            _info = eval(info)
            _exec = _info['_exec']
            cls = '.'.join(_exec.split('.')[:-1])
            spider_cls = common.load_object(cls)
            spider = spider_cls(fn = _info['fn'], url = _info['url'])
            func = _exec.split('.')[-1]
            for res in getattr(spider, func).__call__():
                if not res:
                    continue
                if res.__class__ is spiders.analysis_spider_info:
                    common.put_spider_info2queue(res.get('url'), res.get('_exec'), res.get('referer'))
                elif res.__class__ is spiders.respotitory_info:
                    repository.repository(res)
                else:
                    del res
            rconn.hdel(settings.download_info_retry_count_key, info)
        except:
            log.logger.error(traceback.format_exc())
            i = rconn.hincrby(settings.download_info_retry_count_key, info, 1)
            if i > settings.down_info_retry_times: # give up this info
                log.logger.warn('%s is retry %d times, give up!' % (info, settings.down_info_retry_times))
                rconn.hdel(settings.download_info_retry_count_key, info)
            else:
                rconn.lpush(settings.download_info_queue, info)
        finally:
            time.sleep(1)
    conns_helper.close_redis_conn(rconn)


def start(ths=50):
    for info in settings.start_url_info:
        common.put_spider_info2queue(info['url'], info['_exec'], info['referer'])

    for _ in xrange(ths):
        threading.Thread(target=monitor_spider_info_queue).start()

    for _ in xrange(ths):
        threading.Thread(target=monitor_download_queue).start()

if __name__ == '__main__':
    if not os.path.exists(settings.download_file_dir):
        os.makedirs(settings.download_file_dir)
    start()
