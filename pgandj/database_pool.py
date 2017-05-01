#!/usr/bin/env python

from . import database_driver
psycopg2 = database_driver.import_driver()

import json
from txpostgres import txpostgres
from txpostgres.reconnection import DeadConnectionDetector
from twisted.python.modules import getModule
from twisted.python import util
from twisted.internet import reactor, task, defer


class Pool(txpostgres.ConnectionPool):

    def __init__(self, credentials):
        self.status_df = None
        args = tuple()

        txpostgres.ConnectionPool.__init__(self,
                                           None,
                                           *args,
                                           connection_factory=psycopg2.extras.NamedTupleConnection,
                                           **credentials)

    def start(self):
        if not self.status_df:
            self.status_df = txpostgres.ConnectionPool.start(self)

        """
        Everyone who calls 'start' gets their own deferred
        Probably not important, but it makes the code more
        predictable
        """
        df = defer.Deferred()

        def cb(result):
            df.callback(result)
            return result

        self.status_df.addCallback(cb)
        return df


