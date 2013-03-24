WebpyAdmin
==========

Admin interface for web.py with formalchemy + sqlalchemy + jinja2 + bootstrap + jQuery

为你的web.py应用添加一个简单的Admin页面。

依赖关系
---------------
    
* Jinja2
* Sqlalchemy
* Web.py
* Formalchemy[注意本程序包中的formalchemy已经被改动过以适应本程序]
* jQuery 2.0 beta
* Twitter Bootstrap 2.3
* 仅通过Chrome浏览器测试，不支持其他浏览器

结构说明
---------------

1. subapp/admin中为所有的admin页面代码；
2. subapp/todo为测试用的一个子应用（demo）；
3. formalchemy为修改后的formalchemy包；
4. 根目录目录下的其他所有文件均为样例程序（demo）所需的；
5. start_server.py为启动调试用服务器脚本（$ python start_server.py）；
6. index_wsgi.py为兼容apache等程序的脚本；
7. view.py为demo的main app文件（web.py应用的入口）；
8. urls.py, settings.py类似Django中的相关文件；
9. mysite.db为demo所用的sqlite数据库文件；

使用说明
---------------

将本程序所带的formalchemy包含在sys.path中，参照views.py顶部的几行配置，即：

```python
import settings  # 需要引入sqlalchemy的session（这里用db表示）
import models  # 这个是你的models文件，需要把他的Base传递进去
from admin import settings as adminsettings
adminsettings.setup(settings.db, models.Base)  # 如果你还有子应用则在这后面依次加入
# urls必须在setup之后引入
import urls  # 假设这是你的urlconf文件
```

在你的urlconf中添加一条:

```python
import admin.views
url += (r'/admin', admin.views.app)
```

好了，访问<http://localhost:8080/admin>即可。

预览
---------------

首页

![](https://raw.github.com/Shu-Ji/WebpyAdmin/master/doc/home.png)

单页

![](https://raw.github.com/Shu-Ji/WebpyAdmin/master/doc/view.png)

添加

![](https://raw.github.com/Shu-Ji/WebpyAdmin/master/doc/add.png)

删除

![](https://raw.github.com/Shu-Ji/WebpyAdmin/master/doc/del.png)

修改

![](https://raw.github.com/Shu-Ji/WebpyAdmin/master/doc/mod.png)

进展
---------------

`2013-03-24`

* 通过简单的配置和一个setup函数驱动这个简单的Admin页面
* 响应式设计
* 自动加载所有传递到setup中的model并渲染
* 能查看|修改|添加|删除|搜索某个表中的数据
* 密码字段（需要在你的model中指定__admin_args__['password'来告诉WebpyAdmin）默认不加载
* 暂无分页【有搜索功能应该不需要分页功能吧？】
* 暂不支持外键
* 暂不支持join自动联表查询
* 暂无授权登录机制

`TODO`

* 搜索页面应该去除密码搜索字段
* 搜索时应该排除搜索密码字段，（用户绕过js使用其他程序提交的）数据在搜索时没有检查
* 分页？
* 自动join指定的字段(支持多级join)
* 登录授权机制
