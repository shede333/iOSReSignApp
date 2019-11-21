#!/usr/bin/env python
# _*_ coding:UTF-8 _*_
"""
__author__ = 'shede333'
"""

import re
import subprocess
from collections import namedtuple

SecIDModel = namedtuple("SecIDModel", "sha1, name, is_valid")


def sec_id_model_list(text, is_valid):
    model_list = []
    if not text:
        return model_list
    pattern = re.compile(r'^\d+\)\s+([0-9A-F]+)\s+"([^"]+)"$')
    for line_text in text.strip().splitlines():
        result = pattern.match(line_text.strip())
        if result:
            sha1, name = result.groups()
            model_list.append(SecIDModel(sha1, name, is_valid))
    return model_list


def security_find_identity(policy="codesigning", is_only_valid=False):
    command = "security find-identity"
    if is_only_valid:
        command += " -v"
    if policy:
        command += " -p '{}'".format(policy)

    output = subprocess.check_output(command, shell=True, text=True)

    if is_only_valid:
        return sec_id_model_list(output, is_valid=True)

    sep_key = "Valid identities only"
    split_results = output.split(sep_key, maxsplit=1)
    all_id_text = split_results[0]
    if len(split_results) == 2:
        valid_id_text = split_results[1]
    else:
        valid_id_text = None
    all_model_list = sec_id_model_list(all_id_text, is_valid=False)
    valid_model_list = sec_id_model_list(valid_id_text, is_valid=True)
    valid_sha1_sets = set((tmp_model.sha1 for tmp_model in valid_model_list))

    final_list = []
    for tmp_model in all_model_list:
        final_list.append(tmp_model._replace(is_valid=(tmp_model.sha1 in valid_sha1_sets)))

    return final_list
