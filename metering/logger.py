import sys
import logging

class Logger:
    '''This class encapsulate this modules logging logic.'''
    
    def __init__(self):
        self.log = logging.getLogger('amberflo')

    def debugMode(self):
        self.log.setLevel(logging.DEBUG)

    def debug(self, massage, *args):
        '''Logs a debug level message.'''

        try:
            self.log.debug(massage, *args)
        # https://docs.python.org/3/library/exceptions.html
        except RuntimeError:
            print(massage)

    def warn(self, massage, *args):
        '''Logs a warning level message (a warning is recoverable issue).'''

        try:
            self.log.warning(massage, *args)
        except RuntimeError:
            print(massage, file=sys.stderr)

    def error(self, massage, *args):
        '''Logs an error level message (an error is unrecoverable issue).'''

        try:
            self.log.error(massage, *args)
        except RuntimeError:
            print(massage, file=sys.stderr)
