from oslo.config import cfg

CONF = cfg.CONF
#CONF.import_opt('volume', 'test_cfg', group='disk')
CONF.import_opt('host', 'test_cfg', group='cli')

print "disk volume: ", CONF.disk.volume
print "disk type: ", CONF.disk.type
print "cli host: ", CONF.cli.host