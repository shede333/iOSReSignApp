#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import subprocess
from pathlib import Path


class InfoPlistModel(object):
    """.App文件里的 Info.plist信息model"""

    def __init__(self, file_path):
        self.file_path = file_path

    def _run_command(self, sub_command):
        command = '/usr/libexec/PlistBuddy -c "{}" "{}"'.format(sub_command, self.file_path)
        output = subprocess.check_output(command, shell=True, text=True)
        return output and output.strip()

    @property
    def bundle_id(self):
        return self._run_command("print CFBundleIdentifier")

    @bundle_id.setter
    def bundle_id(self, value):
        command = "set :CFBundleIdentifier {}".format(value)
        self._run_command(command)

    @property
    def exec_name(self):
        return self._run_command("print CFBundleExecutable")

    @property
    def exec_path(self):
        return Path(self.file_path).with_name(self.exec_name)
