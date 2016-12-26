#!/usr/bin/python
#coding:utf-8
import os
import sys
import atexit
import time
import signal
from signal import SIGTERM

class Daemon(object):
    """
    A generic daemon class.

    Usage: subclass the Daemon class and override the run() method
    """
    def __init__(self, pidfile, globalLog, stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = os.path.abspath(pidfile)
        self._globalLog = globalLog

    def daemonize(self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        """
        # do first fork
        try:
            pid = os.fork()
            if pid > 0:
                self._globalLog.debug("fork failed pid %d"%pid)
                sys.exit(0)
            elif pid == 0:
                self._globalLog.debug("in child %d"%pid)
        except OSError, e:
            self._globalLog.error("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir("/")
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                sys.exit(0)
            elif pid == 0:
                self._globalLog.debug("in child %d"%pid)
        except OSError, e:
            self._globalLog.error("fork #1 failed: %d (%s)\n" % (e.errno, e.strerror))
            #self._globalLog.error("fork #2 failed: %d (%s)\n" % (e.errno, e.strerror))
            sys.exit(1)

        # redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()
        si = file(self.stdin, 'r')
        so = file(self.stdout, 'a+')
        se = file(self.stderr, 'a+', 0)
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())

        # registrem destructor function
        atexit.register(self.delpid)
        # write pidfile
        try:
            fd = open(self.pidfile, 'w+')
            fd.write('%s\n'%(str(os.getpid())))
            fd.close()
            os.chmod(self.pidfile, 0777)
        except IOError,msg:
            self._globalLog.error("%s:open pidfile failed."%msg)
            sys.exit(1)

    def sigInt(self, signum, frame):
        '''SIGINT'''
        self._globalLog.error("Receive SIGINT, exit process")
        sys.exit(0)

    def delpid(self):
        '''destructor function'''
        os.remove(self.pidfile)

    def dbstop(self):
        '''stop debug daemon'''
        sys.exit(-1)

    def debug(self):
        '''debug daemon'''
        # register signal
        signal.signal(signal.SIGINT, self.sigInt)

        # run
        self.run()

    def start(self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            #pid = None
            pf.close()
        except IOError,e:
            #self._globalLog.error("pid faild: %d (%s)\n" % (e.errno, e.strerror))
            pid = None

        # existed daemon process, quit
        if pid:
            message = "pidfile %s already exist. Daemon already running?\n"
            self._globalLog.error(message % self.pidfile)
            print message
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        # run
        self.run()

    def stop(self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = file(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError:
            pid = None

        if not pid:
            message = "Not found pid at Pidfile %s does not exist. Manual check process please!"
            self._globalLog.error( message % self.pidfile)
            print message
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                os.kill(pid, SIGTERM)
                time.sleep(0.1)
        except OSError, err:
            err = str(err)
            if err.find("No such process") > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                message = 'Not found pid=%s at %s. Manual removal process please.'
                print message
                self._globalLog.error(message%(pid, self.pidfile))
            else:
                self._globalLog.error('Daemon stop:%s'%err)
                print 'Daemon stop:%s'%err
                sys.exit(1)

    def restart(self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()

    def stopforce(self, cmdfile):
        '''Forced to stop process'''
        pid = str(os.getpid())
        commandstr = "ps -ef|grep python|grep -w '%s'|grep -v grep|awk '{print $2}'|grep -v %s|xargs kill -9"%(cmdfile,pid)
        if os.system(commandstr)>>8 is not 0:
            self._globalLog.error("Forced to stop all process failed, command:%s"%commandstr)

    def usage(self):
        '''user help info'''
        print '''
        usage:
            python command start      ---   start a new monitor
            python command stop       ---   stop a exists monitor
            python command stopforce  ---   forced to stop exists monitor
            python command restart    ---   restart a monitor
            python command debug      ---   start a monitor with debug
            python command help       ---   help information
        '''

    def run(self):
        """
        You should override this method when you subclass Daemon.
        It will be called after the process has been
        daemonized by start() or restart().
        """
        pass