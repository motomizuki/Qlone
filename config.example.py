# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
import os
# for application
SECRET_KEY = "fugafuga"
SESSION_KEY = "hogehoge"
HOST = "127.0.0.1"  # Qloneが起動するホスト名
PORT = 8888  # Qloneが起動するポート番号
DEBUG = False  #デバックモードか否か
# Qloneのルート
# http://host:port/hoge/ Qloneで起動したい場合
# APPLICATION_ROOT = "/hoge"
APPLICATION_ROOT = ""

# for mongodb
MONGO_HOST = "127.0.0.1"
MONGO_DBNAME = "qlone"


# for mail
MAIL_AUTH = True  # メール認証をするか
# アカウント作成を許可するメールのドメイン
# @example.comのみを許可する場合は
# ALLOW_DOMAIN = ["example.com"]
ALLOW_DOMAIN = []
# メール認証をする場合の送信サーバの設定
# gmailの二段階認証を利用している場合は，
# MAIL_PASSWORDにはアプリパスワードを設定する
MAIL_SERVER = 'smtp.gmail.com'
MAIL_PORT = 587
MAIL_USERNAME = "user@example.com"
MAIL_PASSWORD = "password"

# for upload images
APP_ROOT = os.path.dirname(os.path.abspath(__file__)) + "/app"
UPLOAD_FOLDER = APP_ROOT + '/uploads/'