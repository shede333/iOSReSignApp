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
        try:
            output = subprocess.check_output(command, shell=True, text=True)
        except subprocess.CalledProcessError:
            output = None
        return output and output.strip()

    def get_value(self, key):
        return self._run_command("print {}".format(key))

    def set_value(self, key, value):
        self._run_command("set :{} {}".format(key, value))

    @property
    def bundle_id(self):
        return self.get_value("CFBundleIdentifier")

    @bundle_id.setter
    def bundle_id(self, value):
        self.set_value("CFBundleIdentifier", value)

    @property
    def exec_name(self):
        return self.get_value("CFBundleExecutable")

    @property
    def exec_path(self):
        return Path(self.file_path).with_name(self.exec_name)

    @property
    def app_display_name(self):
        return self.get_value("CFBundleDisplayName")

    @app_display_name.setter
    def app_display_name(self, value):
        self.set_value("CFBundleDisplayName", value)

    @property
    def bundle_name(self):
        return self.get_value("CFBundleName")

    @bundle_name.setter
    def bundle_name(self, value):
        self.set_value("CFBundleName", value)

    @property
    def app_version(self):
        return self.get_value("CFBundleShortVersionString")

    @app_version.setter
    def app_version(self, value):
        self.set_value("CFBundleShortVersionString", value)

    @property
    def build_version(self):
        return self.get_value("CFBundleVersion")

    @build_version.setter
    def build_version(self, value):
        self.set_value("CFBundleVersion", value)
