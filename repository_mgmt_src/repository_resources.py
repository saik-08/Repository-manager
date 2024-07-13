"""
#  File : repository_resources.py
#  Description: This file contains repository management flask restful structure implementation
#  List of Class : Repository, Repositories
"""
from http import HTTPStatus
from flask_restful import Resource
from flask import request

from repository_mgmt_src.repository_services import RepositoryService
from repository_mgmt_src.utils import validator
from repository_mgmt_src.utils import response_builder


class Repository(Resource):
    """
    create and fetch operations for repository
    """

    def __init__(self, db_mongo, logger, config):
        self.service = RepositoryService(db_mongo, logger, config)
        self.logger = logger.set_logger(__name__)

    def get(self, repo_id):
        """
        to get repository details
        :param repo_id: type=string, by id fetch repository details
        :return: type=dict
        """
        validation1 = validator.validate_input(repo_id, validator.id_schema)
        if not (validator.is_valid_uuid(repo_id) or validation1):
            return response_builder.response(status=HTTPStatus.BAD_REQUEST, code="INVALID ID",
                                             msg="error due to invalid ID to fetch the "
                                                 "repository details : {}".format(repo_id))
        return self.service.get_repository(repo_id)

    def put(self, repo_id):
        """
        to update repository details
        :param repo_id: type=string, by id update repository
        :return: type=dict
        """
        validation = validator.validate_input(request.get_json(), validator.environment_validator)
        if not validator.is_valid_uuid(repo_id) and validation:
            self.logger.error('Invalid payload for repository update')
            return response_builder.response('Invalid payload for repository creation',
                                             HTTPStatus.BAD_REQUEST, "INVALID PAYLOAD")
        else:
            return self.service.update_repository(repo_id)

    def delete(self, repo_id):
        """
        to delete repository details
        :param repo_id: type=string, by id delete repository
        :return: type=dict
        """
        return self.service.delete_repository(repo_id)


class Repositories(Resource):
    """
    fetch, update and delete operations for repository
    """

    def __init__(self, db_mongo, logger, config):
        self.service = RepositoryService(db_mongo, logger, config)
        self.logger = logger.set_logger(__name__)

    def get(self):
        """
        to get all repositories details
        :return: type=dict
        """
        return self.service.get_all_repository()

    def post(self):
        """
        to create repository
        :return: type=dict
        """
        if validator.validate_input(request.get_json(), validator.repository_validator):
            self.logger.error('Invalid payload for repository update')
            return response_builder.response('Invalid payload for repository creation',
                                             HTTPStatus.BAD_REQUEST, "INVALID PAYLOAD")
        else:
            return self.service.create_repository()


class Nexus(Resource):
    def __init__(self, db_mongo, logger, config):
        self.service = RepositoryService(db_mongo, logger, config)
        self.logger = logger.set_logger(__name__)

    def get(self):
        """
        to get all repositories details
        :return: type=dict
        """
        return self.service.get_all_assets()


class Download(Resource):
    def __init__(self, db_mongo, logger, config):
        self.service = RepositoryService(db_mongo, logger, config)
        self.logger = logger.set_logger(__name__)

    def get(self):
        """
        to downlaod file from the repository
        :return: type=dict
        """
        return self.service.download_assets()
