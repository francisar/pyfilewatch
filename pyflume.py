from common.daemon import Daemon
from filewatch import FsMonitor
from kafkasender import KafkaSender
from common.baselog import BaseLog
from common.config import *
from Queue import Queue
import sys

class Pyflume(Daemon):

    def __init__(self,pidfile,channels, globalLog):
        super(Pyflume, self).__init__(pidfile=pidfile, globalLog = globalLog)
        self._log = globalLog
        self._log.writelog("info","Pyflume init.")
        self._filewatch_threads = []
        self._kafkasend_threads = []
        self._channels = channels

    def run(self):
        self._log.writelog("info","Pyflume run.")
        for channel in self._channels.keys():
            filename = self._channels[channel]['filename']
            topic = self._channels[channel]['topic']
            brokerlist = self._channels[channel]['brokerlist']
            queuelen = self._channels[channel]['queuelen']
            q = Queue(maxsize=queuelen)
            kafkasender = KafkaSender(hosts=brokerlist,inputqueue=q,topic=topic,logger=self._log,threadname=channel+"kafkasender")
            filewatch = FsMonitor(filepath=filename,outqueue=q,logger=self._log,threadname=channel+"filewatch")
            self._filewatch_threads.append(filewatch)
            self._kafkasend_threads.append(kafkasender)
            kafkasender.start()
            filewatch.start()
        for j in self._filewatch_threads:
            j.join()
        for j in self._kafkasend_threads:
            j.join()

if __name__=='__main__':
    globalLog=BaseLog(LOG_LEVEL,LOG_PATH,LOG_FILE,LOG_WHEN,LOG_BACKUPCOUNT,LOG_ROTATING_INTERVAL)
    pyflume = Pyflume(pidfile=PIDFILE,channels=MODULES,globalLog=globalLog)
    if len(sys.argv) == 2:
        if 'start' == sys.argv[1]:
            globalLog.writelog("info","Start pyflume monitor handle.")
            pyflume.start()
        elif 'stop' == sys.argv[1]:
            globalLog.writelog("info","Stop pyflume monitor handle.")
            pyflume.stop()
        elif 'restart' == sys.argv[1]:
            globalLog.writelog("info","Restart pyflume monitor handle.")
            pyflume.restart()
            #pyflume.stopforce(__file__)
            #time.sleep(3)
            #pyflume.start()
            #pyflume.start()
        elif 'debug' == sys.argv[1]:
            globalLog.writelog("info","Start pyflume  handle with debug.")
            pyflume.debug()
        elif 'stopforce' == sys.argv[1]:
            globalLog.writelog("info","stop all exists pyflume  process.")
            pyflume.stopforce(__file__)
        elif 'help' == sys.argv[1]:
            pyflume.usage()
            sys.exit(2)
        else:
            print "Unknown command, please input \"%s help\"."%(sys.argv[0])
            sys.exit(2)
        sys.exit(0)
    else:
        pyflume.usage()
        sys.exit(2)