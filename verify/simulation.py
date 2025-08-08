import sys

from src import gen_network
# sys.path.append("./src")

import os.path
import os
# 用于远程 ssh 访问虚拟机
import paramiko

import src.sva_synth as sva_synth
import src.nfa_run as nfa_run

DISPLAY = True
#       0                   1                   2
#       3                   4                   5
#       6

a = [   1,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,
        0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,
        1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,
        1,0,1,0,1,0,1,0
        ]
b = [   1,1,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,
        0,1,0,1,0,0,0,0,0,1,1,1,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0
        ]
c = [   1,1,1,1,1,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1
        ]
d = [   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1
        ]


def get_inputlist():
    """获取输入列表"""
    input_lists_ = []
    for (i,_) in enumerate(a):
        input_list = []
        if a[i]:
            input_list.append('a')
        else :
            input_list.append('!a')
        if b[i]:
            input_list.append('b')
        else :
            input_list.append('!b')
        if c[i]:
            input_list.append('c')
        else :
            input_list.append('!c')
        if d[i]:
            input_list.append('d')
        else :
            input_list.append('!d')
        input_lists_.append(input_list.copy())
    return input_lists_
# input_lists = get_inputlist()

def log_parser(log_ori : list) -> dict: # {time : {answer : times}}
    """解析打印的 log"""
    # 去除空白行和注释开头的行
    remove_commond_and_blank = [x for x in log_ori if x != '' and not x.startswith('#')]
    ret_val = {}
    time = None
    for elem in remove_commond_and_blank:
        if "run times" in elem:
            time = int(elem.split("=")[-1].strip())

        if time == None:
            continue
        if time not in ret_val:
            ret_val[time] = {"finish":0,"error":0}
        elif "finish" in elem:
            ret_val[time]["finish"] += 1
        elif "error" in elem:
            ret_val[time]["error"] += 1
    return ret_val
def check_log(log0 : list | str, log1: list | str) -> bool:
    if isinstance(log0, str):
        with open(log0, 'r', encoding='utf-8') as f:
            nfa_log_ori = f.readlines()
    else:
        nfa_log_ori = log0
    if isinstance(log1, str):
        with open(log1, 'r', encoding='utf-8') as f:
            sim_log_ori = f.readlines()
    else:
        sim_log_ori = log1
    
    parsed_nfa_log = log_parser(nfa_log_ori)
    parsed_sim_log = log_parser(sim_log_ori)
    no_error = True
    for key, value in parsed_nfa_log.items():
        assert key in parsed_sim_log
        no_error &= value["finish"] == parsed_sim_log[key]["finish"]
        no_error &= value["error"]  == parsed_sim_log[key]["error"]
        if not no_error:
            print(f"Dont Match At time = {key} : {log0} {log1}")
            break
    return no_error

def sim_place_hold(input_file):
    log = ""
    return log






            # check_answer &= check_log(ori_sim_log_path, nfa_log_path)
            # if check_answer:
            #     print(f"[Success] nfa passed test {test_file_name}")
            # else:
            #     sys.exit(-1)

            # check_answer &= check_log(ori_sim_log_path, dfa_log_path)
            # if check_answer:
            #     print(f"[Success] dfa passed test {test_file_name}")
            # else:
            #     sys.exit(-1)

            # check_answer &= check_log(ori_sim_log_path, sv_sim_log_path)
            # if check_answer:
            #     print(f"[Success] sv passed test {test_file_name}")
            # else:
            #     sys.exit(-1)


