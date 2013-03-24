#coding:utf-8

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, DateTime, func, Text

from formalchemy import Column


Base = declarative_base()


class User(Base):
    __tablename__ = 'todo_user'
    __admin_args__ = {
        'alias': u'用户表'
    }

    id = Column(Integer, primary_key=True)
    uid = Column(Integer)
    todo = Column(Text, nullable=False, label=u'内容')
    dt = Column(DateTime, default=func.now(), label=u'日期')


def initDb():
    '''初始化数据库'''
    import settings
    # 创建各个表
    metadata = Base.metadata
    metadata.create_all(settings.engine)
    db = settings.db
    for i in range(1, 32):
        pass
        #db.merge(User(uid=i, todo=u'这个是todo%s' % (2 * i + i)))


if __name__ == '__main__':
    initDb()
