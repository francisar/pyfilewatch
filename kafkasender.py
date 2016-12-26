from pykafka import KafkaClient
import sys
import traceback
from threading import Thread




class KafkaSender(Thread):

    def __init__(self,hosts,inputqueue,topic,logger,threadname):
        Thread.__init__(self,name=threadname)
        self._threadname = threadname
        self._logger = logger
        self._kafkaclient = KafkaClient(hosts=hosts)
        self._inputqueue = inputqueue
        if topic not in self._kafkaclient.topics.keys():
            self.log("error","cannot fount topic:%s in brokerList:%s" % (topic,hosts))
            print "cannot fount topic:%s in brokerList:%s" % (topic,hosts)
            sys.exit(1)
        self._topic = self._kafkaclient.topics[topic]
        self._producer = self._topic.get_producer()

    def log(self,log_level,msg):
        msg = "%s %s" % (self._threadname,msg)
        self._logger.writelog(log_level,msg)

    def run(self):
        while True:
            try:
                item = self._inputqueue.get()
                self._producer.produce(item)
            except Exception,msg:
                exc_type, _, exc_tb = sys.exc_info()
                traceList = traceback.extract_tb(exc_tb)
                for (filename, lineno, funcname, text) in traceList:
                    self.log("error"," type:%s, file:%s, func:%s"\
                    ",lineno:%s, msg:%s"%(exc_type, filename, funcname, lineno, msg,))
