#coding:utf-8

import web
from jinja2 import Environment, FileSystemLoader


class Admin(object):
    models = []
    db = None

    @classmethod
    def setup(cls, session, *Bases):
        '''加载admin应用的最初的初始化，传递所有的models'''
        # FIXME: 这里可能出现错误，需要使用其他方法得到base的所有model
        for Base in Bases:
            Base = Base.__dict__['_decl_class_registry']
            Base.pop('_sa_module_registry')
            cls.models.append(Base)
        cls.db = session
        return cls()

    @classmethod
    def getClassPathString(cls, class_):
        return '.'.join((class_.__module__, class_.__name__))

    def getAllModels(self, need_sep=True):
        '''返回所有的models'''
        for i, Base in enumerate(self.models):
            yield '|', Base.values()[0].__module__
            for name, model in Base.iteritems():
                if hasattr(model, '__admin_args__'):
                    name = model.__admin_args__.get('alias', name)
                href = '/admin/table/%s' % Admin.getClassPathString(model)
                nav_label = model.__name__
                if name != nav_label:
                    nav_label = '%s(%s)' % (nav_label, name)
                yield href, nav_label

    def getModelByTablename(self, clspath):
        '''根据表名返回相应的model类'''
        for Base in self.models:
            for model in Base.itervalues():
                if Admin.getClassPathString(model) == clspath:
                    return model

    def renderTable(self, model, order, page=0, limit=10):
        offset = page * limit
        db = self.db
        m = db.query(model).order_by(order).limit(limit).offset(offset).all()
        from faext import Grid
        g = Grid(model, m)
        exclude = Admin.handlePassword(model, g)
        g.configure(readonly=True, exclude=exclude)
        return g.render()

    @classmethod
    def handlePassword(cls, model, g):
        exclude = []
        if hasattr(model, '__admin_args__'):
            cols = model.__admin_args__.get('password', [])
            for col in cols:
                exclude.append(g[col].password().readonly())
        return exclude

    @classmethod
    def handleTextarea(cls, model, g):
        from sqlalchemy.types import Text
        options = []
        for col in Admin.getAllColumns(model):
            if type(Admin.getColumnType(col)) is Text:
                col = col.property.columns[0].name
                options.append(g[col].textarea())
        return options

    def renderOne(self, model, pk):
        from faext import FieldSet
        fs = FieldSet(Admin.getOneByPk(model, pk))
        options = Admin.handleTextarea(model, fs)
        exclude = Admin.handlePassword(model, fs)
        fs.configure(options=options, exclude=exclude)
        return fs.render()

    def modifyOne(self, model, pk, i):
        '''修改单页'''
        from faext import FieldSet
        fs = FieldSet(Admin.getOneByPk(model, pk), data=i)
        fs.configure(exclude=Admin.handlePassword(model, fs))
        if fs.validate():
            fs.sync()
            self.db.commit()
            return True

    def addOne(self, model, i):
        '''添加记录到数据库'''
        from faext import FieldSet
        fs = FieldSet(model, data=i)
        if fs.validate():
            fs.sync()
            self.db.add(fs.model)
            self.db.commit()
            return True

    def deleteOne(self, model, pk):
        cnt = Admin.db.query(model).filter(
            Admin.getPkColumn(model) == pk).delete()
        self.db.commit()
        return cnt

    def renderNew(self, model):
        '''渲染添加记录页面'''
        from faext import FieldSet
        fs = FieldSet(model)
        fs.configure(options=Admin.handleTextarea(model, fs))
        return fs.render()

    @classmethod
    def getOneByPk(cls, model, pk):
        return Admin.db.query(model).filter(
            Admin.getPkColumn(model) == pk).first()

    @classmethod
    def getPkColumn(cls, model):
        return getattr(model, model.__mapper__.primary_key[0].name)

    def getAllColumnsStr(self, model):
        for col in model.__table__.columns:
            col_name = str(col).split('.')[1]
            label = col.info.get('label', col_name)
            yield label, col_name

    def search(self, model, q, col):
        m = self.db.query(model).filter(getattr(model, col).contains(q)).all()
        if not m:
            return
        from faext import Grid
        g = Grid(model, m)
        exclude = Admin.handlePassword(model, g)
        g.configure(readonly=True, exclude=exclude)
        return g.render()

    @classmethod
    def getAllColumns(cls, model):
        return [getattr(model, str(i).split('.')[1]) for i in model.__table__.columns]

    @classmethod
    def getColumnType(cls, c):
        return c.property.columns[0].type


class Render:
    def __init__(self, path, **k):
        self.env = Environment(loader=FileSystemLoader(path), **k)

    def __getattr__(self, name):
        '''在render之前自动添加web.header为html

        >>> render = Render()
        >>> render.myhome(name='hello')  # 这个将加载template/myhome.html
        '''

        web.header("Content-Type", "text/html")
        return self.env.get_template('%s.html' % name).render


def static(path):
    '''jinja2模板函数，添加后缀使浏览器决定静态文件是否读取缓存'''
    import os
    import settings
    import hashlib
    filename = os.path.join(settings.STATIC_DIR, path)
    v = hashlib.md5(file(filename).read()).hexdigest()
    return '/admin/assets/%s?v=%s' % (path, v)


class StaticFileHandler:
    '''静态文件改变了就重新加载，否则读取缓存'''
    def GET(self, path):
        import mimetypes
        import stat
        import hashlib
        import os
        import settings
        import datetime
        abspath = os.path.join(settings.STATIC_DIR, path)
        stat_result = os.stat(abspath)
        modified = datetime.datetime.fromtimestamp(stat_result[stat.ST_MTIME])
        web.header(
            "Last-Modified", modified.strftime('%a, %d %b %Y %H:%M:%S GMT'))

        mime_type, encoding = mimetypes.guess_type(abspath)
        if mime_type:
            web.header("Content-Type", mime_type)

        # 缓存1年
        cache_time = 86400 * 365 * 1
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
            if settings.GZIP_STATIC_FILE:
                data = gzipData(data)
            return data


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
