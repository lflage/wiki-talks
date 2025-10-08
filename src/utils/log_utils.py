import logging
import os
from ..config import LOGS_DIR

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')

def setup_logger(name, level=logging.INFO):
    """Returns a configured logger 
    log_file must be __file__ from which file you need to log
    """
    file_name = os.path.splitext(os.path.split(name)[-1])[0]
    file_path = os.path.join(LOGS_DIR,file_name)
    if not os.path.exists(LOGS_DIR):
        os.makedirs(LOGS_DIR, exist_ok=True)
    handler = logging.FileHandler(file_path)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger