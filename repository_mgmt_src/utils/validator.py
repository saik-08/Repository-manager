"""
  File : validator.py
  Description: This file contains validation schema for NF and NS test management implementation
"""
from http import HTTPStatus
from uuid import UUID
from jsonschema import validate as js_v, exceptions as js_e

# To test for valid UUID

__author__ = "Alfonso Tierno <alfonso.tiernosepulveda@telefonica.com>"
__version__ = "0.1"

"""
Validator of input data using JSON schemas for those items that not contains an OSM yang
information model
"""
# Basis schemas
shortname_schema = {"type": "string", "minLength": 0, "maxLength": 60,
                    "pattern": "^[^,;()\\.\\$'\"]+$"}
passwd_schema = {"type": "string", "minLength": 0, "maxLength": 60}
name_schema = {"type": "string", "minLength": 0, "maxLength": 255, "pattern": "^[^,;()'\"]+$"}
string_schema = {"type": "string", "minLength": 0, "maxLength": 255}
xml_text_schema = {"type": "string", "minLength": 0, "maxLength": 1000, "pattern": "^[^']+$"}
description_schema = {"type": ["string", "null"], "maxLength": 255, "pattern": "^[^'\"]+$"}
id_schema_fake = {"type": "string", "minLength": 2, "maxLength": 36}
bool_schema = {"type": "boolean"}
null_schema = {"type": "null"}
# "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
id_schema = {"type": "string", "pattern": "^[a-fA-F0-9]{8}(-[a-fA-F0-9]{4}){3}-[a-fA-F0-9]{12}$"}
time_schema = {"type": "string", "pattern": "^[0-9]{4}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]([0-5]:){2}"}
pci_schema = {"type": "string",
              "pattern": "^[0-9a-fA-F]{4}(:[0-9a-fA-F]{2}){2}\\.[0-9a-fA-F]$"}
pci_extended_schema = {"type": "string", "pattern": "^[0-9a-fA-F.:-\\[\\]]{12,40}$"}
http_schema = {"type": "string", "pattern": "^(https?|http)://[^'\"=]+$"}
bandwidth_schema = {"type": "string", "pattern": "^[0-9]+ *([MG]bps)?$"}
memory_schema = {"type": "string", "pattern": "^[0-9]+ *([MG]i?[Bb])?$"}
integer0_schema = {"type": "integer", "minimum": 0}
integer1_schema = {"type": "integer", "minimum": 1}
path_schema = {"type": "string", "pattern": "^(\\.){0,2}(/[^/\"':{}\\(\\)]+)+$"}
vlan_schema = {"type": "integer", "minimum": 1, "maximum": 4095}
vlan1000_schema = {"type": "integer", "minimum": 1000, "maximum": 4095}
mac_schema = {"type": "string",
              "pattern": "^[0-9a-fA-F][02468aceACE](:[0-9a-fA-F]{2}){5}$"}
dpid_Schema = {"type": "string",
               "pattern": "^[0-9a-fA-F]{2}(:[0-9a-fA-F]{2}){7}$"}
ip_schema = {"type": "string",
             "pattern": "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.)"
                        "{3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"}
url_schema = {"type": "string",
              "pattern": "^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\\.){3}"
                         "(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)/(30|[12]?[0-9])$"}
port_schema = {"type": "integer", "minimum": 1, "maximum": 65534}
object_schema = {"type": "object"}
schema_version_2 = {"type": "integer", "minimum": 2, "maximum": 2}
log_level_schema = {"type": "string", "enum": ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]}
checksum_schema = {"type": "string", "pattern": "^[0-9a-fA-F]{32}$"}
size_schema = {"type": "integer", "minimum": 1, "maximum": 100}
schema_version = {"type": "string", "enum": ["1.0"]}
schema_type = {"type": "string"}
wim_type = shortname_schema  # {"enum": ["ietfl2vpn", "onos", "odl", "dynpac", "fake"]}
k8srepo_types = {"enum": ["helm-chart", "juju-bundle"]}
repository_validator = {
    "repoUrl": url_schema,
    "username": name_schema,
    "password": passwd_schema
}

