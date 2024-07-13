"""
#  File : repository_impl.py
#  Description: This file contains environment CRUD operations implementation
#  List of Class : Environment
"""
import json
from http import HTTPStatus
from flask import Response
from repository_mgmt_src.models.repository_model import RepositoryModel
from repository_mgmt_src.utils import response_builder


class Repository:
    """
    Implementation of repository CRUD operations
    """

    def __init__(self, db_mongo, logger, config):
        self.logger = logger.set_logger(__name__)
        self.model = RepositoryModel(db_mongo, logger, config)

    def get_repositories(self):
        """
        to get all repositories
        :return: type=dict, success msg or error
        """
        try:
            repo_details = self.model.get_repository_details(None)
            self.logger.info("successfully received the data : {}".format(repo_details))
            return Response(json.dumps(repo_details), status=200, mimetype='application/json')
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while fetching repo details EXCEPTION : {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            return errors

    def get_repository(self, repo_id):
        """
        to get repository details by id
        :param repo_id: type=string, parameter to get specific repository details
        :return: type=dict, success msg or error
        """
        try:
            repo_details = {'repoId': repo_id}
            repo_list = self.model.get_repository_details(repo_details)
            if repo_list:
                return Response(json.dumps(repo_list), status=200, mimetype='application/json')

            error_msg = 'Repository not found : ' + repo_id
            error_status = "NOT FOUND"
            error = response_builder.response(error_msg, HTTPStatus.NOT_FOUND, error_status)
            return error
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while fetching repo details by id EXCEPTION : {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            self.logger.error(errors)
            return errors

    def create_repository(self, repo_info):
        """
        to create the repository details
        :param repo_info: type=dict, to create repository
        :return: type=dict, resp_obj or error
        """
        try:
            resp_obj = self.model.create_repository(repo_info)
            self.logger.info("successfully created the data : {}".format(resp_obj))
            return resp_obj
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while creating repository : {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            self.logger.erro(errors)
            return errors

    def update_repository(self, repo_info, repo_id):
        """
        to update the repository details
        :param repo_info: type=dict,  to update repository
        :param repo_id: type=string, parameter to update repository
        :return: type=dict, resp_obj or error
        """
        try:
            resp_obj = self.model.update_repository(repo_info, repo_id)
            self.logger.info("successfully updated the data : {}".format(resp_obj))
            return resp_obj
        except Exception as error:
            error_msg = 'Error while updating repository : {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               "Internal error")
            self.logger.error(errors)
            return errors

    def delete_repository(self, repo_id):
        """
        to delete repository details
        :param repo_id: type=string, parameter to delete repository
        :return: type=dict, del_data or error
        """
        try:
            del_data = self.model.delete_repository(repo_id)
            self.logger.info("successfully deleted the data : {}".format(del_data))
            return del_data
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while deleting repository {}'.format(error) + "for id :" + repo_id
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            self.logger.error(errors)
            return errors

    def asset_list(self):
        """
        to get list of assets available in the desired folder inside the repository
        """
        try:
            response, length_of_path = self.model.asset_query()
            if response.status_code == 200:
                # return {'name': response.json()['items'][0]['name']}
                count_of_files = len(response.json()['items'])
                names = []
                for i in range(0, count_of_files):
                    name_included_path = response.json()['items'][i]['name']
                    names.append(name_included_path[length_of_path - 2::])
                return names
                # return Response(json.dumps(response.json()), status=200, mimetype='application/json')
            error_msg = 'Assets not found '
            error_status = "NOT FOUND"
            error = response_builder.response(error_msg, HTTPStatus.NOT_FOUND, error_status)
            return error
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while fetching the assets {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            self.logger.error(errors)
            return errors

    def download_assets(self):
        try:
            response, message_1 = self.model.download_query()
            if response.status_code == 200:
                message_status = "successfully downloaded file"
                message = response_builder.response(message_1, HTTPStatus.OK, message_status)
                return message
            error_msg = 'file not found '
            error_status = "NOT FOUND"
            error = response_builder.response(error_msg, HTTPStatus.NOT_FOUND, error_status)
            return error
        except Exception as error:
            error_status = "INTERNAL SERVER ERROR"
            error_msg = 'Error while downloading the file {}'.format(error)
            errors = response_builder.response(error_msg, HTTPStatus.INTERNAL_SERVER_ERROR,
                                               error_status)
            self.logger.error(errors)
            return errors
