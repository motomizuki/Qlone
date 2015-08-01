# -*- coding: utf-8 -*-
__author__ = 'h.mizumoto'

from flask import Blueprint, request, session, redirect
from app.utils import parse_request, prep_response, send_token, password_encryption
from app.models import DOMAIN
from app import app
from logging import getLogger, StreamHandler, DEBUG

logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

module = Blueprint('auth', __name__, url_prefix=app.config["APPLICATION_ROOT"])


@module.route('/api/auth/login', methods=['POST'])
def auth_login():
    """
    :post_param {string} identify: required
    :post_param {string} password: required
    :return {number} code: status code
    :return {string} token: jwt
    :return {object} user: user info
    :desc:
        user login and get token, user data.
    """
    try:
        data = parse_request(request.form)
        user = login(data['identify'], data['password'])
        if user:
            return prep_response(user)

        return prep_response("invalid identify or password", 401)
    except Exception as e:
        logger.debug(e)
        return prep_response("invalid params", 400)


@module.route('/api/auth/logout')
def auth_logout():
    session.pop('auth', None)
    return redirect(app.config["APPLICATION_ROOT"]+"/")


@module.route('/api/auth/create_account', methods=['POST'])
def create_account():
    try:
        data = parse_request(request.form)
        if set(['user_email', 'user_name', 'password']) > data.keys() \
                or data['user_name'] == '' or data['password'] == '':
            return prep_response('invalid param', 400)

        if len(app.config["ALLOW_DOMAIN"]) > 1 and data["user_email"].split("@")[1] not in app.config["ALLOW_MAIL"]:
                return prep_response('invalid email', 400)

        model = DOMAIN['users']
        user = model.get_index({"$or": [{"user_name": data["user_name"]}, {'user_email': data['user_email']}]})
        if user["count"] > 0:
            return prep_response("existed user name or email address.", 400)

        user = {
            "user_name": data['user_name'],
            "user_email": data["user_email"],
            'user_icon': "default.png",
            "password": password_encryption(data['password']),
            "profile": {
                "first_name": '',
                "last_name": '',
                "organization": '',
                "description": ''
            },
            'stocks': [],
            'following_tags': [],
            'following_users': [],
            "status": "inactive"
        }
        if app.config["MAIL_AUTH"]:
            oid = model.post(user)
            if oid:
                # send token by mail
                data["_id"] = oid
                send_token(data)
                ret = {"oid": oid, "action": 'mail_auth'}
            else:
                return prep_response('db error', 500)
        else:
            user["status"] = "active"
            oid = model.post(user)
            login(data["user_email"], data['password'])
            ret = {"oid": oid, "action": 'login'}
        return prep_response(ret)
    except Exception as e:
        logger.debug(e)
        return prep_response('invalid param', 400)


def existed_user(identify, password):
    """check existed user? and collect password?
        if invalid return False.
    :param {string} identify: required
    :param {string} password: required, hashed strings
    :return {object} user: user data
    """
    model = DOMAIN["users"]
    user = model.get_by_identify(identify)
    if user:
        if user['password'] == password_encryption(password):
            del user['password']
            return user

    return False


def login(identify, password):
    if identify and password:
        user = existed_user(identify, password)
        if user and user["status"] == 'active':
            user["_id"] = str(user["_id"])
            session['auth'] = user
            return user
    return False


def check_login():
    if "auth" in session:
        return session["auth"]
    else:
        return False


def authorized_user():
    return check_login()
