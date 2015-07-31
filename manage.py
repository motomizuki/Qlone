# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

from flask.ext.script import Manager, Server
from app.controller import app

manage = Manager(app)
manage.add_command('runserver',
                   Server(
                       host=app.config['HOST'],
                       port=app.config['PORT']
                   ))

if __name__ == "__main__":
    manage.run()