sdn_properties = {
    "name": name_schema,
    "type": {"type": "string"},
    "url": {"type": "string"},
    "user": shortname_schema,
    "password": passwd_schema,
    "config": {"type": "object"},
    "description": description_schema,
    # The folowing are deprecated. Maintanied for backward compatibility
    "dpid": dpid_Schema,
    "ip": ip_schema,
    "port": port_schema,
    "version": {"type": "string", "minLength": 1, "maxLength": 12},
}

k8scluster_nets_schema = {
    "title": "k8scluster nets input schema",
    "$schema": "http://json-schema.org/draft-04/schema#",
    "type": "object",
    "patternProperties": {".": {"oneOf": [name_schema, null_schema]}},
    "minProperties": 1,
    "additionalProperties": False
}
vim_type = shortname_schema
array_edition_schema = {
    "type": "object",
    "patternProperties": {
        "^\\$": {}
    },
    "additionalProperties": False,
    "minProperties": 1,
}
nameshort_list_schema = {
    "type": "array",
    "minItems": 1,
    "items": shortname_schema,
}

environment_validator = \
    {
        "type": "object",
        "properties": {
            "envName": name_schema,
            "envType": schema_type,
            "envId": string_schema,
            "status": string_schema,
            "username": string_schema,
            "orchestrator": {
                "type": "object",
                "properties": {
                    "orchestName": name_schema,
                    "orchestType": schema_type,
                    "orchestIp": ip_schema,
                    "orchestPort": string_schema,
                    "orchestUser": shortname_schema,
                    "orchestPwd": passwd_schema
                }
            },
            "vimDetails": {
                "type": "array",
                "minItems": 1,
                "items": {
                    "type": "object",
                    "properties": {
                        "vimName": name_schema,
                        "type": vim_type,
                        "vimUrl": string_schema,
                        "tenantName": name_schema,
                        "vimUser": shortname_schema,
                        "vimPwd": passwd_schema,
                        "description": string_schema,
                        "configFile": string_schema
                    }
                }
            },
            "k8sDetails": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "k8Name": string_schema,
                        "k8Version": schema_version,
                        "vimAccount": string_schema,
                        "description": string_schema,
                        "k8Nets": string_schema,
                        "k8sCredentials": string_schema
                    }
                }
            },
            "k8sRepo": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "k8RepoName": name_schema,
                        "k8Type": k8srepo_types,
                        "k8Url": string_schema,
                        "description": string_schema
                    }
                }
            },
            "WimDetails": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "wimName": string_schema,
                        "wimType": string_schema,
                        "wimId": string_schema,
                        "wimURL": string_schema,
                        "WimUser": shortname_schema,
                        "wimPwd": passwd_schema,
                        "description": name_schema,
                        "wimConfig": string_schema
                    }
                }
            },
            "sdnDetails": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "sdnName": string_schema,
                        "type": string_schema,
                        "ip": string_schema,
                        "sdnPort": string_schema,
                        "sdnUser": string_schema,
                        "sdnPwd": passwd_schema,
                        "sdnDPID": string_schema,
                        "description": string_schema,
                        "status": string_schema,
                        "sdnId": string_schema,
                        "sdnVersion": string_schema
                    }
                }
            }
        }
    }


class ValidationError(Exception):
    """
    This contains validation error theme for test management
    """

    def __init__(self, message, http_code=HTTPStatus.UNPROCESSABLE_ENTITY):
        self.http_code = http_code
        Exception.__init__(self, message)


def validate_input(indata: object, schema_to_use: object) -> object:
    """
        Validates input data against json schema
        :param indata: user input data. Should be a dictionary
        :param schema_to_use: jsonschema to test
        :return: None if ok, raises ValidationError exception on error
    """
    try:
        if schema_to_use:
            js_v(indata, schema_to_use)
        return None
    except js_e.ValidationError as error:
        if error.path:
            error_pos = "at '" + ":".join(map(str, error.path)) + "'"
        else:
            error_pos = ""
        return ValidationError("Format error {} '{}' ".format(error_pos, error.message))
    except js_e.SchemaError:
        return ValidationError("Bad json schema {}".format(schema_to_use),
                               http_code=HTTPStatus.INTERNAL_SERVER_ERROR)


def is_valid_uuid(val):
    """
    Test for a valid UUID
    :param val: string to test
    :return: True if val is a valid uuid, False otherwise
    """
    try:
        if UUID(val):
            return True
        return False
    except (TypeError, ValueError, AttributeError):
        return False
