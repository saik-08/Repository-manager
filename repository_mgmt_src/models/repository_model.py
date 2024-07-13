"""
#  File : repository_model.py
#  Description: This file contains repository CRUD operations.
#  List of Class : RepositoryModel
"""
import logging
from datetime import datetime
from http import HTTPStatus
from uuid import uuid4
from gridfs import GridFS

import pymongo
from flask import request
import requests
import yaml
from repository_mgmt_src.utils.service_utils import FileOperation
from repository_mgmt_src.utils import response_builder


class DbException(Exception):
    """
    this contains constructor to initialize the exception message
    """

    def __init__(self, message, http_code=HTTPStatus.NOT_FOUND):
        self.http_code = http_code
        Exception.__init__(self, "database exception " + str(message))


class RepositoryModel:
    """
    CRUD operations for repository
    """

    def __init__(self, db_mongo, logger, config):
        self.config = config
        self.file_ops = FileOperation(logger)
        self.logger = logger.set_logger(__name__)
        self.db_ops = db_mongo

    @staticmethod
    def construct_update_filter(repo_details):
        """
        To construct update repository filter to update
        :param repo_details: type=dict, to construct update filter
        :return: type=dict, update_filter
        """
        update_filter = {'repoId': repo_details['repoId']}
        return update_filter

    @staticmethod
    def construct_payload(repo_details):
        """
        To construct details for storing repository details in db for first time
        :param repo_details: type=dict, to construct nf test details
        :return: type=dict, db_data
        """
        repo_data = {'repoId': repo_details['repoId'], 'repoName': repo_details['repoName'],
                     'repoUrl': repo_details['repoUrl'], 'username': repo_details['username'],
                     'password': repo_details['password']}

        repo_data.update(createdDate=datetime.now().replace(microsecond=0).timestamp(),
                         modifiedDate=datetime.now().replace(microsecond=0).timestamp())
        return repo_data

    def construct_update_data(self, repo_details):
        """
        To update repository details by repo_id in db
        :param repo_details: type=dict, to  update repository
        :return: type=dict, update_data
        """
        update_data = {
            'modifiedBy': self.token_details(),
            'modifiedDate': datetime.now().replace(microsecond=0).timestamp()}
        if 'repoUrl' in repo_details.keys() and repo_details['repoUrl']:
            update_data.update(repoUrl=repo_details['repoUrl'])
        if 'username' in repo_details.keys() and repo_details['username']:
            update_data.update(username=repo_details['username'])
        update_data.update(status=repo_details['username'])
        if 'password' in repo_details.keys() and repo_details['password']:
            update_data.update(password=repo_details['password'])
        if 'repoName' in repo_details.keys() and repo_details['repoName']:
            update_data.update(repoName=repo_details['repoName'])
        return update_data

    @staticmethod
    def destruct_update_filter(repo_details):
        """
        To delete repository details by repository ID
        :param repo_details: type=dict, to create delete filter
        :return: type=dict, update_filter
        """
        update_filter = {'repoId': repo_details['repoId']}
        return update_filter

    def get_repository_details(self, repo_details):
        """
        To fetch specific repository details from db
        :param repo_details: type=string ,
        to fetch the repository details by id or none to get all
         repository details
        :return: type=dict, result or raise exception
        """
        try:
            get_info = self.db_ops.get_list(self.config['COLLECTIONS']['REPO_COLLECT_NAME'],
                                            repo_details)
            result = self.file_ops.convert_id(get_info)
            self.logger.info("successfully received the repository data "
                             "from db : {}".format(result))
            return result
        except Exception as error:
            raise DbException("Error while fetching repository."
                              "Error:{}".format(error),
                              http_code=HTTPStatus.INTERNAL_SERVER_ERROR)

    def create_repository(self, repo_info):
        """
        To create repository details and store in db
        :param repo_info: type=dict, to create repository details
        :return: type=dict, error msg or success msg or exception
        """
        try:
            repo_details = repo_info
            repo_details["repoId"] = str(uuid4())
            repo_name = repo_info['repoName']
            repo_url = repo_info['repoUrl']
            query_name = {'repoName': repo_name}
            query_url = {'repoUrl': repo_url}
            repo_check_name = self.db_ops.get_list(self.config['COLLECTIONS']['REPO_COLLECT_NAME'],
                                                   query_name)
            repo_check_url = self.db_ops.get_list(self.config['COLLECTIONS']['REPO_COLLECT_NAME'],
                                                  query_url)
            if not repo_check_name:
                if not repo_check_url:
                    db_data = self.construct_payload(repo_details)
                    db_data.update(modifiedDate=None)
                    self.db_ops.create(self.config['COLLECTIONS']['REPO_COLLECT_NAME'], db_data)
                    self.logger.info("successfully inserted the data to db")
                    resp_msg = 'Repository: ' + repo_details['repoName'] + ' created successfully'
                    self.logger.info(resp_msg)
                    return response_builder.response(resp_msg,
                                                     HTTPStatus.CREATED, "SUCCESSFULLY CREATED")
            self.logger.info('Repository details already exist')
            return response_builder.response('Repository details already exist chceck for name and url',
                                             HTTPStatus.BAD_REQUEST, "INVALID ARGUMENT")
        except Exception as error:
            self.logger.error('Error while creating repository ')
            logging.error('Error while creating repository ')
            return response_builder.response('Error while creating repository:{}'.format(error),
                                             HTTPStatus.INTERNAL_SERVER_ERROR, "INTERNAL ERROR")

    def delete_repository(self, repo_id):
        """
        To delete repositoy details by id
        :param repo_id: type=string, to delete epository
        :return: type=dict, error msg or success msg or exception
        """
        try:
            query = {'repoId': repo_id}
            repo_delete = self.get_repository_details(query)
            if not repo_delete:
                return response_builder.response("Repository " + repo_id + " does not exist",
                                                 HTTPStatus.NOT_FOUND, "REPOSITORY NOT FOUND")
            delete = self.destruct_update_filter(query)
            self.db_ops.del_one(self.config['COLLECTIONS']['REPO_COLLECT_NAME'], delete)
            self.logger.info("successfully deleted the data from db")
            return response_builder.response('Repository: ' + repo_id + ' deleted successfully',
                                             HTTPStatus.OK, "DELETED SUCCESSFULLY")
        except Exception as error:
            self.logger.error('Error while deleting REPOSITORY ')
            return response_builder.response('Error while deleting environment : {}'.format(error),
                                             HTTPStatus.INTERNAL_SERVER_ERROR, "INTERNAL ERROR")

    def update_repository(self, repo_info, repo_id):
        """
        to update repository details by id
        :param repo_info: type=dict, to update repository details
        :param repo_id: type=string, to update repository details by id
        :return: type=dict, error msg or success msg or exception
        """
        try:
            repo_details = repo_info
            query = {'repoId': repo_id}
            repo_update = self.get_repository_details(query)
            if not repo_update:
                return response_builder.response("Repository " + repo_details['repoName'] +
                                                 " does not exist", HTTPStatus.NOT_FOUND,
                                                 "Repository NOT FOUND")
            update_filter = self.construct_update_filter(query)
            update_data = self.construct_update_data(repo_details)
            self.db_ops.set_one(self.config['COLLECTIONS']['REPO_COLLECT_NAME'],
                                update_filter, update_data)
            self.logger.info("successfully updated the data to db")
            return response_builder.response('Repository: ' + repo_details['repoName'] +
                                             ' updated successfully', HTTPStatus.OK,
                                             "UPDATED SUCCESSFULLY")
        except Exception as error:
            self.logger.error('Error while updating repository ')
            logging.error('Error while updating repository ')
            return response_builder.response("Error while updating repository : {}".format(error),
                                             HTTPStatus.INTERNAL_SERVER_ERROR, "Internal error")

    def token_details(self):
        """
        return the details of the token in header from auth module
        :return: string, returns the username who does this action
        """
        try:
            token = request.headers.get('Authorization')
            headers = {"Authorization": token}
            end_point = "https://{}:{}/{}".format(self.config["APIs"]["AUTH_HOST"],
                                                  self.config["APIs"]["AUTH_PORT"],
                                                  self.config["APIs"]["TOKEN_URL"])
            details = requests.request('GET', url=end_point, headers=headers, data={}, verify=False)
            value = yaml.safe_load(details.content)
            if details.status_code == HTTPStatus.OK:
                return value[0]["username"]
            else:
                return response_builder.response(msg="Error in authenticating the token provided",
                                                 status=details.status_code,
                                                 code='AUTH Module error')
        except Exception as error:
            self.logger.error('Error while querying the token ', error)
            raise

    def asset_query(self):
        """
        return list of assets present inside the desired folder of repository
        :return: int, rentuns the length of group i.e., from the root folder to final folder and response
        """
        try:
            repository = request.args.get('repository')
            type_ = request.args.get('type')
            group = '"/{}/Descriptors/{}"'.format(repository, type_)
            print(group)
            asset_endpoint = self.file_ops.construct_route(host=self.config['NEXUS']['NEXUS_HOST'],
                                                           port=self.config['NEXUS']['NEXUS_PORT'],
                                                           resource=self.config['NEXUS']['ASSET_URL'])
            response = requests.get(asset_endpoint.format(repository, group))
            length_of_group = len(group)
            return response, length_of_group

        except Exception as error:
            self.logger.error('Error while fetching assets ', error)
            raise

    def download_query(self):
        """
        it will download the file present in the given path to local machine in present working directory
        :return: int, returns the length of group i.e., from the root folder to final folder and response
        """
        try:
            repository = request.args.get('repository')
            type_2 = request.args.get('typevnf')
            name_of_file = request.args.get('file')
            mongo_host = self.config['APIs']['mongo_host']
            mongo_port = self.config['APIs']['mongo_port']
            mongo_port = int(mongo_port)
            db_name = self.config['APIs']['db_name']

            asset_endpoint = self.file_ops.construct_route(host=self.config['NEXUS']['NEXUS_HOST'],
                                                           port=self.config['NEXUS']['NEXUS_PORT'],
                                                           resource=self.config['NEXUS']['DOWNLOAD_URL'])
            final_endpoint = asset_endpoint + '/' + repository + '/' + repository + '/' + "Descriptors" \
                + '/' + type_2 + '/' + name_of_file
            response = requests.get(final_endpoint)
            if response.status_code == 200:
                file_binary = response.content
                client = pymongo.MongoClient(mongo_host, mongo_port)
                db = client[db_name]
                fs = GridFS(db)
                file_id = fs.put(file_binary, filename=name_of_file)

                message = {"message": "File uploaded to MongoDB GridFS", "file_id": str(file_id), "file_name": name_of_file}

            else:
                message = "failed to download the file"
            return response, message
        except Exception as error:
            self.logger.error('Error while fetching assets ', error)
            raise
