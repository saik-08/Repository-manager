"""
file:logger_func.py
description: this file contains method to register the log into a log file based on timed rotation
"""
import os
import sys
from logging import FileHandler, StreamHandler, Formatter, getLogger, INFO
from pythonjsonlogger import jsonlogger


class Logger:
    """
    this contains methods to log the details in the log file for debugging purpose
    """

    def __init__(self, config):
        self.config = config

    def set_logger(self, name):
        """
        this method is used to store logs into a log file
        :param name: contains name of the module from where log comes up
        :return: type=dict, contains the attributes of the logger
        """
        if not os.path.isdir(self.config['LOGS']['LOGGER_PATH']):
            os.makedirs(self.config['LOGS']['LOGGER_PATH'])
        logger = getLogger(name)
        logger.setLevel(INFO)
        if logger.hasHandlers():
            logger.handlers.clear()
        formatter = Formatter(
            '[%(asctime)s : %(module)s : %(lineno)s : %(levelname)s]: %(message)s')
        jsonformatter = jsonlogger.JsonFormatter(
            '%(asctime)s %(module)s %(lineno)s %(levelname)s %(message)s')
        file_handler = FileHandler(self.config['LOGS']['REPLOG_FILENAME'])
        file_handler.setLevel(INFO)
        file_handler.setFormatter(jsonformatter)
        logger.addHandler(file_handler)
        stream_handler = StreamHandler(sys.stdout)
        stream_handler.setLevel(INFO)
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)
        return logger
