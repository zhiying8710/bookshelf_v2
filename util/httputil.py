#coding: utf-8
import urllib2,cookielib;
import lxml.etree;
import pycurl
import StringIO
import time

def loadData(url,data=None,decode=True,returnUrl=False,encoding="utf-8"):
    initOpener()
    opener = urllib2.build_opener()
    page = opener.open(fullurl = url, data = data)
    data = page.read()
    url = page.url;
    if decode:
        data = data.decode(encoding,'ignore');
    if returnUrl:
        return (data,url);
    return data;

def ajax(url):
    crl = initPycurl()
    crl.setopt(pycurl.URL, str(url))
    crl.fp = StringIO.StringIO()
    crl.setopt(pycurl.WRITEFUNCTION, crl.fp.write)
    try:
        crl.perform()
    except:
        time.sleep(5)
        crl.perform()
    return crl.fp.getvalue()

def createDom(data, parser = None):
    if not parser:
        parser = lxml.etree.HTMLParser()
    return lxml.etree.fromstring(data,parser);

def dom_to_str(dom, encoding = "utf-8", method="html"):
    return lxml.etree.tostring(dom, encoding=encoding, method=method)

def createTree(filename):
    f = open(filename, 'r')
    content = f.read()
    tree = createDom(content)
    f.close()
    return tree

def initOpener(host = None):
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11'),\
                         ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),\
                         ('Accept-Charset', 'GBK,utf-8;q=0.7,*;q=0.3'),\
                         ('Accept-Encoding', 'gzip,deflate,sdch'),\
                         ('Accept-Language', 'zh-CN,zh;q=0.8'),\
                         ('Connection', 'keep-alive')
                         ]
    if host:
        opener.addheaders.append(('Host', host))
    urllib2.install_opener(opener);

def debug_fn(info_type, info):
#    print info_type, "---->", info
    pass

def init_pycurl():
    headers = ['Accept:text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',\
               'Accept-Charset:GBK,utf-8;q=0.7,*;q=0.3',\
               'Accept-Language:zh-CN,zh;q=0.8',\
               'Connection:keep-alive'
               ]
    crl = pycurl.Curl()
    crl.setopt(pycurl.VERBOSE,1)
    crl.setopt(pycurl.USERAGENT, "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.79 Safari/535.11")
    crl.setopt(pycurl.MAXREDIRS, -1)
    crl.setopt(pycurl.FOLLOWLOCATION, 10)
    crl.setopt(pycurl.HTTPHEADER, headers)
    crl.setopt(pycurl.DEBUGFUNCTION, debug_fn)
    crl.setopt(pycurl.CONNECTTIMEOUT, 5)
    crl.setopt(pycurl.TIMEOUT, 10)
    return crl

def findDomFirst(tree,path):
    result = tree.xpath(path);

    if(len(result) == 0):
        return None;
    return result[0];


