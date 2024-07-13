"""
  File : config_parser.py
  Description: This document will validate the config
  List of Functions: read_config
"""
import configparser


class ConfigParse:
    """
    Responsible for validating correct config
    """

    def __init__(self):
        self.parse_config = configparser.ConfigParser()

    def read_config(self, file_path='config.cfg'):
        """
        This will read the config
        :return: config object
        """
        try:
            self.parse_config.read(file_path)
            return self.parse_config
        except Exception:
            return None
