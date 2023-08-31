"""Module with logger"""

import logging
import sys
import os
import datetime


class Logger:
    """
    Logging in cmd and in the log file (by date).

    :return: logging
    """

    def __init__(self):
        self.path_to_logs = \
            os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
        self.logger = self._setup_logger()

    def _setup_logger(self):
        """Method for setup logger."""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = \
            logging.Formatter("%(asctime)s [%(levelname)s] %(message)s",
                              datefmt='%d-%b-%y %H:%M:%S')
        file_handler = \
            logging.FileHandler(f'{self.path_to_logs}/{datetime.date.today()}.log',
                                mode="a")
        file_handler.setFormatter(formatter)
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        return logger
