# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

from flask import Blueprint, request, send_file
from logging import getLogger, StreamHandler, DEBUG
from app.views.auth import authorized_user
from app.utils import prep_response, allowed_file, img_upload
from app.decoretor import authorize_required
from app.models import DOMAIN
from app import app
from bson import ObjectId
import os

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

module = Blueprint('api', __name__, url_prefix=app.config["APPLICATION_ROOT"])


@module.route('/authenticated_user/items')
@authorize_required
def authenticated_users_items():
    user = authorized_user()
    model = DOMAIN['items']
    status = request.args.get('status')
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    query = {
        'user_id': user['_id'],
        'status': status
    }
    items = model.get_index(query, page=page, per_page=per_page)
    logger.debug(items["page"])
    return prep_response(items)


@module.route('/stocks/<regex("[0-9a-f]{24}"):oid>')
@authorize_required
def get_stock_user(oid):
    model = DOMAIN['users']
    query = {
        'stocks': oid
    }
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    ret = model.get_index(query, per_page=per_page, page=page)
    return prep_response(ret)


@module.route('/<user_name>/feeds')
@authorize_required
def get_feeds(user_name):
    user = authorized_user()
    model = DOMAIN['items']
    query = {
        'status': 'published',
        '$or': [
            {'user_id': {'$in': user['following_users']}},
            {'tags': {'$in': user['following_tags']}},
        ],
    }
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    ret = model.get_index(query, per_page=per_page, page=page)
    return prep_response(ret)


@module.route('/stocks/<user_name>')
@authorize_required
def get_stocked_items(user_name):
    user = authorized_user()
    model = DOMAIN['items']
    item_ids = [ObjectId(oid) for oid in user['stocks']]
    query = {
        'status': 'published',
        '_id': {'$in': item_ids}
    }
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    ret = model.get_index(query, per_page=per_page, page=page)
    return prep_response(ret)



@module.route('/toggle_stocks/<oid>/<operation>')
@authorize_required
def toggle_stock(oid, operation):
    user = authorized_user()
    model = DOMAIN['users']
    ret = model.toggle_array(user['_id'], "stocks", oid, operation)
    return prep_response(ret)


@module.route('/toggle_tags/<oid>/<operation>')
@authorize_required
def toggle_follow_tag(oid, operation):
    user = authorized_user()
    model = DOMAIN['users']
    ret = model.toggle_array(user['_id'], 'following_tags', oid, operation)
    return prep_response(ret)


@module.route('/toggle_users/<oid>/<operation>')
@authorize_required
def toggle_follow_user(oid, operation):
    user = authorized_user()
    model = DOMAIN['users']
    ret = model.toggle_array(user['_id'], 'following_users', oid, operation)
    return prep_response(ret)


@module.route("/<user_name>/items/<oid>/comments")
@authorize_required
def get_items_comments(user_name, oid):
    model = DOMAIN['comments']
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)

    ret = model.get_index({"item_id": oid}, sort=('created', 1), per_page=per_page, page=page)
    return prep_response(ret)


@module.route('/images/<filename>')
@authorize_required
def get_image(filename):
    """
    only authorized user could access images
    :param filename:
    :return:
    """
    img_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(img_path)


@module.route('/<user_name>/icon')
@authorize_required
def get_user_icon(user_name):
    """
    get user's icon
    :param user_name:
    :return:
    """
    user = DOMAIN['users'].get_by_identify(user_name)
    if user:
        img_path = os.path.join(app.config['UPLOAD_FOLDER'], user['user_icon'])
        return send_file(img_path)
    else:
        return prep_response('Not Found', 404)


@module.route('/upload', methods=['POST'])
@authorize_required
def upload():
    try:
        uploaded_files = request.files.getlist("files[]")
        filenames = img_upload(uploaded_files)
        if len(filenames) > 0:
            urls = ['/images/'+x for x in filenames]
            return prep_response({"files_url": urls})
    except:
        pass

    return prep_response('Upload error', 500)


@module.route('/upload/icon', methods=['POST'])
@authorize_required
def upload_icon():
    try:
        user = authorized_user()
        uploaded_files = request.files.getlist("files[]")
        if len(uploaded_files) > 1:
            uploaded_files = [uploaded_files[-1]]
        filenames = img_upload(uploaded_files)
        if len(filenames) > 0:
            # removed old image
            if user['user_icon'] != 'default.png':
                os.remove(os.path.join(app.config['UPLOAD_FOLDER'], user['user_icon']))
            DOMAIN['users'].patch(user['_id'], {'user_icon': filenames[-1]})
            return prep_response({})
    except Exception as e:
        logger.debug(str(e))

    return prep_response('Upload error', 500)