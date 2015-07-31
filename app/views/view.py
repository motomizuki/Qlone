# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
from flask import Blueprint, request, render_template, abort
from app.utils import jwt_decode
from app.views.auth import check_login, authorized_user, login
from app.models import DOMAIN
from app import app
from app.decoretor import login_required
from bson import ObjectId
import re
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

module = Blueprint('view', __name__, url_prefix=app.config["APPLICATION_ROOT"])



@module.route("/")
def index():
    """
    ログイン，アカウント作成
    """
    user = check_login()
    if not user:
        return render_template("index.html", prefix=app.config["APPLICATION_ROOT"])

    return render_template("home.html", user=user, prefix=app.config["APPLICATION_ROOT"])


@module.route("/drafts/")
@login_required
def drafts(oid=None):
    """
    下書き一覧
    """
    user = authorized_user()
    return render_template("drafts.html", oid=oid, user=user, prefix=app.config["APPLICATION_ROOT"])


@module.route("/drafts/new")
@module.route("/drafts/<oid>/edit")
@login_required
def edit_drafts(oid=None):
    """
    下書き作成
    """
    user = authorized_user()
    model = DOMAIN["items"]
    draft = dict()
    if oid:
        draft = model.get_by_id(oid)
        draft['markdown'] = draft['markdown'].replace('\\', '\\\\').replace('\n', '\\n')
    return render_template("edit_drafts.html", oid=oid, user=user, draft=draft, prefix=app.config["APPLICATION_ROOT"])



@module.route("/<user_name>/items/<oid>")
@login_required
def item_page(user_name, oid):
    """
    記事閲覧
    """
    user = authorized_user()
    author = DOMAIN['users'].get_by_identify(user_name)
    model = DOMAIN['items']
    query = {'status': 'published', 'user_id': author['_id']}
    item = model.get_by_id(oid, query)
    comments = DOMAIN["comments"].get_index({'item_id': oid}, sort=('created', 1))
    stocks = DOMAIN["users"].get_index({'stocks': oid})
    del author['password']
    if item:
        return render_template('item.html', user=user, item=item, author=author, comments=comments, stocks=stocks,
                               prefix=app.config["APPLICATION_ROOT"])
    else:
        abort(404)


@module.route("/home/<user_name>/")
@module.route("/home/<user_name>/<target>")
@login_required
def user_page(user_name, target=None):
    """
    ユーザページ
    """
    user = authorized_user()
    author = DOMAIN['users'].get_by_identify(user_name, password=False)
    if author:
        model = DOMAIN['items']
        query = {'status': 'published', 'user_id': author['_id']}
        item = model.get_index(query, sort=("created", -1))
        comments = DOMAIN["comments"].get_index({'user_id': author['_id']})
        stock_ids = [ObjectId(x) for x in author['stocks']]
        stocks = model.get_index({'_id': {'$in': stock_ids}})
        followers = DOMAIN['users'].get_index({'following_users': author['user_name']}, password=False)
        return render_template('users.html', user=user, item=item, author=author, stocks=stocks, comments=comments,
                               followers=followers, target=target, prefix=app.config["APPLICATION_ROOT"])
    else:
        abort(404)



@module.route("/tags")
@login_required
def tags_index():
    """
    タグ一覧
    """
    user = authorized_user()
    model = DOMAIN['items']
    tags = model.get_all_tags()
    return render_template('tags_index.html', user=user, tags=tags, prefix=app.config["APPLICATION_ROOT"])


@module.route("/tags/<tag_name>")
@login_required
def tags_page(tag_name):
    """
    タグ詳細
    """
    user = authorized_user()
    model = DOMAIN['items']
    items = model.get_index({'tags': tag_name})
    follower = DOMAIN['users'].get_index({'following_tags': tag_name})
    return render_template('tags.html', user=user, items=items, tag_name=tag_name, follower_count=follower['count'],
                           prefix=app.config["APPLICATION_ROOT"])



@module.route("/settings")
@login_required
def setting():
    """
    設定ページ
    """
    user = authorized_user()
    return render_template('settings.html', user=user, prefix=app.config["APPLICATION_ROOT"])


@module.route("/search")
@login_required
def search():
    """
    検索
    """
    user = authorized_user()
    model = DOMAIN["items"]
    q = request.args.get("query")
    terms = q.split()
    title = map(lambda x: {"title": re.compile(".*"+x+".*")}, terms)
    tags = map(lambda x: {"tags": re.compile(".*"+x+".*")}, terms)

    query = {
        "$or": [{"$and": list(title)}, {"$and": list(tags)}]
    }

    result = model.get_index(query)
    return render_template("search_result.html", user=user, items=result,
                           query=q, prefix=app.config["APPLICATION_ROOT"])


@module.route("/session/activate")
def activate_page():
    """
    アカウントアクティベーション
    """
    token = request.args.get("token")
    if token:
        model = DOMAIN["users"]
        data = jwt_decode(token)
        user = model.get_by_id(data["_id"])
        if user["password"] == data["password"] and user["user_email"] == data["user_email"]:
            # activate user account
            model.patch(user["_id"], {"status": "active"})
            # login
            login(user["user_email"], user["password"])
        return render_template("session.html", message="アカウントを認証しました。", user=user, prefix=app.config["APPLICATION_ROOT"])
    else:
        return render_template("session.html", message="不正なトークンです。", user=None, prefix=app.config["APPLICATION_ROOT"])


@module.route("/session/account_created")
def created():
    return render_template("session.html", message="アカウントを作成しました。<br>メールに届いたURLをクリックし、<br>アカウントを認証してください。",
                           user=None, prefix=app.config["APPLICATION_ROOT"])
