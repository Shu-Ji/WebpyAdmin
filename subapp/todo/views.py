#!/usr/bin/python
#coding:utf-8

import web

import urls


class Home:
    def GET(self):
        web.header("Content-Type", "text/html")
        return u'TODO HOME. <a href="/admin">访问admin页面</a>'


app = web.application(urls.urls, globals())
