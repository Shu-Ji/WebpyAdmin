#coding:utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String

from formalchemy import Column


Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    __admin_args__ = {
        'alias': u'用户表',  # 定义此表在页面上显示时的中文名
        'password': ['pwd']  # 告诉admin哪些字段是密码字段
    }

    id = Column(Integer, primary_key=True)
    name = Column(String(20), unique=True, nullable=False, label=u'用户名')
    email = Column(String(30), unique=True, nullable=False, label=u'邮箱')
    pwd = Column(String(32), label=u'密码')


class Order(Base):
    __tablename__ = 'order'

    oid = Column(Integer, primary_key=True, label=u'订单编号')
    uid = Column(Integer, label=u'谁的订单')
    amount = Column(Integer, nullable=False, label=u'订单金额')


class Like(Base):
    __tablename__ = 'like'
    __admin_args__ = {
        'alias': u'喜欢表',
    }

    lid = Column(Integer, primary_key=True)
    uid = Column(Integer, label=u'谁喜欢')
    uid2 = Column(Integer, label=u'被喜欢')


def initDb():
    '''初始化数据库'''
    import settings
    # 创建各个表
    metadata = Base.metadata
    metadata.create_all(settings.engine)

    db = settings.db
    for i in range(1, 10):
        pass
        #db.merge(Like(uid=i * 2, uid2=i * 3 + 1))

    from subapp.todo import models
    models.initDb()
    db.commit()


if __name__ == '__main__':
    initDb()
