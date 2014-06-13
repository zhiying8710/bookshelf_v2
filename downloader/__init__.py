import os
from util import common, httputil, log, conns_helper, settings
import pycurl
import time
import re

def download(dest_dir, info):
    if not dest_dir.endswith(os.sep):
        dest_dir += os.sep
    url = info['url']
    filename = dest_dir + common._md5(url) + '.html'
    crl = httputil.init_pycurl()
    referer = None
    if 'referer' in info:
        referer = info['referer']
    if referer:
        crl.setopt(pycurl.REFERER, str(referer))  # @UndefinedVariable
    crl.setopt(pycurl.URL, str(url))  # @UndefinedVariable
    crl.fp = open(filename, "w")
    crl.setopt(pycurl.WRITEFUNCTION, crl.fp.write)  # @UndefinedVariable
    try:
        crl.perform()
    except:
        log.logger.warning(u"download url:%s failure, current thread sleep 10 seconds and try again!" %url)
        time.sleep(10)
        try:
            if os.path.exists(filename):
                os.remove(filename)
            crl.setopt(pycurl.WRITEFUNCTION, crl.fp.write)  # @UndefinedVariable
            crl.perform()
        except:
            raise Exception(u"download url: %s error, give up!" % url)
    finally:
        crl.fp.close()
    rcode = str(crl.getinfo(pycurl.RESPONSE_CODE))  # @UndefinedVariable
    if re.match("^(4|5)[0-9]{2}$", rcode):
#         if os.path.exists(filename):
#             os.remove(filename)
        msg = u"HTTP error code for url %s is %s"% (url, rcode)
        raise Exception(msg)
    else:
        info['fn'] = filename
        conns_helper.get_redis_conn().rpush(settings.download_info_queue, info)
