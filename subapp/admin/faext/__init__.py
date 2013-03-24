#!/usr/bin/env python
#coding:utf-8


from formalchemy import FieldSet as BaseFieldSet
from formalchemy import Field as BaseField
from formalchemy import Grid as BaseGrid
from formalchemy.templates import TemplateEngine as BaseTemplateEngine


class Jinja2Engine(BaseTemplateEngine):
    def __init__(self, **kw):
        import os.path as osp
        from jinja2 import Environment, FileSystemLoader
        faext_dir = osp.dirname(osp.realpath(__file__))
        tmp_dir = osp.join(faext_dir, 'templates')
        self._lookup = Environment(
            loader=FileSystemLoader(tmp_dir),
            trim_blocks=True,
            line_comment_prefix='^^',
            line_statement_prefix='^')

        self._lookup.globals.update({
            'dir': dir,
        })
        BaseTemplateEngine.__init__(self, **kw)

    def get_template(self, name):
        return self._lookup.get_template('%s.html' % name)

    def render(self, template_name, **kw):
        return self.templates.get(template_name).render(**kw)


class Grid(BaseGrid):
    engine = Jinja2Engine()


class Field(BaseField):
    engine = Jinja2Engine()


class FieldSet(BaseFieldSet):
    engine = Jinja2Engine()
