#!/usr/bin/env python
from get import GET
from post import POST

__all__ = ["REQUEST"]

REQUEST = dict()
REQUEST.update(GET)
REQUEST.update(POST)
