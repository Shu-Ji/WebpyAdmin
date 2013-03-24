#!/usr/bin/env python
#coding:utf-8

# 此模块主要用于操作数据库
import datetime
import re
import os
import logging

import web

import settings
import utils


db = settings.outer.db


def static(path):
    '''jinja2模板函数，添加后缀使浏览器决定静态文件是否读取缓存'''
    filename = os.path.join(settings.STATIC_DIR, path)
    v = utils.md5(file(filename).read())[:10]
    return '/assets/%s?v=%s' % (path, v)


def loadSqla(handler):
    '''webpy的sqlalchemy钩子'''
    try:
        result = handler()
        if not web.config.get('is_ajax'):
            # gzip压缩html, js, css
            result = gzipData(result)
        elif settings.DEBUG and result:
            # 是Ajax请求的，那么在Debug模式下输出返回结果方便调试
            logging.warning(result)
        return result
    except web.HTTPError:
        db.commit()
        raise
    except Exception:
        db.rollback()
    finally:
        try:
            db.commit()
        except Exception, e:
            logging.error(e)
        db.close()


def printquery(statement, bind=None):
    '''用于输出sqlalchemy产生的sql语句'''
    import sqlalchemy.orm
    if isinstance(statement, sqlalchemy.orm.Query):
        if bind is None:
            bind = statement.session.get_bind(statement._mapper_zero_or_none())
        statement = statement.statement
    elif bind is None:
        bind = statement.bind

    dialect = bind.dialect
    compiler = statement._compiler(dialect)

    class LiteralCompiler(compiler.__class__):
        def visit_bindparam(
                self, bindparam, within_columns_clause=False,
                literal_binds=False, **kwargs):
            return super(LiteralCompiler, self).render_literal_bindparam(
                bindparam, within_columns_clause=within_columns_clause,
                literal_binds=literal_binds, **kwargs)

    compiler = LiteralCompiler(dialect, statement)
    print '\n', '_' * 20, datetime.datetime.now(), '_' * 20
    print compiler.process(statement)
    print


def json(**kwargs):
    '''(dict) -> jsonstring

    设置Content-Type为json. 并返回相应的json串.
    >>> name, pwd = 'Mr. Tian', '123456'
    >>> json(username=name, password=pwd)
    '{"username": "Mr. Tian", "password": "123456"}'
    '''

    import json as jsonpy
    web.header("Content-Type", "application/json")
    # 不要进行gzip压缩
    web.config.is_ajax = True
    return jsonpy.dumps(kwargs)


def gzipData(data):
    '''gzip压缩'''
    import gzip
    import cStringIO
    accepts = web.ctx.env.get('HTTP_ACCEPT_ENCODING', '')
    if accepts.find('gzip') != -1:
        zbuf = cStringIO.StringIO()
        zfile = gzip.GzipFile(mode='wb', fileobj=zbuf, compresslevel=9)
        # render产生的html内容是unicode的
        if isinstance(data, unicode):
            data = data.encode('u8')
        zfile.write(data)
        zfile.close()
        gzip_data = zbuf.getvalue()
        # 原来的长度
        old_length = len(data)
        # 压缩的的长度[有可能压缩后变大]
        new_length = len(gzip_data)
        if new_length < old_length:
            web.header('Content-Encoding', 'gzip')
            web.header('Content-Length', str(new_length))
            web.header('Vary', 'Accept-Encoding', unique=True)
            data = gzip_data
    return data


class StaticFileHandler:
    '''静态文件改变了就重新加载，否则读取缓存'''
    def GET(self, path):
        import mimetypes
        import stat
        import hashlib
        abspath = os.path.join(settings.STATIC_DIR, path)
        stat_result = os.stat(abspath)
        modified = datetime.datetime.fromtimestamp(stat_result[stat.ST_MTIME])
        web.header(
            "Last-Modified", modified.strftime('%a, %d %b %Y %H:%M:%S GMT'))

        mime_type, encoding = mimetypes.guess_type(abspath)
        if mime_type:
            web.header("Content-Type", mime_type)

        # 缓存10年
        cache_time = 86400 * 365 * 10
        web.header("Expires", datetime.datetime.now() +
                   datetime.timedelta(seconds=cache_time))
        web.header("Cache-Control", "max-age=%s" % cache_time)

        ims_value = web.ctx.env.get("HTTP_IF_MODIFIED_SINCE")
        if ims_value is not None:
            # ie的ims值不标准，所以导致不能正常产生缓存，这里解决
            # IE的是Sat, 02 Feb 2013 14:44:34 GMT; length=4285
            # 标准的为Sat, 02 Feb 2013 14:44:34 GMT
            stupid = ims_value.find(';')
            if stupid != -1:
                ims_value = ims_value[:stupid]

            since = datetime.datetime.strptime(
                ims_value, '%a, %d %b %Y %H:%M:%S %Z')
            if since >= modified:
                # 如果是调试模式，那么强制加载所有非第三方js文件
                if not (settings.DEBUG and
                        abspath.endswith('.js') and '3rd' not in abspath):
                    raise web.notmodified()

        with open(abspath, "rb") as f:
            data = f.read()
            hasher = hashlib.sha1()
            hasher.update(data)
            web.header("Etag", '"%s"' % hasher.hexdigest())
            # 合并js文件[第三方库不压缩]
            if abspath.endswith('.js') and not '3rd' in abspath:
                libs = re.findall(r'(.*?@import "([^"]+\.js)".*?)', data)
                for line, lib in libs:
                    lib = os.path.join(settings.STATIC_DIR, lib)
                    data = data.replace(line, file(lib).read())

                # mangle: 局部变量压缩
                # mangle_toplevel: 整个文件压缩[即函数名也压缩]
                #data = slimit.minify(data, mangle=True)
                if not settings.DEBUG:
                    import slimit
                    data = slimit.minify(
                        data, mangle=True, mangle_toplevel=True)
            return data
