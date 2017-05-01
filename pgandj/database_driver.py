#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Find out if we're running in a pypy session, in which case we need to
use the cffi version of psycopg2
"""
import platform

def import_driver():
    pypy = "PyPy" == platform.python_implementation()
    if pypy:
        from psycopg2cffi import compat
        compat.register()

    import psycopg2
    import psycopg2.extras
    import psycopg2.extensions
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
    psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)
    return psycopg2
