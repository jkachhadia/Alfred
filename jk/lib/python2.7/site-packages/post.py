#!/usr/bin/env python
import cgi

__all__ = ["POST"]

POST = dict()
fs = cgi.FieldStorage()
for k in fs.keys():
    v = fs[k].value
    POST[k] = v
