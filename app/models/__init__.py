# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'
from .base import BaseModel
from .users import UsersModel
from .items import ItemsModel
DOMAIN = {
    # 'collection_name': model
    'users': UsersModel(),
    'items': ItemsModel(),
    'comments': BaseModel('comments')
}
