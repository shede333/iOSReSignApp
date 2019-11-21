#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import argparse

from . import util
from .resign import resign


def parse_arg():
    """解析命令行的输入的参数"""
    parser = argparse.ArgumentParser("App文件重签名")

    parser.set_defaults(func=resign)
    parser.add_argument("app_path", help=".app文件路径")
    parser.add_argument("-m", "--mobileprovision", dest="mobileprovision_path", required=True,
                        help="mobileprovision文件路径")
    parser.add_argument("-s", "--sign", help="(可选)签名证书的 SHA1或者name")
    parser.add_argument("-e", "--entitlements-path", help="(可选)entitlements环境plist文件")
    parser.add_argument("-q", "--quiet", action='store_true', help="是否隐藏print信息")
    parser.add_argument("--show-ipa", dest="is_show_ipa", action='store_true',
                        help="是否打开Finder显示最终的ipa文件")

    args = parser.parse_args()
    return args


def main():
    params = parse_arg()
    f_params = params.__dict__.copy()

    util.IS_QUIET = params.quiet
    del f_params["quiet"]  # 删除无用参数

    del f_params["func"]  # 删除无用参数
    params.func(**f_params)  # 执行命令对应的函数


if __name__ == '__main__':
    main()
