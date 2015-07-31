# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

from app.models.base import BaseModel
from app.utils import oid_to_str
from flask import session
from datetime import datetime
from bson import ObjectId
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class UsersModel(BaseModel):
    def __init__(self):
        super().__init__("users")

    def get_index(self, query=dict(), sort=('created', -1), password=True):
        users = super().get_index(query, sort=sort)
        if users["count"] > 0 and not password:
            for document in users["documents"]:
                del document['password']
        return users

    def get_by_id(self, oid, query=dict(), password=True):

        user = super().get_by_id(oid,query)
        if not password:
            del user['password']
        return oid_to_str(user)

    def get_by_identify(self, identify, password=True):

        user = self.col.find_one({"$or": [{"user_name": identify}, {"user_email": identify}]})
        if not password:
            del user['password']
        return oid_to_str(user)

    def post(self, data):
        return super().post(data)

    def patch(self, oid, data):
        logger.debug(data)
        if "password" in data:
            if data["password"] == "":
                del data['password']
            else:
                if data["password"] == data["password_confirm"]:
                    del data["password_confirm"]
                else:
                    #　パスワードがおかしい
                    raise Exception
        ret = super().patch(oid, data)
        if ret:
            ret = self.get_by_id(oid, password=False)
            session['auth'] = ret
        return ret

    def toggle_array(self, user_id, field, oid, operation):
        try:
            update = dict()
            toggle_data = {field: oid}
            if operation == 'add':
                update['$addToSet'] = toggle_data
            else:
                update['$pull'] = toggle_data
            update["$set"] = {"modified": datetime.now().strftime("%Y-%m-%dT%H:%M:%S")}
            logger.debug(update)
            self.col.update({"_id": ObjectId(user_id)}, update)
            ret = self.get_by_id(user_id, password=False)
            session['auth'] = ret
            return oid_to_str(ret)
        except Exception as e:
            logger.debug(e)
            return False

