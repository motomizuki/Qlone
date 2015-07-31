# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
from app import app
from app import mongo
import pymongo
from bson import ObjectId
import datetime
from app.utils import oid_to_str

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class BaseModel:
    """
    model for mongodb
    """
    def __init__(self, collection):
        self.col = mongo[collection]

    def get_index(self, query=dict(), sort=('created', -1), per_page=20, page=1):
        try:
            response = dict()
            find = self.col.find(query)
            response["count"] = find.count()
            find = find.sort(sort[0], sort[1])
            logger.debug([page, per_page])
            if per_page > 0 and page > 0:
                find = find.skip((page-1) * per_page).limit(per_page)
                response["page"] = page
                response["per_page"] = per_page
            response["documents"] = oid_to_str(list(find))
            return response
        except Exception as e:
            raise e

    def get_by_id(self, oid, query=dict()):
        query['_id'] = ObjectId(oid)
        document = self.col.find_one(query)
        return oid_to_str(document)

    def post(self, data):
        try:
            data["created"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            data["modified"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            return oid_to_str(self.col.insert(data))
        except Exception as e:
            raise e

    def patch(self, oid, data):
        if len(data) < 1:
            return False
        try:
            if '_id' in data:
                del data['_id']
            data["modified"] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
            updates = {"$set": data}
            self.col.update({"_id": ObjectId(oid)}, updates)
            return True
        except Exception as e:
            raise e

    def delete(self, oid):
        try:
            self.col.remove({"_id": ObjectId(oid)})
            return True
        except Exception as e:
            raise e