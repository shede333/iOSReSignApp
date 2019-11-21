#!/usr/bin/env python3
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'

重签名.app文件



"""

import shutil
import subprocess
import tempfile
from pathlib import Path

from mobileprovision import MobileProvisionModel

from . import codesign
from . import security
from . import util
from .util import plog


def zip_payload(payload_path, ipa_path):
    command = "zip -r '{}' 'Payload'".format(ipa_path, payload_path)
    plog(command)
    if util.IS_QUIET:
        subprocess.check_output(command, shell=True, cwd=payload_path.parent)
    else:
        subprocess.check_call(command, shell=True, cwd=payload_path.parent)


def safe_ipa_path(name_prefix, dst_dir):
    """
    获取ipa文件路径，保证此路径不指向任何文件；
    :param name_prefix: 文件名前缀（不包含扩展名）
    :param dst_dir: ipa文件存放的目录
    :return: 路径对象
    """
    name_index = 0
    while True:
        if name_index > 0:
            ipa_name = "{}-{}.ipa".format(name_prefix, name_index)
        else:
            ipa_name = "{}.ipa".format(name_prefix)
        ipa_path = Path(dst_dir).joinpath(ipa_name)
        if not ipa_path.is_file():
            break
        name_index += 1
    return ipa_path


def resign(app_path, mobileprovision_path, sign=None, entitlements_path=None, is_show_ipa=False):
    app_path = Path(app_path)

    mp_model = MobileProvisionModel(mobileprovision_path)
    id_model_list = security.security_find_identity()
    valid_sha1_set = set((tmp_model.sha1 for tmp_model in id_model_list if tmp_model.is_valid))
    if not valid_sha1_set:
        raise Exception("钥匙串里 不存在有效的签名证书sign!")
    if sign:
        invalid_sha1_set = set(
            (tmp_model.sha1 for tmp_model in id_model_list if not tmp_model.is_valid))
        if sign in invalid_sha1_set:
            raise Exception("sign对应于 钥匙串 里的证书，无效！")
        if sign not in valid_sha1_set:
            raise Exception("钥匙串 里的有效证书，不存在此sign: {}".format(sign))
    else:
        # 使用mobileprovision里第一个有效的证书
        for tmp_cer in mp_model.developer_certificates:
            if tmp_cer.sha1 in valid_sha1_set:
                sign = tmp_cer.sha1
                plog("\n* auto find, sign使用: {}, {}".format(sign, tmp_cer.common_name))
                break
        else:
            raise Exception("钥匙串里，不存在有效的mobileprovision里的cer证书")

    with tempfile.TemporaryDirectory() as temp_dir_path:
        ws_dir_path = Path(temp_dir_path)
        plog("临时工作目录:", ws_dir_path)
        if not entitlements_path:
            # 从mobileprovision文件里提取 entitlements.plist文件
            entitlements_path = ws_dir_path.joinpath("entitlements.plist")
            mp_model.export_entitlements_file(entitlements_path)
            plog("\n* 从mobileprovision文件里提取 entitlements.plist文件")
        # 创建Payload目录
        payload_path = ws_dir_path.joinpath("Payload")
        payload_path.mkdir()
        dst_app_path = payload_path.joinpath(app_path.name)
        # 赋值.app文件
        shutil.copytree(app_path, dst_app_path)
        # 嵌入mobileprovision文件
        dst_mp_path = dst_app_path.joinpath("embedded.mobileprovision")
        src_mp_path = Path(mobileprovision_path)
        if src_mp_path and src_mp_path.is_file() and (dst_mp_path != src_mp_path):
            shutil.copy(src_mp_path, dst_mp_path)

        plog("\n开始 重签名resign：")
        codesign.cs_app(dst_app_path, entitlements_path)

        plog("\n开始 zip *.app to *.ipa")
        ipa_path = safe_ipa_path(app_path.stem, app_path.parent)
        zip_payload(payload_path, ipa_path)

    plog("\n* 重签名resign 成功！\nipa产物: {}".format(ipa_path))
    if is_show_ipa:
        command = "open '{}'".format(ipa_path.parent)
        subprocess.call(command, shell=True)
