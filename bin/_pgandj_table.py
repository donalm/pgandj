#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import time
import argparse
from twisted.python import log
from twisted.internet import reactor

import pgandj

logger = pgandj.get_logger()


def eb(f):
    logger.error(f.getBriefTraceback())

def stop(schema, args, t):
    print time.time() - t
    reactor.stop()
    data = json.dumps(schema, indent=4, sort_keys=False, separators=(',', ': '))

    next_id = 0
    outfile = None
    try:
        if not args.outfile:
            outfile = os.path.realpath("./%s_%03d.json" % (args.database, next_id,))
            while  os.path.exists(outfile):
                next_id += 1
                outfile = os.path.realpath("./%s_%03d.json" % (args.database, next_id,))
        else:
            outfile = os.path.realpath(args.outfile)
    except Exception as e:
        print("Failed to write json data to '%s': %s" % (outfile, e,))
        sys.exit(1)

    if os.path.exists(outfile):
        overwrite = raw_input("File '%s' exists. Replace? \n(Y/N) " % (args.outfile,))
        if overwrite.lower() != 'y':
            return

    try:
        fh = open(outfile, "w")
        fh.write(data)
        fh.close()
        print("JSON file created at " + outfile)
    except Exception as e:
        print("Failed to write json data to '%s': %s" % (outfile, e,))
        sys.exit(1)

def begin(args):
    t = time.time()
    inspect = pgandj.Inspect(args)
    df = inspect.table(args.table)
    df.addErrback(eb)
    df.addBoth(stop, args, t)

def main():
    parser = argparse.ArgumentParser(
            description='Parse a PostgreSQL database schema into JSON.',
            prog='pgandj'
        )

    parser.add_argument('database', metavar="DATABASE", type=str,
                        help='The name of the database')
    parser.add_argument('table', metavar="TABLE", type=str,
                        help='The name of the table')
    parser.add_argument('-o', metavar="FILEPATH", type=str,
                        help='A path to write the JSON file', dest='outfile')
    parser.add_argument('-u', metavar="USERNAME", type=str,
                        help='postgres username', dest='username')
    parser.add_argument('-w', metavar="PASSWORD", type=str,
                        help='postgres password', dest='password')
    parser.add_argument('--host', metavar="HOST", type=str,
                        default='127.0.0.1', dest='host',
                        help='postgres server hostname')
    parser.add_argument('-p', metavar="PORT", type=int,
                        default=5432, dest='port',
                        help='postgres server port')

    args = parser.parse_args()

    reactor.callWhenRunning(begin, args)
    reactor.run()


if __name__ == '__main__':
    main()
