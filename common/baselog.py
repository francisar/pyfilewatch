#!/usr/bin/python
# -*- coding:utf-8 -*-
import logging
from logging.handlers import TimedRotatingFileHandler
from function import switch
import sys
import os
import stat


class BaseLog(object):

    _level = {
                'CRITICAL': logging.CRITICAL,
                'DEBUG': logging.DEBUG,
                'ERROR': logging.ERROR,
                'FATAL': logging.FATAL,
                'WARNING': logging.WARNING,
                'WARN': logging.WARN,
                'INFO': logging.INFO,
                'NOTSET': logging.NOTSET
        }

    def __init__(self,log_level,log_path,log_file,log_when,log_backupCount,log_rotating_interval,name=__name__):
        log_format = '%(asctime)s %(levelname)s %(message)s'
        self._logger = logging.getLogger(name)
        self._logger.setLevel(self._level[log_level.upper()])
        self._logdir = log_path
        self._logbase = self._logdir + log_file
        self._create_file()
        self._mod_authority()
        for h in self._logger.handlers:
            self._logger.removeHandler(h)
        handler = TimedRotatingFileHandler(filename=self._logbase, when=log_when, interval=eval(log_rotating_interval), backupCount=eval(log_backupCount))
        handler.setLevel(self._level[log_level.upper()])
        formatter = logging.Formatter(log_format)
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def _create_file(self):
        '''Create file for logging.'''
        try:
            if os.path.isdir(self._logdir) is False:
                os.makedirs(self._logdir)
            if os.path.exists(self._logbase) is False:
                open(self._logbase, 'w').close()
        except (OSError, IOError, Exception),msg:
            sys.stderr.write('_LogConfig:%s'%msg)
            sys.exit(-1)

    def _mod_authority(self):
        '''Modify file authority'''
        try:
            os.chmod(self._logdir, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
            os.chmod(self._logbase, stat.S_IRWXU|stat.S_IRWXG|stat.S_IRWXO)
        except Exception,msg:
            sys.stderr.write('User does not have '\
            'modify permissions, msg:%s\n'%msg)

    def writelog(self,log_level,message):
        for case in switch(log_level.strip().lower()):
            if case('warn'):
                self.warn(message)
                break
            if case('info'):
                self.info(message)
                break
            if case('error'):
                self.error(message)
                break
            if case('debug'):
                self.debug(message)
                break
            if case():
                break

    def info(self, message):
        self._logger.info(message)

    def warn(self, message):
        self._logger.warn(message)

    def error(self, message):
        self._logger.error(message)

    def debug(self, message):
        self._logger.debug(message)