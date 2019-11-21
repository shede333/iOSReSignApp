#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

IS_QUIET = False


def plog(*texts):
    if IS_QUIET:
        return
    print(*texts)
