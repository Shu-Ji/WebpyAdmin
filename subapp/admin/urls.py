# coding: utf-8


urls = (
    r'/assets/(.+?)', 'StaticFileHandler',
    r'(.+)/', 'Redirect',

    r'/?', 'Home',
    # 显示某个表的记录
    r'/table/([^/]+)', 'ViewTable',
    r'/table/([^/]+)/modify/(\d+)', 'ModifyRow',
    r'/table/([^/]+)/add', 'AddRow',
    r'/table/([^/]+)/delete/(\d+)', 'DeleteRow',
    r'/table/([^/]+)/search', 'Search',
)
