# logger.py

import logging
import os
from datetime import datetime


class Logger():
    
    def __init__(self):
        self.log = self.setup_log()


    def define_log_file(self):
        return os.path.join("logs", ("grlrr_" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ".log").replace(" ", "_"))


    def configure_logger(self, file_name):
        logging.basicConfig(filename = file_name, 
                            level    = logging.INFO, 
                            format   = '%(asctime)s %(levelname)-8s %(message)s',
                            datefmt  = '%Y-%m-%d %H:%M:%S')

    def get_log_name(self):
        return logging.getLogger(__name__)


    def setup_log(self):

        lf = self.define_log_file()
        self.configure_logger(lf)
        return self.get_log_name()

