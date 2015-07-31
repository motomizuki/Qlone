# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

import re


class ValidationError(Exception):
    """
    バリデーションエラー用の例外クラス
    """

    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.msg = msg

    def get_message(self):
        return self.msg


class BaseValidator(object):
    """
    バリデータ用のベースクラス
    """

    def validate(self, value):
        return value


class RegexValidator(BaseValidator):
    """
    入力値が正規表現にマッチするかどうか調べるバリデータ
    """
    errors = (u'正しい値を入力してください。',)

    def __init__(self, pat):
        self.regex_pat = re.compile(pat)

    def validate(self, value):
        if value == "":
            return value

        if not self.regex_pat.search(value):
            raise ValidationError(self.errors[0])
        return value


class EmailValidator(RegexValidator):
    """
    メールアドレスとして正しい文字列かどうかを調べるバリデータ
    ＊簡易チェック
    """
    errors = (u'正しいメールアドレスを入力してください。',)

    def __init__(self):
        self.regex_pat = re.compile(
            r'([0-9a-zA-Z_&.+-]+!)*[0-9a-zA-Z_&.+-]+@'
            r'(([0-9a-zA-Z]([0-9a-zA-Z-]*[0-9a-z-A-Z])?\.)+'
            r'[a-zA-Z]{2,6}|([0-9]{1,3}\.){3}[0-9]{1,3})$'
        )



