"""
#  File : repository_services.py
#  Description: This file contains environment services to perform
#  List of Class : RepositoryService
"""
__author__ = 'Saikumar'

from flask import request
from repository_mgmt_src.repository_impl import Repository


class RepositoryService:
    """
    This class contains repository services
    """

    def __init__(self, db_mongo, logger, config):
        self.logger = logger.set_logger(__name__)
        self.repository = Repository(db_mongo, logger, config)

    def get_all_assets(self):
        """
        to get assests inside sub folder
        :return: type->dict
        """
        return self.repository.asset_list()

    def download_assets(self):
        """
        to downlaod file inside sub folder
        """
        return self.repository.download_assets()

    def get_all_repository(self):
        """
        To get all the repositories
        :return: type->dict
        """
        return self.repository.get_repositories()

    def get_repository(self, repo_id):
        """
        To get specific repository
        :param repo_id: type->string by id fetch particular epository
        :return: type->dict
        """
        return self.repository.get_repository(repo_id)

    def create_repository(self):
        """
        To create repository service
        :return: type->dict, success msg or error
        """
        repo_info = request.get_json()
        return self.repository.create_repository(repo_info)

    def update_repository(self, repo_id):
        """

        To update epository service
        :param repo_id: type->string by id update epository
        :return: type->dict, success msg or error
        """
        repo_info = request.get_json()
        return self.repository.update_repository(repo_info, repo_id)

    def delete_repository(self, repo_id):
        """
        To delete epository service
        :param repo_id: type->string by id delete epository
        :return: type->dict, success msg or error
        """
        return self.repository.delete_repository(repo_id)
