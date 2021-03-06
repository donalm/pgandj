#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time

from twisted.python import log
from twisted.internet import defer
from collections import OrderedDict
from collections import namedtuple

from . import database_pool
from . import metaqueries
from . import log



class Inspect(object):
    tbltpl = namedtuple('table', ['table_name'])
    logger = log.get_logger()
    def __init__(self, database, port=5432, host='127.0.0.1', password=None, user=None):
        credentials = {
            "port": port,
            "host": host,
            "password": password,
            "user": user,
            "database": database
        }
        self.pool = database_pool.Pool(credentials)
        self.ready = self.pool.start()
        self.result = {}

    def eb(self, f):
        self.logger.error(f.getBriefTraceback())

    def database(self):
        return self.ready.addCallback(self.get_tables)

    def table(self, table):
        df = self.ready.addCallback(self.get_tables)
        df.addCallback(self.return_table_data, table)
        return df

    def return_table_data(self, result, table):
        return result[table]

    def get_tables(self, *args):
        self.logger.debug("get_tables")
        query = metaqueries.queries["list_tables"]
        df = self.pool.runQuery(query)
        df.addCallback(self.parse_tables)
        df.addCallback(self.return_result)
        return df

    def parse_tables(self, tables):
        dfs = []
        for table in tables:
            table_name = table.table_name
            self.result[table_name] = {"fields":OrderedDict(),
                                  "indices":OrderedDict()}
            df = self.get_columns(table_name)
            df.addCallback(self.parse_columns, table_name)
            df.addCallback(self.get_indices)
            df.addCallback(self.parse_indices, table_name)
            df.addCallback(self.get_foreign_keys)
            df.addCallback(self.parse_foreign_keys)
            dfs.append(df)

        dfl = defer.DeferredList(dfs)
        return dfl

    def get_columns(self, table_name, *args):
        self.logger.debug("get_columns")
        query = metaqueries.queries["list_table_columns"]
        return self.pool.runQuery(query, (table_name,))

    def parse_columns(self, results, table_name):
        nullable = {"YES":True, "NO":False}
        for column in results:
            val = {'name': column.column_name,
                   'type': column.data_type,
                   'nullable': nullable[column.is_nullable],
                   'default': column.column_default,
                   'references_foreign_key': None,
                   'referenced_by_foreign_key': None,
                   'leads_index': False}
            self.result[table_name]["fields"][column.column_name] = val

        return table_name

    def get_indices(self, table_name, *args):
        self.logger.debug("get_indices: %s" % (table_name,))
        query = metaqueries.queries["list_table_indices"]
        return self.pool.runQuery(query, (table_name,))

    def parse_indices(self, results, table_name):
        for result in results:
            leader = result.column_names[0]
            self.result[table_name]["fields"][leader]["leads_index"] = True
            self.result[table_name]["indices"][result.index_name] = {"fields": result.column_names, "unique":result.unique}
            if len(result.column_names) == 1 and result.unique:
                self.result[table_name]["fields"][leader]["unique"] = True
        return table_name

    def get_foreign_keys(self, table_name):
        self.logger.debug("get_foreign_keys")
        query = metaqueries.queries["list_foreign_keys"]
        return self.pool.runQuery(query, (table_name,))

    def parse_foreign_keys(self, results):
        for result in results:
            self.result[result.table_name]["fields"][result.column_name]["references_foreign_key"] = (result.foreign_table_name, result.foreign_column_name,)
            try:
                self.result[result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"].append((result.table_name, result.column_name,))
            except Exception, e:
                self.result[result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"] = [(result.table_name, result.column_name,)]

    def return_result(self, _):
        return self.result
