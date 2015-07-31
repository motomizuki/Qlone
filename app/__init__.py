# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'


from flask import Flask
from werkzeug.routing import BaseConverter
from logging import getLogger, StreamHandler, DEBUG
from pymongo import MongoClient
from config import APPLICATION_ROOT

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

# flask app
app = Flask(__name__, static_url_path=APPLICATION_ROOT+"/static")
app.config.from_pyfile("../config.py")
mongo = MongoClient(app.config['MONGO_HOST'])[app.config['MONGO_DBNAME']]


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

# Use the RegexConverter function as a converter
# method for mapped urls
app.url_map.converters['regex'] = RegexConverter