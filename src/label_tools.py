
import re
from functools import reduce
from copy import deepcopy

from networkx import complement


def clear_excl_mark_of_set(label : set) -> set:
    """"去除集合中元素里面多余的感叹号"""
    label_temp = set()
    for seq in label:
        cnt = 0
        for alph in seq:
            if alph == '!':
                cnt +=1
        cnt = int(cnt / 2) * 2
        label_temp |= set([seq[cnt:]])
        assert seq[cnt:] != ""
    return label_temp

# input inp 集合
# output out 集合构成的列表
def get_sub_sets(inp) -> list:
    """获得输入集合的全部子集"""
    # print(f"inp = {inp}")
    out = [inp]
    if len(inp) > 1:
        for member in inp:
            out += get_sub_sets(inp - set([member]))
    return out

def get_sub_sets_with_inv(inp_ : set) -> list:
    """
    要求输入集合中的元素不存在 "!"
    假设输入为 {"a", "b", "c",....}, 则输出为 {"a","!a","b","!b","c","!c",...} 构成的集合
    且此集合不会同时出现 a !a, b !b, c !c 等情况
    """
    # 去除 inp 中元素的 "!", 同时去重
    inp = set([re.sub("!","",x) for x in inp_])
    sub_sets = get_sub_sets(inp)
    out = []
    for sub_set in sub_sets:
        sub_set_temp0 = deepcopy(sub_set)
        for elem in inp:
            if elem not in sub_set:
                sub_set_temp0.add("!" + elem)
        out += [sub_set_temp0]
        sub_set_temp1 = set()
        for _,elem in enumerate(list(sub_set_temp0)):
            sub_set_temp1.add("!" + elem)
            
        out += [sub_set_temp1]
    out = [x for x in out if len(x) == len(inp)]

    return out

def get_compl(sets : list):
    """将 sets 的全集求出后从中去除 sets 随后获得最大子集"""
    def _or(set_a, set_b):
        set_c = set_a | set_b
        return set_c
    befor_univ_set = reduce(_or, sets)
    befor_univ_set = set([re.sub("!","",x) for x in befor_univ_set])
    universal_sets = get_sub_sets_with_inv(befor_univ_set)

    ori_sets = [clear_excl_mark_of_set(set_) for set_ in sets]
    complement_sets : set = set()
    for set_ in universal_sets:
        if set_ not in ori_sets:
            complement_sets |= set_
    
    return complement_sets
