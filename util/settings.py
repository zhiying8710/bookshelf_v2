# encoding: utf-8
# Created on 2014-6-12
# @author: binge

mongo_host = '127.0.0.1'
mongo_port = 27017
redis_host = '127.0.0.1'
redis_port = 6379
redis_def_db = 0
redis_sep = ':::'

download_file_dir = 'e:\\bookshelf\\download\\'
spider_info_queue = '__spider_info_queue'
download_info_queue = '__download_info_queue'

spider_info_retry_count_key = '__spider_info_retry_count'
spider_info_retry_times = 2

download_info_retry_count_key = '__download_info_retry_count'
down_info_retry_times = 2

repository_item_queue = '__repository_item_queue'

last_crawl_time_key = '__last_crawl_time'

us_search_spider_info_queue = '__us_search_spider_info_queue' # update site search spider info queue.

every_crawl_timedelta_mins = 5

source_spider_sleep_secs = 10 * 60

book_no_home_url_val = 'NONE'

spider_info_level_top = 1

start_url_info = [
                  {
                  'url' : 'http://all.qidian.com/Book/BookStore.aspx?ChannelId=-1&SubCategoryId=-1&Tag=all&Size=-1&Action=-1&OrderId=6&P=all&PageIndex=1&update=4',
                  '_exec' : 'spiders.qidian.qidian.start',
                  'referer' : 'http://qidian.com',
                  'level' : spider_info_level_top
                  },
                  ]
