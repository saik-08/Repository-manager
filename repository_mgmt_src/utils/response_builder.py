"""
#  File : response_builders.py
#  Description: This file contains Response builders for environment
#  List of functions : success_response, error_response
"""
import json
from flask import Response


def response(msg, status, code):
    """
    For environment success response
    :param msg: type->string,success or error message
    :param code: type->integer, success or error code
    :param status: type->string, success or error status
    :return: success response
    """
    success = {'status': status, 'code': code, 'detail': msg}
    return Response(json.dumps(success), status=status, mimetype='application/json')
