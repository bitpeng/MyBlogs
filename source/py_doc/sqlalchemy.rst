.. _sqlalchemy:


########################
sqlalchemy笔记
########################


.. contents:: 目录

--------------------------


Python ORM框架sqlalchemy学习笔记！


定义表
========

.. code-block:: python

    from sqlalchemy import Column, String, create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy import Table, Column, Integer, Numeric, String, ForeignKey, DateTime

    import json
    from datetime import datetime

    MYSQL_USER = "root"
    MYSQL_PASS = "httc123"
    MYSQL_HOST = "localhost"
    DB_NAME = "cec_audit"

    # 使用utf-8编码，防止MySQL数据库中的中文字段出现乱码。
    DB_URL = "mysql://%s:%s@%s/%s?charset=utf8"%(MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DB_NAME)

    #engine = create_engine(DB_URL, echo=True)
    engine = create_engine(DB_URL)


    # 创建对象的基类:
    Base = declarative_base()

    class SystemLog(Base):
        # 表的名字:
        __tablename__ = 'cec_cmsystem_log'

        id = Column(String(20), primary_key=True)
        time = Column(DateTime)
        description = Column(String(200))

    Base.metadata.create_all(engine)


然后执行代码，如果cec_audit数据库中，不存在cec_cmsystem_log表，则会创建该表。

插入
=====


查询
======

::

    DBSession = sessionmaker(bind=engine)
    session = DBSession()


    session.query(SystemLog).one()
    session.query(SystemLog).all()

    # select * from cec_cmsystem_log limit 10, 30
    session.query(SystemLog).offset(10).limit(20)

