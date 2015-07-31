# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
from flask import make_response, jsonify
import json
from bson import ObjectId
import mistune
from app.lib.toc import TocRenderer
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import pytz
import hashlib
import jwt
import itertools
import os
from werkzeug.utils import secure_filename
import operator
from . import app
from . import validate

from logging import getLogger, StreamHandler, DEBUG
logger = getLogger(__name__)
handler = StreamHandler()
handler.setLevel(DEBUG)
logger.setLevel(DEBUG)
logger.addHandler(handler)

def date_to_str(date):
    return datetime.strftime(date, "%Y-%m-%d")


def prep_response(obj, status_code=200):
    body = {'status': status_code}
    if status_code < 400:
        body["data"] = obj
    else:
        body["message"] = obj
    response = jsonify(body)
    response.status_code = status_code
    response.mimetype = 'application/json'
    return response


def oid_to_str(obj):
    try:
        if isinstance(obj, list):
            for _ in obj:
                _["_id"] = str(_["_id"])
        elif isinstance(obj, dict):
            obj["_id"] = str(obj["_id"])
        elif isinstance(obj, ObjectId):
            obj = str(obj)
        return obj
    except Exception as e:
        return obj


def password_encryption(password):
    return hashlib.sha1(password.encode()).hexdigest()


def _cvt_func(value, typ):
    if typ == "str":
        return str(value)
    elif typ == "int":
        return int(value)
    elif typ == "float":
        return float(value)
    elif typ == "bool":
        return bool(value)
    elif typ == "date":
        return pytz.utc.localize(datetime.strptime(value, "%Y-%m-%d"))
    elif typ == "email":
        v = validate.EmailValidator()
        return v.validate(value)
    elif typ == "password":
        return password_encryption(value)
    else:
        raise TypeError("unkown type {0}".format(typ))


def parse_form(frm_data):
    dat = json.loads(frm_data)
    it = itertools.groupby(dat, operator.itemgetter("name"))
    ret = {}
    for key, items in it:
        splt = key.split(":")
        if len(splt) == 1:
            name = splt[0]
            typ = "str"
        else:
            name = splt[0]
            typ = splt[1]
        try:
            data = [_cvt_func(item["value"], typ) for item in items]
            if len(data) == 1:
                data = data[0]
        except Exception as e:
            raise ValueError("cannot parse {0}".format(key))

        ret[name] = data

    return ret


def parse_data(frm_data):
    dat = json.loads(frm_data)
    ret = {}
    for key, items in dat.items():
        splt = key.split(":")
        if len(splt) == 1:
            name = splt[0]
            typ = "str"
        else:
            name = splt[0]
            typ = splt[1]
        try:
            if isinstance(items, str):
                data = _cvt_func(items, typ)
            else:
                data = items

        except Exception as e:
            raise ValueError("cannot parse {0}".format(key))

        ret[name] = data

    return ret


def parse_request(frm_data):
    if "form" in frm_data:
        return parse_form(frm_data["form"])
    elif "data" in frm_data:
        return parse_data(frm_data["data"])

    raise LookupError("invalid request")


def jwt_encode(data):
    encoded = jwt.encode(data, app.config["SECRET_KEY"], algorithm='HS256').decode()
    return encoded


def jwt_decode(token):
    decoded = jwt.decode(token.encode(), app.config["SECRET_KEY"], algorithms=['HS256'])
    return decoded


def mail(to, title, body):
    sender = app.config["MAIL_USERNAME"]
    passwd = app.config["MAIL_PASSWORD"]

    msg = MIMEText(body)
    msg['Subject'] = title
    msg['From'] = sender
    msg['To'] = to

    # Send the message via our own SMTP server.
    s = smtplib.SMTP(app.config["MAIL_SERVER"], app.config["MAIL_PORT"])
    s.ehlo()
    s.starttls()
    s.ehlo()
    s.login(sender, passwd)
    s.send_message(msg)
    s.close()


def send_token(data):
    token = jwt_encode(data)
    url = "http://" + app.config["DOMAIN"] + app.config["APPLICATION_ROOT"] + "/session/activate?token=" + token
    body = "Qiita:Cloneへようこそ！\nURLをクリックしてアカウントを認証してください。\n" + url
    logger.debug(data["user_email"])
    mail(data["user_email"], "Qiita:Clone アカウント作成", body)


def render_md(text):
    try:
        tocr = TocRenderer()
        md = mistune.Markdown(renderer=tocr)
        tocr.reset_toc()  # initial the status
        html = md.parse(text)  # parse for headers
        toc = tocr.render_toc(level=3)  # render TOC HTML
    except:
        # if html has no "h tags"
        toc = ''

    return html, toc


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ['jpg', 'jpeg', 'png', 'gif']


def img_upload(uploaded_files):
    filenames = []
    try:
        for file in uploaded_files:
            # Check if the file is one of the allowed types/extensions
            if file and allowed_file(file.filename):
                # File name is hashed for uploading same name images
                hashed_name = hashlib.sha224((file.filename+datetime.now().ctime()).encode()).hexdigest()
                logger.debug(hashed_name)
                filename = secure_filename(hashed_name)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                filenames.append(filename)
    except Exception as e:
        logger.debug(str(e))
    return filenames
