from pyinotify import WatchManager, Notifier, ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY
import sys
import traceback
from threading import Thread
from common.baselog import BaseLog
from Queue import Queue


class EventHandler(ProcessEvent):

    def __init__(self,filepath,outqueue,logger,threadname):
        super(EventHandler, self).__init__()
        self._logger = logger
        self._outqueue = outqueue
        self._threadname = threadname
        self._filepath = filepath
        try:
            self._file = open(filepath,'r')
            self._file.seek(0,2)
        except Exception,msg:
            exc_type, _, exc_tb = sys.exc_info()
            traceList = traceback.extract_tb(exc_tb)
            for (filename, lineno, funcname, text) in traceList:
                self.log("error"," type:%s, file:%s, func:%s"\
                ",lineno:%s, msg:%s"%(exc_type, filename, funcname, lineno, msg,))
                print " type:%s, file:%s, func:%s"\
                ",lineno:%s, msg:%s"%(exc_type, filename, funcname, lineno, msg,)
            sys.exit(1)

    def log(self,log_level,msg):
        msg = "%s %s" % (self._threadname,msg)
        self._logger.writelog(log_level,msg)

    def process_IN_DELETE(self, event):
        self._file.close()

    def process_IN_CREATE(self, event):
        self._file = open(self._filepath,'r')

    def process_IN_MODIFY(self, event):
        while True:
            line = self._file.readline()
            if not line:
                self.log("debug","read file:%s failed" % self._file)
                break
            else:
                try:
                    self.log("debug","queue length:%d" % self._outqueue.qsize())
                    self._outqueue.put_nowait(line)
                except Exception,msg:
                    exc_type, _, exc_tb = sys.exc_info()
                    traceList = traceback.extract_tb(exc_tb)
                    for (filename, lineno, funcname, text) in traceList:
                        self.log("error"," type:%s, file:%s, func:%s"\
                        ",lineno:%s, msg:%s"%(exc_type, filename, funcname, lineno, msg,))


    def __del__(self):
        self._file.close()

class FsMonitor(Thread):

    def __init__(self,filepath,outqueue,logger,threadname):
        Thread.__init__(self,name=threadname)
        self._threadname = threadname
        self._logger = logger
        self._eventhandler = EventHandler(filepath,outqueue,logger,threadname)
        wm = WatchManager()
        mask = IN_DELETE | IN_CREATE | IN_MODIFY
        self._notifier = Notifier(wm, self._eventhandler)
        wm.add_watch(filepath, mask, auto_add= True, rec=True)

    def log(self,log_level,msg):
        msg = "%s %s" % (self._threadname,msg)
        self._logger.writelog(log_level,msg)

    def run(self):
        while True:
            try:
                self._notifier.process_events()
                if self._notifier.check_events():
                    self._notifier.read_events()
            except Exception,msg:
                exc_type, _, exc_tb = sys.exc_info()
                traceList = traceback.extract_tb(exc_tb)
                for (filename, lineno, funcname, text) in traceList:
                    self.log("error"," type:%s, file:%s, func:%s"\
                    ",lineno:%s, msg:%s"%(exc_type, filename, funcname, lineno, msg,))
                self._notifier.stop()
                break


if __name__=='__main__':
    LOG_PATH = '/data/logs/spark/nginx_log/'
    LOG_FILE = 'user_experience.log'
    LOG_LEVEL = 'debug'
    LOG_WHEN = 'D'
    LOG_BACKUPCOUNT = '1'
    LOG_ROTATING_INTERVAL = '7'
    loger = BaseLog(LOG_LEVEL,LOG_PATH,LOG_FILE,LOG_WHEN,LOG_BACKUPCOUNT,LOG_ROTATING_INTERVAL)
    filename =sys.argv[1]
    q=Queue()
    fsmonitor=FsMonitor(filename,q,loger,'test')
    fsmonitor.start()
    while True:
        i = q.get()
        print i

