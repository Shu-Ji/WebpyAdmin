#coding:utf-8

import os

import web

import utils


DEBUG = True
BRAND = 'WebpyAdmin'


# 静态文件设置
APP_ROOT = os.path.dirname(__file__)
STATIC_DIR = os.path.join(APP_ROOT, 'static')
TEMPLATE_DIR = os.path.join(APP_ROOT, 'templates')


# 是否启用gzip压缩静态文件
GZIP_STATIC_FILE = True


# jinja2模板设置
render = utils.Render(
    TEMPLATE_DIR,
    trim_blocks=True,
    line_comment_prefix='^^',
    line_statement_prefix='^')


def setup(session, *Bases):
    '''初始化session'''
    outer.db = session
    outer.admin = utils.Admin.setup(session, *Bases)


outer = web.storage()
