#!/usr/bin/python
#coding:utf-8

import web

import settings
import urls
import utils
import controler as ctrl


render = settings.render
outer = settings.outer
db = outer.db
admin = outer.admin


class Redirect:
    def GET(self, path):
        raise web.seeother(path)


class Home:
    def GET(self):
        return render.home()


class ViewTable:
    def GET(self, clspath):
        i = web.input()
        page = int(i.get('page', 0))
        order = i.get('order', None)
        limit = int(i.get('limit', 10))
        model = admin.getModelByTablename(clspath)
        if model is None:
            raise web.notfound()
        return render.table(
            table=admin.renderTable(model, order, page, limit),
            cols=admin.getAllColumnsStr(model),
            is_ajax=order is not None)

    def POST(self, clspath):
        from formalchemy import Field
        model = admin.getModelByTablename(clspath)
        fs = Field(model, data=web.input())
        fs.sync()
        db.commit()
        print web.input()
        print fs.validate()
        if fs.validate():
            fs.sync()
            db.commit()


class ModifyRow:
    def GET(self, clspath, pk):
        model = admin.getModelByTablename(clspath)
        return render.modify(row=admin.renderOne(model, pk))

    def POST(self, clspath, pk):
        model = admin.getModelByTablename(clspath)
        return ctrl.json(suc=admin.modifyOne(model, pk, web.input()))


class AddRow:
    def GET(self, clspath):
        model = admin.getModelByTablename(clspath)
        return render.add(row=admin.renderNew(model))

    def POST(self, clspath):
        model = admin.getModelByTablename(clspath)
        return ctrl.json(suc=admin.addOne(model, web.input()))


class DeleteRow:
    def POST(self, clspath, pk):
        model = admin.getModelByTablename(clspath)
        return ctrl.json(suc=admin.deleteOne(model, pk))


class Search:
    def POST(self, clspath):
        i = web.input()
        model = admin.getModelByTablename(clspath)
        return ctrl.json(suc=admin.search(model, i.q.strip(), i.col))


class StaticFileHandler(utils.StaticFileHandler):
    pass


render.env.globals.update({
    'BRAND': settings.BRAND,

    'static': utils.static,
    '_': lambda x: x,
    'pathInfo': lambda: web.ctx.env['PATH_INFO'],
    'nav_models': list(admin.getAllModels(need_sep=True)),
})


app = web.application(urls.urls, globals())
