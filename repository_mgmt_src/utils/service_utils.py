"""
#  File : service_utils.py
#  Description: This file contains File operations for environment
#  List of functions : remove_id, convert_id
"""


class FileOperation:
    """
    Remove and convert id for environment
    """

    def __init__(self, logger):
        self.logger = logger.set_logger(__name__)

    def remove_id(self, repo_data):
        """
        To remove id
        :param repo_data: type=object, environment id to remove
        :return: data or exception
        """
        try:
            for value in repo_data:
                value.pop("_id", None)
            return repo_data
        except BaseException as error:
            self.logger.error('Error while removing object ids from records ', error)
            raise

    def convert_id(self, repo_data):
        """
        To convert id to string
        :param repo_data: type=string, environment id convert to string
        :return: data or exception
        """
        try:
            for dic in repo_data:
                dic['_id'] = str(dic['_id'])
            return repo_data
        except BaseException as error:
            self.logger.error('Error while converting object ids from records ', error)
            raise

    @staticmethod
    def construct_route(host, port, resource, is_https=False):
        """
        this method is used to construct the end point requests call
        :param host: type=string, contains the IP
        :param port: type=string, contains the port number
        :param resource: type=string, contains the end point
        :param is_https: type=bool, says about the type of http call
        :return: type= string, returns the construct routing point
        """
        if is_https:
            return "https://{}:{}/{}".format(host, port, resource)
        return "http://{}:{}/{}".format(host, port, resource)