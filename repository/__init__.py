import spiders
from util import log, conns_helper, common, settings

@conns_helper.redis_mongo_exec(rconn=conns_helper.get_redis_conn(), mongo=conns_helper.get_mongo())
def repository_book(book, rconn=None, mongo=None):
    db = mongo.bookshelf
    source = book.get('source')
    _id = common._md5(source)  # gene _id
    _book = db.books.find_one({'_id' : _id})

    if not _book:  # this book has never been crawled.
        book.set('_id', _id)
        book.set('update_time', common.TimeHelper.time_2_str())
        db.books.insert(book.info)  # insert it to mongodb
        # this book must be searched in other update sites.
        rconn.sadd(settings.us_search_spider_info_queue, {'b_id' : _id, 'b_name' : book.get('name'), 'b_author' : book.get('author'), 'us' : {}})
    else:  # this book has been crawled once or more.
        book_homes = _book['homes']
        for home in book_homes:
            home_url = book_homes[home]
            if home_url and not home_url == settings.book_no_home_url_val and not home_url == source:
                rconn.rpush(settings.spider_info_queue, {'url' :  home_url, '_exec' : 'spiders.%s.%s.home' % (home, home), 'referer' : home_url})
        rconn.sadd(settings.us_search_spider_info_queue, {'b_id' : _id, 'b_name' : _book['name'], 'b_author' : _book['author'], 'us' : book_homes})

_execs = {
          'book' : repository_book,
          }

def repository(item):
    _type = item.get('type')
    if _type and _type in _execs:
        print _type
        _execs[_type](item)
    else:
        log.logger.warning('%s type is none or error.' % str(item))
        del item
