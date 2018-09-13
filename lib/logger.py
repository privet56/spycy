import os, sys, time

class Logger:

    def __init__(self, prefix, datadir):
        self.datadir = datadir
        self.prefix = prefix
        
        assert self.datadir != None
        assert self.prefix != None

        self.lasttime = time.time()

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
