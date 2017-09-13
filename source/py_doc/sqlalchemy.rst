.. _sqlalchemy:


########################
sqlalchemy笔记
########################


.. contents:: 目录

--------------------------


Python ORM框架sqlalchemy学习笔记！


定义表
========

方式一
+++++++++

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

方式二
+++++++++++++

除开上面这种方式，还有另外一种方式定义表：

::

    from sqlalchemy import create_engine
    from sqlalchemy import Table, Column, Integer, Numeric, String, ForeignKey, DateTime
    from sqlalchemy import MetaData
    from sqlalchemy.exc import IntegrityError

    from datetime import datetime

    MYSQL_USER = "root"
    MYSQL_PASS = "httc123"
    MYSQL_HOST = "localhost"
    DB_NAME = "openstack_dashboard"

    #engine = create_engine("mysql://root:httc123@localhost/cloud_monitor", echo=True)
    DB_URL = "mysql://%s:%s@%s/%s"%(MYSQL_USER, MYSQL_PASS, MYSQL_HOST, DB_NAME)

    conn = None

    #engine = create_engine(DB_URL, echo=True)
    engine = create_engine(DB_URL)
    conn = engine.connect()

    metadata = MetaData()

    services = Table('services', metadata,
        Column('id', Integer(), primary_key=True),
        Column('name', String(30), nullable=True, unique=True),
        Column('description', String(30), nullable=True),
        Column('host', String(30), nullable=True),
        Column('status', String(30), nullable=True),
        Column('running_status', String(50), nullable=True),
        Column('updated_on', DateTime(), default=datetime.now, onupdate=datetime.now)
    )

    metadata.create_all(engine)

这种方式定义的表，可以采用下面的插入方式：

::

    ins = services.insert().values(
        id=1,
        name='glance-api',
        host='allinone-v2',
        status='unknown',
        updated_on=datetime.now()
    )
    conn.execute(ins)

    multi_data = [
        {
            'id': 2,
            'name': 'glance-registry',
            'host': 'allinone-v2',
            'status': 'unknown',
            'updated_on': datetime.now()
        },

        {
            'id': 3,
            'name': 'keystone-all',
            'host': 'allinone-v2',
            'status': 'unknown',
            'updated_on': datetime.now()
        },
    ]

    ins_multi = services.insert()
    conn.execute(ins_multi, multi_data)


查询和更新：

::

    ser_table = services
    update = ser_table.update
    s = ser_table.select()
    rs = conn.execute(s)

    row = rs.fetchall()

    for i in row:
        print (i['name'])

    s = update().where(ser_table.c.name == i).values(status='active', running_status='running')

    conn.execute(s)


插入
=====

下面的插入和查询操作，都是针对第一种创建表的方式！

::

    new_record = SystemLog(id='5', description=='Bob')
    # 添加到session:
    session.add(new_record)
    # 提交即保存到数据库:
    session.commit()
    # 关闭session:
    session.close()

查询
======

.. code-block:: python

    DBSession = sessionmaker(bind=engine)
    session = DBSession()

    session.query(SystemLog).one()
    session.query(SystemLog).all()

    # select * from cec_cmsystem_log limit 10, 30
    session.query(SystemLog).offset(10).limit(20)

    session.query(SystemLog).filter(SystemLog.id=='5').one()

    # 倒序查询，相当于查询数据库的倒手第25至倒手15条记录！
    session.query(SystemLog).order_by(SystemLog.id.desc()).offset(15).limit(10)

    # 查询数据最后十条记录
    session.query(SystemLog).order_by(SystemLog.id.desc()).limit(10)

    # 查询结果有多条记录，返回一条。
    session.query(BusinessIpMap).filter(SystemLog.id==id, SystemLog.time==time).first()



待以后陆续补充、更新和完善！
