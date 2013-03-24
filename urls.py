# coding: utf-8


import subapp.admin.views as adminviews
import subapp.todo.views as todoviews


urls = (
    r'/', 'Home',

    r'/admin', adminviews.app,
    r'/todo', todoviews.app,
)
