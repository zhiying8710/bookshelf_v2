# encoding: utf-8
# Created on 2014-6-12
# @author: binge
import logging

logger = logging.getLogger("bookshelf")

logger.setLevel(logging.DEBUG)

fh = logging.FileHandler("bookshelf.log")
fh.setLevel(logging.DEBUG)
ch = logging.StreamHandler()
ch.setLevel(logging.ERROR)

formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
fh.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)
