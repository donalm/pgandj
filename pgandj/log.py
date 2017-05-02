#!/usr/bin/env python
# -*- coding: utf-8 -*-

from twisted.python import log

import logging
import sys


def get_logger(name=None):
    logger = logging.getLogger(name)
    logger.setLevel(logging.WARNING)

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.WARNING)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s - %(filename)s:%(lineno)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    observer = log.PythonLoggingObserver()
    observer.start()
    return logger
