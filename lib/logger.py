import os, sys, time
import enum

#alternative logging class to the standard builtin import logging(basicConfig|getLogger) & pprint

@enum.unique
class LogLevel(enum.Enum):
    INF = "INF "
    WRN = "WRN "
    ERR = "ERR "

    def __str__(self):
        return '{0}'.format(self.value)

class Logger:

    PREFIX4ONLY_STDOUT = "*"

    def __init__(self, prefix, datadir):
        self.datadir = datadir
        self.prefix = prefix
        
        assert self.datadir != None
        assert self.prefix != None

        self.lasttime = time.time()

    def logByIdent(self, caller, str, bWithElapsedTime=False):
        #//TODO: log also function name
        self.log(""+self.__class__.__name__+str, bWithElapsedTime)

    def inf(self, str, bWithElapsedTime=False):
        return self.log(LogLevel.INF.value + str, bWithElapsedTime=bWithElapsedTime)
    def wrn(self, str, bWithElapsedTime=False):
        return self.log(LogLevel.WRN.value + str, bWithElapsedTime=bWithElapsedTime)
    def err(self, str, bWithElapsedTime=False):
        return self.log(LogLevel.ERR.value + str, bWithElapsedTime=bWithElapsedTime)

    def log(self, str, bWithElapsedTime=False):
        sElapsedTime = ''
        logged = ''
        if(bWithElapsedTime):
            elapsed_time = time.time() - self.lasttime
            sElapsedTime = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
            sElapsedTime = '   (prev step took ' + sElapsedTime + ' secs)'
            logged = self._log('{0:<55} {1:>33}'.format(str, sElapsedTime))
        else:
            logged = self._log(str)

        self.lasttime = time.time()

        return logged

    def _log(self, str):

        print(str)

        if(self.prefix != self.PREFIX4ONLY_STDOUT):
            with open(os.path.join(self.datadir,'{0}.log'.format(self.prefix)), "a") as log_file:
                log_file.write(str+'\n')

        return str
