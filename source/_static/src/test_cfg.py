#! /usr/bin/env python
# coding:utf-8
import sys
from oslo.config import cfg
from oslo.config import types

PortType = types.Integer(1, 65535)

disk_list = ['hda 100G', 'hdb 150G', 'hdc 200G']
disk_opts= [
    cfg.MultiStrOpt('volume', default=disk_list, help='disk volumes in GB'),
    cfg.StrOpt('type', default='ssd', help='disk type!'),
]

cli_opts = [
    cfg.StrOpt('host',
            default='119.119.119.119',
            help='IP address to listen on.'),
    cfg.Opt('port',
            type=PortType,
            default=9292,
            help='Port number to listen on.')
]

# oslo.config 默认维护了一个 ConfigOpts 类型的全局变量 CONF。
# 注册参数，以及后续获取参数，都是可以通过 CONF。
CONF = cfg.CONF
# t_opts不是命令行参数，所以假如要覆盖默认值，只能通过配置文件改变！
# 注册的选项必须是可迭代的！否则会发生错误
#CONF.register_opts(disk_opts)
#CONF.register_cli_opts(cli_opts)

CONF.register_opts(disk_opts, 'disk')
CONF.register_cli_opts(cli_opts, 'cli')


if __name__ == '__main__':
    CONF(sys.argv[1:])

    #print "volume:", CONF.volume
    #print "cli_host:", CONF.host
    #print "cli_port:", CONF.port
    print "volume:", CONF.disk.volume
    print "cli_host:", CONF.cli.host
    print "cli_port:", CONF.cli.port
