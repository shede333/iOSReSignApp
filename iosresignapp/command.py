#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import argparse

from . import util
from .resign import resign, batch_resign


def parse_arg():
    """解析命令行的输入的参数"""
    parser = argparse.ArgumentParser("对'.app/.ipa'文件，进行重签名")
    subparsers = parser.add_subparsers(help="支持的命令如下：")

    single_parser = subparsers.add_parser("resign", help="重签单个文件")
    single_parser.set_defaults(func=resign)  # 对应的函数

    single_parser.add_argument("app_path", help="'.app/.ipa'文件路径")
    single_parser.add_argument("-m", "--mobileprovision", dest="mobileprovision_info",
                               required=True,
                               help="mobileprovision文件路径,或者Name属性,或者UUID属性，同时会根据mp文件内的appID来修改app的BundleID")
    single_parser.add_argument("-s", "--sign", help="(可选)签名证书的 SHA1或者name")
    single_parser.add_argument("-e", "--entitlements-path", help="(可选)entitlements环境plist文件")
    single_parser.add_argument("--re-suffix-name", default="resign",
                               help="(可选)重签名后的文件名后缀，如果设置了'--output-ipa-path'，则此选项无效；默认为'resign'")
    single_parser.add_argument("-o", "--output-ipa-path", help="(可选)ipa文件输出路径，不传此值则输出到.app同级目录下")
    single_parser.add_argument("-q", "--quiet", action='store_true', help="是否隐藏print信息")
    single_parser.add_argument("-S", "--show-ipa", dest="is_show_ipa", action='store_true',
                               help="是否打开Finder显示最终的ipa文件")
    single_parser.add_argument("--set-app-name", required=False, help="(可选)修改App的显示名称")
    single_parser.add_argument("--set-app-version", required=False, help="(可选)修改App的版本号")
    single_parser.add_argument("--set-app-infos", required=False,
                               help="(可选)修改App的Info内的信息，多条信息以逗号分割，例如：'CFBundleVersion:1.0, CFBundleDisplayName:HelloApp'")

    batch_parser = subparsers.add_parser("batch_resign", help="批量重签")
    batch_parser.set_defaults(func=batch_resign)
    batch_parser.add_argument("json_path", help="重签信息json文件的路径")

    args = parser.parse_args()
    return args


def main():
    params = parse_arg()
    f_params = params.__dict__.copy()

    if "quiet" in f_params:
        util.IS_QUIET = params.quiet
        del f_params["quiet"]  # 删除无用参数

    del f_params["func"]  # 删除无用参数
    params.func(**f_params)  # 执行命令对应的函数


if __name__ == '__main__':
    main()
