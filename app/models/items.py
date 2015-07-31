__author__ = 'hmizumoto'
from flask import session
from app.models.base import BaseModel
from app.utils import render_md

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


class ItemsModel(BaseModel):
    def __init__(self):
        super().__init__("items")

    def post(self, data):
        user = session['auth']
        data["user_id"] = user['_id']
        data["user_name"] = user['user_name']
        if data["status"] == 'published':
            # 公開htmlの更新
            data["publish_html"], data["publish_toc"] = render_md(data["markdown"])  # render TOC HTML
        if isinstance(data['tags'], str):
            if data["tags"] == '' or data["tags"] == '\'\'':
                data['tags'] = []
            else:
                data['tags'] = [data['tags']]
        oid = super().post(data)
        if oid:
            data["_id"] = str(oid)
            return data
        return False

    def patch(self, oid, data):
        old_doc = self.get_by_id(oid)
        user = session['auth']

        if data["status"] == 'published':
            # 公開htmlの更新
            data["publish_html"], data["publish_toc"] = render_md(data["markdown"])  # render TOC HTML
        else:
            # 下書きの場合はmarkdown等のみ更新
            del data["status"]
        if old_doc['user_id'] == user["_id"]:
            if "_id" in data:
                del data["_id"]
            if isinstance(data['tags'], str):
                data['tags'] = [data['tags']]
            ret = super().patch(oid, data)
            if ret:
                data["_id"] = oid
                return data
        return False

    def delete(self, oid):
        user = session['auth']
        old_doc = self.get_by_id(oid)
        if user['_id'] == old_doc['user_id']:
            return super().delete(oid)
        else:
            raise ValueError

    def get_all_tags(self):
        ret = self.col.aggregate([
            {'$unwind': "$tags"},
            {'$group': {"_id": "$tags", "count": {"$sum": 1}}}])
        return list(ret)



