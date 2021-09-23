#!/usr/bin/env python3
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'

重签名.app文件



"""

import json
import re
import shutil
import subprocess
import tempfile
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from iosappinfoparser import InfoPlistModel
from iosappinfoparser.info_plist import change_app_display_name
from mobileprovision import MobileProvisionModel
from mobileprovision import util as mp_util

from . import codesign
from . import security
from .util import plog


class ResignException(Exception):
    pass


def zip_payload(payload_path, ipa_path):
    command = "zip -r '{}' 'Payload'".format(Path(ipa_path).resolve(), payload_path)
    plog(command)
    subprocess.run(command, shell=True, check=True, capture_output=True, cwd=payload_path.parent)


def safe_ipa_path(dst_dir, name_prefix, name_suffix=None):
    """
    获取ipa文件路径，保证此路径不指向任何文件；
    :param dst_dir: ipa文件存放的目录
    :param name_prefix: 文件名前缀（不包含扩展名）
    :param name_suffix: （可选）文件名后缀
    :return: 路径对象
    """
    if name_suffix:
        pure_name = "{}-{}".format(name_prefix, name_suffix)
    else:
        pure_name = name_prefix
    dst_dir = Path(dst_dir).resolve()
    name_index = 0
    while True:
        if name_index > 0:
            ipa_name = "{}-{}.ipa".format(pure_name, name_index)
        else:
            ipa_name = "{}.ipa".format(pure_name)
        ipa_path = dst_dir.joinpath(ipa_name)
        if not ipa_path.is_file():
            break
        name_index += 1
    return ipa_path


def parse_mobileprovision(mobileprovision_info):
    """
    解析出mobileprovision信息
    :param mobileprovision_info: mobileprovision文件路径,或者Name属性,或者UUID属性
    :return:
    """
    if mobileprovision_info.endswith(mp_util.MP_EXT_NAME):
        return MobileProvisionModel(mobileprovision_info)

    result = re.match(r"^([a-zA-Z]+):(.+)$", mobileprovision_info.strip())
    if result:
        matched_list = []
        p_name, p_value = map(lambda x: x.strip(), result.groups())
        for mp_path in mp_util.mp_path_in_dir(mp_util.MP_ROOT_PATH):
            mp_model = MobileProvisionModel(mp_path)
            if mp_model[p_name] == p_value:
                matched_list.append(mp_model)
        # 按照创建时间，从新到旧
        matched_list = sorted(matched_list, key=lambda x: x.creation_timestamp, reverse=True)
        if matched_list:
            used_model = matched_list[0]
            plog("\n根据'{}: {}', 使用mobileprovision：{}".format(p_name, p_value, used_model.file_path))
            return used_model
        else:
            e_info1 = "根据'{}: {}', 无法找到对应的mobileprovision文件".format(p_name, p_value)
            e_info2 = "查找路径：{}".format(mp_util.MP_ROOT_PATH)
            raise ResignException("\n".join([e_info1, e_info2]))
    else:
        raise ResignException("无法识别mobileprovision:", mobileprovision_info)


def resign(app_path, mobileprovision_info, sign=None, entitlements_path=None, output_ipa_path=None,
           is_show_ipa=False, re_suffix_name=None, set_app_name=None, set_app_version=None,
           set_app_infos=None):
    app_path = Path(app_path)

    # 处理冲突参数
    if output_ipa_path and re_suffix_name:
        raise ResignException("不能同时设置： output_ipa_path 与 re_suffix_name ")

    # 解析mobileprovision文件里的有效信息
    mp_model = parse_mobileprovision(mobileprovision_info)
    if not mp_model.date_is_valid():
        raise ResignException("mobileprovision 已过期")
    # 查找p12文件的签名ID：sha1
    id_model_list = security.security_find_identity()
    valid_sha1_set = set((tmp_model.sha1 for tmp_model in id_model_list if tmp_model.is_valid))
    if not valid_sha1_set:
        raise ResignException("钥匙串里 不存在有效的签名证书sign!")
    if sign:
        invalid_sha1_set = set(
            (tmp_model.sha1 for tmp_model in id_model_list if not tmp_model.is_valid))
        if sign in invalid_sha1_set:
            raise ResignException("sign对应于 钥匙串 里的证书，无效！")
        if sign not in valid_sha1_set:
            raise ResignException("钥匙串 里的有效证书，不存在此sign: {}".format(sign))
    else:
        # 使用mobileprovision里第一个有效的证书
        for tmp_cer in mp_model.developer_certificates:
            if tmp_cer.sha1 in valid_sha1_set:
                sign = tmp_cer.sha1
                plog("\n* auto find, sign使用: {}, {}".format(sign, tmp_cer.common_name))
                break
        else:
            raise ResignException("钥匙串里，不存在有效的mobileprovision里的cer证书")

    # 创建临时工作目录，将.app文件解压到此处，并重签名、打包操作
    with tempfile.TemporaryDirectory() as temp_dir_path:
        ws_dir_path = Path(temp_dir_path)
        plog("\n临时工作目录:", ws_dir_path)
        if not entitlements_path:
            plog("\n* 从mobileprovision文件里提取 entitlements.plist文件")
            entitlements_path = ws_dir_path.joinpath("entitlements.plist")
            mp_model.export_entitlements_file(entitlements_path)

        payload_path = ws_dir_path.joinpath("Payload")
        ext_name = app_path.suffix.lower()
        if ext_name == ".ipa":
            # 解压ipa文到 工作目录下
            command = "unzip -oqq '{}' -d '{}'".format(app_path, ws_dir_path)
            plog("\n" + command)
            subprocess.check_call(command, shell=True)
            assert payload_path.is_dir()
            all_sub_app = list(payload_path.glob("*.app"))
            assert len(all_sub_app) == 1
            dst_app_path = all_sub_app[0]
        elif ext_name == ".app":
            # 创建Payload目录
            payload_path.mkdir()
            dst_app_path = payload_path.joinpath(app_path.name)
            # 复制.app文件到此处
            shutil.copytree(app_path, dst_app_path)
        else:
            raise ResignException("不支持此文件类型: {}".format(app_path))
        plog("dst_app_path: {}".format(dst_app_path))

        # 检测App的BundleID 与 mobileprovision里的BundleID 是否一致
        info_model = InfoPlistModel(dst_app_path.joinpath("Info.plist"))
        inner_bundle_id = info_model.bundle_id
        mp_app_id = mp_model.app_id()
        if inner_bundle_id != mp_app_id:
            # 重新设置App的BundleID
            plog("\n* 修改 BundleID from '{}', to '{}'".format(inner_bundle_id, mp_app_id))
            info_model.bundle_id = mp_app_id
        if set_app_infos:
            app_infos = map(lambda x: tuple(x.split(":")), set_app_infos.split(","))
            for tmp_key, tmp_value in app_infos:
                plog("\n* 修改 App Info.plist {} to '{}'".format(tmp_key, tmp_value))
                info_model.set_value(tmp_key.strip(), tmp_value.strip())
        if set_app_name:
            plog("\n* 修改 App Name to '{}'".format(set_app_name))
            change_app_display_name(dst_app_path, set_app_name)
        if set_app_version:
            plog("\n* 修改 App Version to '{}'".format(set_app_version))
            info_model.app_version = set_app_version

        # 嵌入mobileprovision文件
        dst_mp_path = dst_app_path.joinpath("embedded.mobileprovision")
        src_mp_path = mp_model.file_path
        if src_mp_path and src_mp_path.is_file():
            if not dst_mp_path.is_file():
                plog("\ncopy embedded.mobileprovision文件：{}".format(src_mp_path))
                shutil.copy(src_mp_path, dst_mp_path)
            elif not src_mp_path.samefile(dst_mp_path):
                plog("\n替换 embedded.mobileprovision文件：{}".format(src_mp_path))
                shutil.copy(src_mp_path, dst_mp_path)

        # 给MachO可执行文件加上 执行权限
        command = "chmod +x '{}'".format(info_model.exec_path)
        plog("\n" + command)
        subprocess.check_call(command, shell=True)

        # 删除extension和Watch，个人证书没法签名这些东西
        plugins_path = dst_app_path.joinpath("PlugIns")
        watch_path = dst_app_path.joinpath("Watch")
        for tmp_path in [plugins_path, watch_path]:
            if tmp_path.is_dir():
                plog("- 删除：{}".format(tmp_path))
                shutil.rmtree(tmp_path)

        plog("\n开始 重签名resign App+Framework：")
        codesign.cs_app(dst_app_path, sign, entitlements_path)
        plog("\n验证并显示.app的签名信息:")
        codesign.cs_info(dst_app_path, is_verbose=True)

        plog("\n开始 zip *.app to *.ipa")
        if output_ipa_path:
            output_ipa_path = Path(output_ipa_path).resolve()
        else:
            output_ipa_path = safe_ipa_path(app_path.parent, app_path.stem, re_suffix_name)
        zip_payload(payload_path, output_ipa_path)

    plog("\n* 重签名resign 成功！\nipa产物: {}".format(output_ipa_path))
    if is_show_ipa:
        command = "open '{}'".format(output_ipa_path.parent)
        subprocess.call(command, shell=True)
    print('', flush=True)
    return output_ipa_path


def batch_resign(json_path):
    file_content = Path(json_path).read_bytes()
    info_obj = json.loads(file_content)
    config_list = info_obj['list']

    executor = ProcessPoolExecutor()
    task_list = [executor.submit(resign, **params) for params in config_list]
    print('wait task finish...')
    result_list = []
    for tmp_task in as_completed(task_list):
        try:
            tmp_result = tmp_task.result()
            result_list.append(tmp_result)
        except ResignException as e:
            print(e)
        except Exception as e:
            print(e)
    print(f'all task finish!\n{result_list}\n\n')
