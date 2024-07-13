"""
#  File : repository_app.py
#  Description: This file going to run repository app
#  List of Class : resource_allocator, initiator
"""
__author__ = 'Saikumar'

import os
from configparser import ConfigParser
from flask import Flask
from flask_restful import Api
from flask_cors import CORS
from repository_mgmt_src.repository_resources import Repository, Repositories, Nexus, Download
from repository_mgmt_src.operations.dbmongo import DbMongo
from repository_mgmt_src.utils.logger_func import Logger
from repository_mgmt_src.utils.config_parser import ConfigParse


def resource_allocator(api, db_val=None, logger_val=None, config_val=None):
    """
    resource allocator for repository
    :param api: type=string, Repository api by flask restful
    :param db_val: type=object, contains db value to connect
    :param logger_val: type=object, to store logs
    :param config_val: type=object, indicates configuration details
    :return: type=object
    """
    api.add_resource(Repositories, '/manager/repositorymgmt/v1/repositories',
                     resource_class_kwargs={'db_mongo': db_val,
                                            'logger': logger_val, 'config': config_val})
    api.add_resource(Repository, '/manager/repositorymgmt/v1/repositories/<repo_id>',
                     resource_class_kwargs={'db_mongo': db_val,
                                            'logger': logger_val, 'config': config_val})

    api.add_resource(Nexus, '/manager/repositorymgmt/v1/assets',
                     resource_class_kwargs={'db_mongo': db_val,
                                            'logger': logger_val, 'config': config_val})

    api.add_resource(Download, '/manager/repositorymgmt/v1/download',
                     resource_class_kwargs={'db_mongo': db_val,
                                            'logger': logger_val, 'config': config_val})


def initiator():
    """
    To initiate db connect and logger function
    :return: type=object
    """
    repository_app = Flask(__name__)
    CORS(repository_app)
    ip_allocator()
    config = ConfigParse().read_config('repository_mgmt_src/config.cfg')
    if config:
        api = Api(repository_app)
        config_db = {"host": config['APIs']['MONGO_HOST'],
                     "port": int(config['APIs']['MONGO_PORT']),
                     "db_name": config['APIs']['DB_NAME']}
        db_mongo = DbMongo()
        db_mongo.db_connect(config_db)
        logger = Logger(config)
        resource_allocator(api, db_mongo, logger, config)
        return {"api": api, "app": repository_app, "db_mongo": db_mongo, "logger": logger,
                "config": config}
    return None


def ip_allocator():
    """
    this method is used to allocate dynamic ip details to repository management microservice
    :return: type=file,config
    """
    config = ConfigParser()
    config.read('repository_mgmt_src/config.cfg')
    service_list = dict(config.items('APIs'))
    logger = Logger(config).set_logger(__name__)
    for service in service_list.keys():
        config.set('APIs', service, os.getenv(service))
        logger.info('{}:{}'.format(service, os.getenv(service)))
    config.set('Default', 'PORT', os.getenv('PORT'))
    with open('repository_mgmt_src/config.cfg', 'w') as configfile:
        config.write(configfile)
    return config


def start_service(connection):
    """
    this method is used to start the repository management microservice
    """
    config = connection["config"]
    connection["app"].run(host=config['Default']['GATEWAY'], port=config['Default']['PORT'],
                          debug=config['Default']['DEBUG_MODE'])


def stop_service(connection):
    """
    this method is used to stop the repository management microservice
    :return: None
    """
    connection["db_mongo"].db_disconnect()


if __name__ == "__main__":
    connections = initiator()
    try:
        start_service(connections)
    except Exception as exe:
        logger_var = connections['logger'].set_logger(__name__)
        logger_var.info("EXCEPTION: {}".format(exe))
        stop_service(connections)
