# logger.py

import logging
import os
from datetime import datetime

class Logger():
    def __init__(self):
        self.file_name = None
        self.define_log_file()
        self.configure_logger()
        self.provide_log_name()


    def define_log_file(self):
        self.file_name = os.path.join("logs", ("grlrr_" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ".log").replace(" ", "_"))

    def configure_logger(self):
        logging.basicConfig(filename = self.file_name, 
                            level    = logging.INFO, 
                            format   = '%(asctime)s %(levelname)-8s %(message)s',
                            datefmt  = '%Y-%m-%d %H:%M:%S')
        
    def provide_log_name(self):
        self.log_name = logging.getLogger(__name__)

    def info(self, log_message):
        self.log_name.info(log_message)

    def debug(self, log_message):
        self.log_name.debug(log_message)



