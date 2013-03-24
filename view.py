#!/usr/bin/python
#coding:utf-8

import web

import settings
import models
from subapp.admin import settings as adminsettings
from subapp.todo import models as todomodels
adminsettings.setup(settings.db, models.Base, todomodels.Base)
# urls必须在setup之后引入
import urls


class Home:
    def GET(self):
        web.header("Content-Type", "text/html")
        return u'<a href="/admin">访问admin页面</a>'


app = web.application(urls.urls, globals())
application = app.wsgifunc()


if __name__ == '__main__':
    app.run()
