"""
#  File : dbmongo.py
#  Description: This file contains CRUD operations to store in mongo db
#  List of Class : DbException
"""
from threading import Lock
from http import HTTPStatus
from copy import deepcopy
from pymongo import MongoClient, errors


class DbException(Exception):
    """
    this contains constructor to initialize the exception message
    """

    def __init__(self, message, http_code=HTTPStatus.NOT_FOUND):
        self.http_code = http_code
        Exception.__init__(self, "database exception " + str(message))


def deep_update(to_update, update_with):
    """
    Similar to deepcopy but recursively with nested dictionaries. 'to_update' dict is updated
    with a content copy of 'update_with' dict recursively
    :param to_update: must be a dictionary to be modified
    :param update_with: must be a dictionary. It is not changed :return: to_update
    """
    for key in update_with:
        if key in to_update:
            if isinstance(to_update[key], dict) and isinstance(update_with[key], dict):
                deep_update(to_update[key], update_with[key])
                continue
        to_update[key] = deepcopy(update_with[key])
    return to_update


class DbMongo:
    """
    this contains method to connect, create, update, fetch and delete the dataabse entries using
    pymongo
    """

    def __init__(self):
        self.client = None
        self.db_mongo = None
        self.lock = Lock()

    def db_connect(self, config):
        """
        Connect to database
        :param config: Configuration of database
        :return: None or raises DbException on error
        """
        try:
            self.client = MongoClient(config["host"], config["port"])
            self.db_mongo = self.client[config["db_name"]]
        except errors.PyMongoError as exe:
            raise DbException(exe)

    def _format_filter(self, q_filter):
        """
        this method is used to format the filter data
        :param q_filter: filter value
        :return: filtered data
        """
        try:
            db_filter = {}
            if not q_filter:
                return db_filter
            for query_k, query_v in q_filter.items():
                dot_index = query_k.rfind(".")
                if dot_index > 1 and query_k[dot_index + 1:] in ("eq", "ne", "gt", "gte", "lt",
                                                                 "lte", "cont", "ncont", "neq"):
                    operator = "$" + query_k[dot_index + 1:]
                    if operator == "$neq":
                        operator = "$ne"
                    k = query_k[:dot_index]
                else:
                    operator = "$eq"
                    k = query_k

                val_v = query_v
                val_v, operator = self.assign_valv(val_v, operator, query_v)
                if operator in ("$eq", "$cont"):
                    # v cannot be a comma separated list, because operator would have been
                    # changed to $in
                    db_v = val_v
                elif operator == "$ncount":
                    # v cannot be a comma separated list, because operator would have been
                    # changed to $nin
                    db_v = {"$ne": val_v}
                else:
                    db_v = {operator: val_v}

                # process the ANYINDEX word at k.
                kleft, _, kright = k.rpartition(".ANYINDEX.")
                while kleft:
                    k = kleft
                    db_v = {"$elemMatch": {kright: db_v}}
                    kleft, _, kright = k.rpartition(".ANYINDEX.")

                # insert in db_filter maybe db_filter[k] exist. e.g. in the query string for
                # values between 5 and 8: "a.gt=5&a.lt=8"
                deep_update(db_filter, {k: db_v})

            return db_filter
        except Exception as exe:
            raise DbException("Invalid query string filter."
                              "Error:{}".format(exe),
                              http_code=HTTPStatus.BAD_REQUEST)

    @staticmethod
    def assign_valv(val_v, operator, query_v):
        """
        this method is used to assign val_v and operations
        :param val_v: contains the items in the filter data
        :param operator: operations to be done
        :param query_v: query value
        :return: data  of val_v and operations to be done
        """
        if isinstance(val_v, list):
            if operator in ("$eq", "$cont"):
                operator = "$in"
                val_v = query_v
                return val_v, operator
            elif operator in ("$ne", "$ncont"):
                operator = "$nin"
                val_v = query_v
                return val_v, operator
            val_v = query_v.join(",")
            return val_v, operator
        return val_v, operator

    def create(self, table, indata):
        """
        Add a new entry at database
        :param table: collection or table
        :param indata: content to be added
        :return: database id of the inserted element. Raises a DbException on error
        """
        try:
            with self.lock:
                collection = self.db_mongo[table]
                data = collection.insert_one(indata)
            return data.inserted_id
        except Exception as exe:
            raise DbException(exe)

    def get_one(self, table, q_filter=None, fail_on_empty=True):
        """
        Obtain one entry matching q_filter
        :param table: collection or table
        :param q_filter: Filter
        :param fail_on_empty: If nothing matches filter it returns None unless this flag
        is set tu True, in which case it raises a DbException
        :return: The requested element, or None
        """
        try:
            fail_on_more = True
            db_filter = self._format_filter(q_filter)
            with self.lock:
                collection = self.db_mongo[table]
                if not (fail_on_empty and fail_on_more):
                    return collection.find_one(db_filter)
                rows = collection.find(db_filter)
            if rows.count() == 0:
                if fail_on_empty:
                    raise DbException("Not found any {} with filter='{}'".format(table[:-1],
                                                                                 q_filter),
                                      HTTPStatus.NOT_FOUND)
                return None
            elif rows.count() > 1:
                if fail_on_more:
                    raise DbException("Found more than one {} with filter='{}'".format(table[:-1],
                                                                                       q_filter),
                                      HTTPStatus.CONFLICT)
            return rows[0]
        except Exception as exe:
            raise DbException(exe)

    def get_list(self, table, q_filter=None):
        """
        Obtain a list of entries matching q_filter
        :param table: collection or table
        :param q_filter: Filter
        :return: a list (can be empty) with the found entries. Raises DbException on error
        """
        try:
            result = []
            with self.lock:
                collection = self.db_mongo[table]
                db_filter = self._format_filter(q_filter)
                rows = collection.find(db_filter)
            for row in rows:
                result.append(row)
            return result
        except DbException:
            raise
        except Exception as exe:
            raise DbException(exe)

    def del_one(self, table, q_filter=None, fail_on_empty=True):
        """
        Deletes one entry that matches q_filter
        :param table: collection or table
        :param q_filter: Filter
        :param fail_on_empty: If nothing matches filter it returns '0' deleted unless this flag is
        set tu True, in
        which case it raises a DbException
        :return: Dict with the number of entries deleted
        """
        try:
            with self.lock:
                collection = self.db_mongo[table]
                rows = collection.delete_one(self._format_filter(q_filter))
            if rows.deleted_count == 0:
                if fail_on_empty:
                    raise DbException("Not found any {} with filter='{}'".format(table[:-1],
                                                                                 q_filter),
                                      HTTPStatus.NOT_FOUND)
                return None
            return {"deleted": rows.deleted_count}
        except Exception as exe:
            raise DbException(exe)

    def del_list(self, table, q_filter=None):
        """
        Deletes all entries that match q_filter
        :param table: collection or table
        :param q_filter: Filter
        :return: Dict with the number of entries deleted
        """
        try:
            with self.lock:
                collection = self.db_mongo[table]
                rows = collection.delete_many(self._format_filter(q_filter))
            return {"deleted": rows.deleted_count}
        except DbException:
            raise
        except Exception as exe:
            raise DbException(exe)

    def set_one(self, table, q_filter, update_dict=None):
        """
        Modifies an entry at database
        :param table: collection or table
        :param q_filter: Filter
        :param update_dict: Plain dictionary with the content to be updated. It is a dot separated
        keys and a value
        it raises a DbException
        :return: Dict with the number of entries modified. None if no matching is found.
        """
        try:
            fail_on_empty = True
            push = None
            unset = None
            pull = None
            db_oper = {}
            if update_dict:
                db_oper["$set"] = update_dict
            if unset:
                db_oper["$unset"] = unset
            if pull:
                db_oper["$pull"] = pull
            if push:
                db_oper["$push"] = push
            with self.lock:
                collection = self.db_mongo[table]
                rows = collection.update_one(self._format_filter(q_filter), db_oper)
            if rows.matched_count == 0:
                if fail_on_empty:
                    raise DbException("Not found any {} with filter='{}'".format(table[:-1],
                                                                                 q_filter),
                                      HTTPStatus.NOT_FOUND)
                return None
            return {"modified": rows.modified_count}
        except Exception as exe:
            raise DbException(exe)

    def set_many(self, table, q_filter, update_dict=None):
        """
        Modifies multiple entries at database
        :param table: collection or table
        :param q_filter: Filter
        :param update_dict: Plain dictionary with the content to be updated. It is a dot separated
        keys and a value
        it raises a DbException
                     is appended to the end of the array
        :return: Dict with the number of entries modified. None if no matching is found.
        """
        try:
            fail_on_empty = True
            push = None
            unset = None
            pull = None
            db_oper = {}
            if update_dict:
                db_oper["$set"] = update_dict
            if unset:
                db_oper["$unset"] = unset
            if pull:
                db_oper["$pull"] = pull
            if push:
                db_oper["$push"] = push
            with self.lock:
                collection = self.db_mongo[table]
                rows = collection.update_many(self._format_filter(q_filter), db_oper, upsert=False)
            if rows.matched_count == 0:
                if fail_on_empty:
                    raise DbException("Not found any {} with filter='{}'".format(table[:-1],
                                                                                 q_filter),
                                      HTTPStatus.NOT_FOUND)
                return None
            return {"modified": rows.modified_count}
        except Exception as exe:
            raise DbException(exe)

    def db_disconnect(self):
        """
        this method is used to disconnect the database connect
        :return: type=None
        """
        self.client.close()
