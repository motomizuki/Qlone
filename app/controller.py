# -*- coding: utf-8 -*-
__author__ = 'hmizumoto'

from . import app
from .views import auth, rest, api, view

# for auth api
app.register_blueprint(auth.module)

# for rest api
app.register_blueprint(rest.module)

# for other api
app.register_blueprint(api.module)

# for render template
app.register_blueprint(view.module)