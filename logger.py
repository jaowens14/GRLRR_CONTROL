#logger.py

import logging
import os
from datetime import datetime

log_file_name = os.path.join("logs", ("grlrr_" + str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')) + ".log").replace(" ", "_"))

grlrr_log = logging.getLogger(__name__)

logging.basicConfig(filename=log_file_name, 
                    level=logging.INFO, 
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

