Qlone
===============
Qiitaをオンプレで使いたい人のためのクローン

# インストール
## python3を用意
[pyenv](https://github.com/yyuu/pyenv)を使うといいと思います．
```bash
$ git clone https://github.com/yyuu/pyenv.git ~/.pyenv
$ echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
$ echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
$ echo 'eval "$(pyenv init -)"' >> ~/.bash_profile
$ pyenv install 3.4.x
```
## mongodbを用意
[Install MongoDB](http://docs.mongodb.org/manual/installation/)を参照してください．
## Qloneのセットアップ
```
$ git clone 
```
## 依存ライブラリのインストール

```bash
$ cd qlone
$ pip install -r requirements.txt
```

ライブラリのインストールに失敗する場合は

```bash
$ pip install -U pip 
```

をするとうまくいくかも

## Qloneの設定
`config.example.py`を`config.py`にリネームして，  
各設定値をそれぞれ自分の環境に合わせてください.

```py
# for application
SECRET_KEY = "fugafuga"
SESSION_KEY = "hogehoge"
HOST = "127.0.0.1"  # Qloneが起動するホスト名
PORT = 8888  # Qloneが起動するポート番号
# Qloneのルート
# http://host:port/hoge/ のアドレスでQloneを起動したい場合
# APPLICATION_ROOT = "/hoge"
APPLICATION_ROOT = ""

# for mongodb
MONGO_HOST = "127.0.0.1"
MONGO_DBNAME = "qlone"
DEBUG = True

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
```
## Qloneの起動
ライブラリのインストール，設定に問題なければ

```
$ python manage.py runserver
```

を実行すると`config.py`で設定した`http://HOST:PORT/APPLICATION_ROOT/`でQloneにアクセスできるはずです．

# システム構成
## フロントエンド
- HTML5
- jquery
- knockout.js
- Bootstrap
  - Flat UI

## バックエンド
- DB: MongoDB
- Lang: Python3
- Framework: Flask
- Dependent libraries: requirements.txt 参照

#schema
## users
ユーザアカウントのスキーマ
記事数に対してユーザ数はたかだか数百なので，
基本的にはユーザに情報を持たせる．

```jsonschema
{
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'schema for users collection',
    'type': 'object',
    'properties': {
        '_id': { 'type': 'ObjectId' }
        'user_name': { 'type': 'string' },
        'user_email': {
            'type': 'string',
            'format': 'email'
        },
        'profile': {
            'type': 'object',
            'properties':{
                'first_name': {'type':'string'},
                'last_name': {'type':'string'},
                'organization': {'type':'string'},
                'description': {'type':'string'},
            }
        },
        'password': { 'type': 'string' },
        'following_tags': {
            'type': 'array'
            'items': { 'type': 'string' },
            'uniqueItems': True
        },
        'following_users': {
            'type': 'array'.
            'items': { 'type': 'ObjectId' },
            'uniqueItems': True
        },
        'status':{
            'type': 'string',
        },
        'created':{
            'type': 'string',
            'format': 'datetime',
        },
        'modified':{
            'type': 'string',
            'format': 'datetime',
        }
    }
}
```

## items
記事のスキーマ

```jsonschema
{
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'schema for users collection',
    'type': 'object',
    'properties': {
        '_id': { 'type': 'ObjectId' },
        'user_id': {'type': 'string'},
        'user_name': {'type': 'string'},
        'title': { 'type': 'string' },
        'markdown': { 'type': 'string' },
        'publish_html': { 'type': 'string' },
        'publish_toc': { 'type': 'string' },
        'tags': {
            'type': 'array'
            'items': { 'type': 'string' },
            'uniqueItems': True
        },
        'status':{
            'type': 'string',
        },
        'collaborate': {
            'type': 'boolean',
            'description': 'Allowed collaborative editing or not',
        },
        'created':{
            'type': 'string',
            'format': 'datetime',
        },
        'modified':{
            'type': 'string',
            'format': 'datetime',
        }
    }
}
```

## comments
コメントのスキーマ
コメントもMarkdownで記述可能にするために別collectionに
(現在はマークダウンで記述可能じゃないです)
```
{
    '$schema': 'http://json-schema.org/draft-04/schema#',
    'description': 'schema for comments collection',
    'type': 'object',
    'properties': {
        '_id': { 'type': 'ObjectId' },
        'user_id': { 'type': 'string'},
        'user_name': { 'type': 'string'},
        'item_id': { 'type': 'string' },
        'markdown': { 'type': 'string' },
        'html': { 'type': 'string' },
        'created': {
            'type': 'string',
            'format': 'datetime'
        },
        'modified': {
            'type': 'string',
            'format': 'datetime'
        }
    }
}
```