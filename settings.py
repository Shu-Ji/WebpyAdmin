#coding:utf-8

import os

import web

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session


# 调试是否开启
DEBUG = True
web.config.debug = DEBUG


APP_ROOT = os.path.dirname(__file__)


# sqlalchemy 设置
engine = create_engine(
    'sqlite:///%s/mysite.db' % APP_ROOT,
    encoding='utf8',
    echo=False,
)
db = scoped_session(sessionmaker(bind=engine))
