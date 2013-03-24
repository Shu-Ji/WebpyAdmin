#!/usr/env/bin python
#coding:utf-8

import sys
import web
import view


app = view.app
application = app.wsgifunc()
web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)

if __name__ == '__main__':
    app.run()