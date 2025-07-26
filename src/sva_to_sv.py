import enum
from jinja2 import Template
import json
import os
import re

from gen_network import nfa_to_json


def generate_file(tar_fpath, tpl_fpath, **params):
    with open(tpl_fpath, 'r', encoding='utf-8') as fp:
        tpl = Template(fp.read())
    with open(tar_fpath, 'w', encoding='utf-8') as fp:
        fp.write(tpl.render(**params))

def dfa_to_sv(dfa_json_path : str, output_mod_path : str, output_tb_path : str, module_name : str,\
            sv_tpl_path : str, tb_tpl_path : str):
    """将 dfa json 中的文件进行一定的处理后转换为 sv"""
    with open(dfa_json_path,"r",encoding = "utf-8") as fp:
        sva_dict = json.load(fp)

        # 收集 label 需要哪些 signal
        sva_all_input_signals = set()
        for _,value0 in sva_dict.items():
            for _, value1 in value0.items():
                value = []
                for label in value1:
                    value += [re.sub("!","",x) for x in label]
                sva_all_input_signals |= set(value)
        sva_all_input_signals = list(sva_all_input_signals)

        params = {"module_name":module_name,"sva_all_input_signals":sva_all_input_signals,"sva_dict":sva_dict,\
                "enumerate":enumerate, "len":len, "range":range}
        generate_file(output_mod_path, sv_tpl_path, **params)
        generate_file(output_tb_path, tb_tpl_path, **params)

def test(min_test, max_test):
    try:
        os.mkdir('./output/gen')
    except:
        pass
    for i in range(min_test, max_test+1):
        dfa_to_sv(f"./output/json/test{i}.sv.dfa.json",f"./output/gen/test{i}.sv",f"./output/gen/test{i}_tb.sv",i)
if __name__ == '__main__':
    min_test = 6
    max_test = 6
    test(min_test, max_test)