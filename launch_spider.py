# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-
# LOGGING

import logging
from datetime import datetime

LOG_FILE_PATH = 'log/'
LOG_FILENAME = 'black_widow'
LOG_FILE_EXT = '.log'
LOG_FORMAT = "%(message)s"  

def init_logging():
    
  t = datetime.now()
  tstamp = '%d-%d-%d-%d-%d' % (t.year, t.month, t.day, t.hour, t.minute)
  fname = LOG_FILE_PATH + LOG_FILENAME + '_' + tstamp + LOG_FILE_EXT    
  print('log file - %s' % fname)
  logging.basicConfig(filename=fname, level=logging.INFO, format=LOG_FORMAT)  
  
  # add a redirect to console
  
  class LogToConsoleHandler(logging.Handler):
    def emit(self, record):
        print(record.msg)

  logging.getLogger().addHandler(LogToConsoleHandler())  

# =-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-

from core import knights_tour

def main():
    init_logging()
    knights_tour.main()

if __name__ == '__main__':
  main()
