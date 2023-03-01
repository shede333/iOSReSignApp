#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import subprocess
from pathlib import Path

from .util import plog


def cs_verify(dir_path):
    command = "codesign --verify --verbose '{}'".format(dir_path)
    is_success = True
    try:
        subprocess.check_call(command, shell=True)
    except subprocess.CalledProcessError:
        is_success = False

    return is_success


def cs_info(dir_path, is_verbose=False):
    # codesign --display --verbose --verify
    command = "codesign -d -vv '{}'".format(dir_path)
    is_success = True
    try:
        output = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        is_success = False
        output = str(e)
    if is_verbose:
        print(command)
        print('验证结果：{}'.format(is_success))
        print(output)

    return is_success, output


def run_codesign(dir_path, p12_id, entitlements_path=None):
    # codesign --force --sign <keychain_SHA1> --entitlements <app_path> <entitlements_path>
    command = "codesign --generate-entitlement-der -fs '{}' '{}' ".format(p12_id, dir_path)
    if entitlements_path:
        command += " --entitlements '{}'".format(entitlements_path)
    plog(command)
    # 实际上，这里的内容会输出终端，似乎是codesign的bug
    subprocess.run(command, shell=True, check=True, capture_output=True)


def cs_app(app_path, p12_id, entitlements_path=None):
    app_path = Path(app_path)
    for tmp_file_path in app_path.iterdir():
        if tmp_file_path.name == 'Frameworks':
            for sub_fw_path in tmp_file_path.iterdir():
                if sub_fw_path.suffix == ".framework" or sub_fw_path.suffix == ".dylib":
                    # 重签 framework
                    run_codesign(sub_fw_path, p12_id)
    # 重签 .app本身
    run_codesign(app_path, p12_id, entitlements_path)
