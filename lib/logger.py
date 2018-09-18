import os, sys, time
import enum

@enum.unique
class LogLevel(enum.Enum):
    INF = "INF "
    WRN = "WRN "
    ERR = "ERR "

class Logger:

    def __init__(self, prefix, datadir):
        self.datadir = datadir
        self.prefix = prefix
        
        assert self.datadir != None
        assert self.prefix != None

        self.lasttime = time.time()

    def inf(self, str, bWithElapsedTime=False):
        self.log(LogLevel.INF + str, bWithElapsedTime=bWithElapsedTime)
    def wrn(self, str, bWithElapsedTime=False):
        self.log(LogLevel.WRN + str, bWithElapsedTime=bWithElapsedTime)
    def err(self, str, bWithElapsedTime=False):
        self.log(LogLevel.ERR + str, bWithElapsedTime=bWithElapsedTime)

    def log(self, str, bWithElapsedTime=False):
        sElapsedTime = ''
        if(bWithElapsedTime):
            elapsed_time = time.time() - self.lasttime
            sElapsedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            sElapsedTime = '   (prev step took ' + sElapsedTime + ' secs)'
            self._log('{0:<55} {1:>33}'.format(str, sElapsedTime))
        else:
            self._log(str)

        self.lasttime = time.time()

    def _log(self, str):

        print(str)

        with open(os.path.join(self.datadir,'{0}.log'.format(self.prefix)), "a") as log_file:
            log_file.write(str+'\n')
