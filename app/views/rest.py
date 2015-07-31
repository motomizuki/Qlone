# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

from flask import Blueprint, request, abort
from app.utils import prep_response, parse_request
from app.models import DOMAIN
from app import app
from app.decoretor import authorize_required
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

module = Blueprint('rest', __name__, url_prefix=app.config["APPLICATION_ROOT"])

'''
routeの重複を防ぐために全部書く
@module.route('/collection', methods=['GET', 'POST'])
@authorize_required
def rest_collection():
    return __rest_collection('collection')

@module.route('/collection/<oid>', methods=['GET', 'POST'])
@authorize_required
def rest_doc_collection(oid):
    return __rest_document('collection', oid)


'''
@module.route('/users', methods=['GET', 'POST'])
@authorize_required
def rest_users():
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    return __rest_collection('users', per_page=per_page, page=page)

@module.route('/users/<oid>', methods=['GET', 'POST', 'DELETE'])
def rest_doc_users(oid):
    return __rest_document('users', oid)


@module.route('/items', methods=['GET', 'POST'])
@module.route('/items/', methods=['GET', 'POST'])
@authorize_required
def rest_items():
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    query = {'status': 'published'}
    return __rest_collection('items', query, per_page=per_page, page=page)


@module.route('/items/<oid>', methods=['GET', 'POST', 'DELETE'])
@authorize_required
def rest_doc_items(oid):
    return __rest_document('items', oid)


@module.route('/comments', methods=['GET', 'POST'])
@authorize_required
def rest_comments():
    page = request.args.get('page', default=0, type=int)
    per_page = request.args.get('per_page', default=0, type=int)
    return __rest_collection('comments', sort=("created", 1), per_page=per_page, page=page)


@module.route('/comments/<oid>', methods=['GET', 'POST', 'DELETE'])
@authorize_required
def rest_doc_comments(oid):
    return __rest_document('comments', oid)


def __rest_collection(collection, query=dict(), sort=("created", -1), per_page=0, page=0):
    if collection in DOMAIN:
        model = DOMAIN[collection]
        try:
            if request.method == 'GET':
                ret = model.get_index(query, sort, per_page, page)
                logger.debug(ret)
                return prep_response(ret)
            elif request.method == 'POST':
                data = parse_request(request.form)
                ret = model.post(data)
                return prep_response(ret, 201)
        except ValueError as e:
            logger.debug(e)
            return prep_response(str(e), 400)
        except Exception as e:
            logger.debug(e)
            return prep_response(str(e), 500)
    abort(404)


def __rest_document(collection, oid):
    if collection in DOMAIN:
        model = DOMAIN[collection]
        try:
            if request.method == "GET":
                ret = model.get_by_id(oid)
                return prep_response(ret)
            elif request.method == "POST":
                data = parse_request(request.form)
                ret = model.patch(oid, data)
                return prep_response(ret)
            elif request.method == "DELETE":
                model.delete(oid)
                return prep_response(dict(), 204)
        except ValueError as e:
            return prep_response(str(e), 400)
        except Exception as e:
            logger.debug(e)
            return prep_response(str(e), 500)
    abort(404)


