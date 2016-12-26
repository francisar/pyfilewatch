#!/usr/bin/python
# -*- coding:utf-8 -*-
from function import Config
import os


config_file = "%s/../config.ini" % os.path.split(os.path.realpath(__file__))[0]
cf = Config(config_file)

LOG_PATH = cf.get('logging','log_path')
LOG_LEVEL = cf.get('logging','log_level')
LOG_FILE = cf.get('logging','log_file')
LOG_WHEN = cf.get('logging','log_when')
LOG_BACKUPCOUNT = cf.get('logging','log_backupCount')
LOG_ROTATING_INTERVAL = cf.get('logging','log_rotating_interval')


PIDFILE = cf.get('daemon','pid')

channel_MODULE = cf.get('daemon','channel').split(',')



MODULES = {}
for module in channel_MODULE:
    filename = cf.get(module,'filename')
    brokerlist = cf.get(module,'brokerlist')
    topic = cf.get(module,'topic')
    queuelen =  eval(cf.get(module,'queuelen'))
    temp = {"filename":filename,"topic":topic,"brokerlist":brokerlist,"queuelen":queuelen}
    MODULES[module] = temp