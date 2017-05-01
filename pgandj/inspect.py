#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.python import log
from twisted.internet import defer
from collections import OrderedDict

from . import database_pool
from . import metaqueries
from . import log


logger = log.get_logger()

class Inspect(object):
    def __init__(self, args):
        credentials = {
            "port": args.port,
            "host": args.host,
            "password": args.password,
            "user": args.username,
            "database": args.database
        }
        self.pool = database_pool.Pool(credentials)
        self.ready = self.pool.start()
        self.result = {}

    def database(self):
        return self.ready.addCallback(self.get_tables)

    def get_tables(self, *args):
        logger.error("get_tables")
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
            df.addCallback(self.show_columns, table_name)
            df.addCallback(self.get_indices)
            df.addCallback(self.parse_indices, table_name)
            df.addCallback(self.get_foreign_keys)
            df.addCallback(self.parse_foreign_keys)
            dfs.append(df)

        dfl = defer.DeferredList(dfs)
        return dfl

    def get_columns(self, table_name, *args):
        logger.error("get_columns")
        query = metaqueries.queries["list_table_columns"]
        return self.pool.runQuery(query, (table_name,))

    def show_columns(self, results, table_name):
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
        logger.error("get_indices: %s" % (table_name,))
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
        logger.error("get_foreign_keys")
        query = metaqueries.queries["list_foreign_keys"]
        print(table_name)
        print(query)
        return self.pool.runQuery(query, (table_name,))

    def parse_foreign_keys(self, results):
        print(results)
        for result in results:
            self.result[result.table_name]["fields"][result.column_name]["references_foreign_key"] = (result.foreign_table_name, result.foreign_column_name,)
            try:
                self.result[result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"].append((result.table_name, result.column_name,))
            except Exception, e:
                self.result[result.foreign_table_name]["fields"][result.foreign_column_name]["referenced_by_foreign_key"] = [(result.table_name, result.column_name,)]

    def return_result(self, _):
        return self.result
