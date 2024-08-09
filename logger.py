#logger.py

import logging

grlrr_log = logging.getLogger(__name__)
logging.basicConfig(filename='grlrr.log', 
                    level=logging.INFO, 
                    format='%(asctime)s %(levelname)-8s %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S')

