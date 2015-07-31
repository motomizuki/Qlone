# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
from functools import wraps
from flask import redirect
from app.views.auth import check_login
from app.utils import prep_response
from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if check_login():
            return f(*args, **kwargs)
        return redirect("/")
    return decorated_function


def authorize_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if check_login():
            return f(*args, **kwargs)
        return prep_response({'message': 'This API requires authorization'}, 404)
    return decorated_function
