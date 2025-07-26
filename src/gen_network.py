
from cProfile import label
import enum
from importlib.util import LazyLoader
import networkx as nx
import matplotlib.pyplot as plt
import networkx
from networkx.drawing.nx_pydot import to_pydot
from numpy import isin
from IPython.display import Image
import pydot
import io

import matplotlib.pyplot as plt
import matplotlib.image as mpimg

from label_tools import get_compl
need_kill = False



class nfa_create():
    """
    用于创建各类 nfa 基础状态机的类, 以及提供 nfa 之间的各种操作函数
    """
    def __init__(self):
        self.G = nx.DiGraph()
        self.first_node : str
        self.last_node  : str
        self.first_nodes = [] # 用于多个序列重复的时候, 分辨前后序列的开始和结尾
        self.last_nodes  = []
        self.lazy_last_node : str = ''

    def copy(self, nfa = None):
        """复制当前 nfa, 等价 copy to"""
        if nfa is None:
            nfa_return   = nfa_create()
            nfa_return.G = self.G.copy()
            nfa_return.first_node = deepcopy(self.first_node)
            nfa_return.last_node  = deepcopy(self.last_node)
            nfa_return.lazy_last_node = deepcopy(self.lazy_last_node)
            nfa_return.first_nodes = deepcopy(self.first_nodes )
            nfa_return.last_nodes  = deepcopy(self.last_nodes  )
            return nfa_return
        else:
            nfa.G = self.G.copy()
            nfa.first_node = self.first_node
            nfa.last_node  = self.last_node
            nfa.lazy_last_node = self.lazy_last_node
            nfa.first_nodes[0:]   = self.first_nodes [0:]
            nfa.last_nodes [0:]   = self.last_nodes  [0:]
            return nfa
    

    def create_empty_graph(self, name):
        """将类成员 G 变为空 nfa 图"""
        create_empty_graph(self, name)
    
    def create_delay0_graph(self, name):
        """将类成员 G 变为 0 延迟 nfa 图
        ---
        ## 0
        """
        create_delay0_graph(self, name)
    def create_delay1_graph(self,name):
        """将类成员 G 变为 1 延迟 nfa 图
        ---
        ## 1
        """
        create_delay1_graph(self,name) 

    def create_star_consecutive_repetition(self,name,value,expression):
        """将类成员 G 变为表达式 expression 重复任意次的 nfa 图
        ---
        expression[*]
        """
        create_star_consecutive_repetition(self,name,expression)

    def create_plus_consecutive_repetition(self,name,value,expression):
        """将类成员 G 变为表达式 expression 重复至少一次的 nfa 图
        ---
        expression[+]
        """
        create_plus_consecutive_repetition(self,name,expression)
    
    def create_constant_consecutive_repetition(self,name,value,expression):
        """将类成员 G 变为表达式 expression 重复 value(单元素) 次的 nfa 图
        ---
        expression[*a]
        """
        create_constant_consecutive_repetition(self,name,value,expression)
    
    def create_range_consecutive_repetition(self,name,value,expression):
        """将类成员 G 变为表达式 expression 重复 value(区间) 次的 nfa 图
        expression[*a:b]
        """
        create_range_consecutive_repetition(self,name,value,expression)

    def create_constant_delay(self, name, value : list):
        """将类成员 G 变为延迟 value(单元素) 次的 nfa 图
        ---
        ## a
        """
        create_constant_delay(self, name, value)

    def create_range_delay(self, name, value : list):
        """将类成员 G 变为延迟 value(区间) 次的 nfa 图
        ---
        ## [a:b]
        """
        create_range_delay(self, name, value)

    def create_star_delay(self, name, value = None):
        """将类成员 G 变为延迟任意次的 nfa 图
        ---
        ## [*]
        """
        create_star_delay(self, name)

    def create_plus_delay(self, name, value = None):
        """将类成员 G 变为延迟至少一次的 nfa 图
        ---
        ## [+]
        """
        create_plus_delay(self, name)

    def create_constant_goto_repetition(self, name, value : list, expression):
        """将类成员 G 变为表达式 expression goto 重复 value(单元素) 次的 nfa 图
        ---
        expression[->a]
        """
        create_constant_goto_repetition(self, name, value , expression)

    def create_range_goto_repetition(self, name, value : list, expression):
        """将类成员 G 变为表达式 expression goto 重复 value(区间) 次的 nfa 图
        ---
        expression[->a:b]
        """
        create_range_goto_repetition(self, name, value, expression)

    def create_constant_non_consecutive_repetition(self, name, value : list, expression):
        """将类成员 G 变为表达式 expression 非连续且严格重复 value(单元素) 次的 nfa 图
        ---
        expression[=a]
        """
        create_constant_non_consecutive_repetition(self, name, value, expression)

    def create_range_non_consecutive_repetition(self, name, value : list, expression):
        """将类成员 G 变为表达式 expression 非连续且严格重复 value(区间) 次的 nfa 图
        ---
        expression[=a:b]
        """
        create_range_non_consecutive_repetition(self, name, value, expression)

    def nfa_not(self):
        """对 nfa 取 not"""
        nfa_not(self)
    
    def nfa_concat(self,nfa1):
        """将 nfa1 的 G 串联在当前 nfa 的后方"""
        nfa_concat(nfa0 = self,nfa1 = nfa1).copy(self)
    
    def nfa_or(self,nfa1):
        """将参数 nfa1 的图 G 与当前 nfa 的图 G 按或逻辑连接"""
        nfa_or(self,nfa1).copy(self)
    
    def remove_node(self, node):
        """移除图 G 中的指定节点"""
        # FIXME : 应当及时更改头尾节点
        assert node != self.first_node
        assert node != self.last_node
        nfa_remove_node(self, node)
    
    def clean(self,level):
        """根据 level 的不同清理掉 episilion 等边以及节点"""
        return nfa_clean(self,level)

    def node_rename(self,ori, tar):
        """根据 level 的不同清理掉 episilion 等边以及节点"""
        if ori in self.G:
            self.G = nx.relabel_nodes(self.G, {ori : tar})
            assert ori not in self.G
            if ori == self.lazy_last_node:
                self.lazy_last_node = tar
            elif ori == self.first_node:
                self.first_node = tar
            elif ori == self.last_node:
                self.last_node = tar
        
        return self

    def nfa_node_rename(self, src_name, dst_name):
        """用 dst_name 创建新的节点并且按 src_name 去连接, 连接完成后删除 src_name 节点"""
        # FIXME : 应当及时更改头尾节点
        assert src_name != self.first_node
        assert src_name != self.last_node
        nfa_node_rename(self, src_name, dst_name)

    def nfa_kill_to_lazy_kill(self):
        """好像没啥用了, 别调用"""
        nfa_kill_to_lazy_kill(self)
    
    def nfa_show(self):
        """通过 pydot 展示图 G"""
        nfa_show(self)

    def rename_to_number(self):
        return rename_to_number(self)
    
    def to_digraph(self, need_d0 = True):
        """将 nx.MultiDigraph 转换为 nx.Digraph"""
        if isinstance(self, nx.DiGraph):
            return self
        G_new = nx.DiGraph()
        idx = 0
        for node in self.G:
            G_new.add_node(node)
        for node in self.G:
            succs = self.G.successors(node)
            for succ in succs:
                edges = self.G.get_edge_data(node, succ)
                for key, label in edges.items():
                    label = label["label"]
                    mid = node + "_" + str(key) + succ
                    G_new.add_edge(node, mid, label = label)
                    G_new.add_edge(mid, succ,label = set(["__episilon"]))
        
        assert len(G_new) != 0
        if need_d0:
            new_first_node = self.first_node + "_new"
            G_new.add_edge(new_first_node, self.first_node, label = set(["__delay0"]))
            self.first_node = new_first_node
        self.first_nodes = [new_first_node]
        self.G = G_new
        return self

    def normal(self):
        """做一些正规化处理, 更符合 sva 的运行结果"""
        # return self
        # 合并 O --d1--> O --d0--> O 的情况
        self.clean(2)
        # self.nfa_show()

        nfa_tar : nfa_create = self.copy()
        for ori_node in self.G:
            
            tar_pre_nodes_of_ori_node = [x for x in nfa_tar.G.predecessors(ori_node)]
            tar_succ_nodes_of_ori_node = [x for x in nfa_tar.G.successors(ori_node)]
            for succ in tar_succ_nodes_of_ori_node:
                for pre in tar_pre_nodes_of_ori_node:
                    label_pre = nfa_tar.G[pre][ori_node]["label"]
                    label_succ = nfa_tar.G[ori_node][succ]["label"]
                    if label_pre == set(["__delay1"]) and label_succ == set(["__delay0"]):
                        cur_pre = deepcopy(pre)
                        cur_succ = deepcopy(succ)

                        nfa_tar.G.remove_edge(cur_pre, ori_node)
                        succs_of_pre = [x for x in nfa_tar.G.successors(cur_pre)]
                        for succ_of_pre in succs_of_pre:
                            label = nfa_tar.G[cur_pre][succ_of_pre]["label"]
                            mid_node_name = cur_pre + "_epi_" + succ_of_pre
                            nfa_tar.G.add_edge(cur_pre, mid_node_name, label = set(["__episilon"]))
                            nfa_tar.G.add_edge(mid_node_name, succ_of_pre, label = label)
                            nfa_tar.G.remove_edge(cur_pre, succ_of_pre)
                        # 连接一个 __episilon 在 cur_pre 和 cur_succ 之间
                        succs_of_ori_node = [x for x in nfa_tar.G.successors(ori_node)]
                        for succ_of_ori_node in succs_of_ori_node:
                            nfa_tar.G.add_edge(cur_pre, succ_of_ori_node, label = set(["__episilon"]))
                break

        self.G = nfa_tar.G.copy()
        # self.nfa_show()
        return self

                            

# ====================================================================
import re
import json
from copy import deepcopy
from functools import reduce
from networkx.drawing.nx_pydot import to_pydot
import networkx as nx

from nfa_run import nfa_run_one_step
from label_tools import clear_excl_mark_of_set
from gen_network import nfa_create
from label_tools import *


def nfa_to_json(nfa : nfa_create, fpath = None):
    """将 nfa 转换为 json"""
    dic = {}
    if type(nfa.G) == nx.DiGraph:
        for node in nfa.G.nodes():
            dic[node] = {}
            for succ in nfa.G.successors(node):
                dic[node][succ] = list(nfa.G[node][succ]['label'])
    else:
        for node in nfa.G.nodes():
            dic[node] = {}
            for succ in nfa.G.successors(node):
                edges = nfa.G.get_edge_data(node, succ)
                dic[node][succ] = [list(x["label"]) for _,x in edges.items()]
    # 输出漂亮的 json 格式文件
    if fpath is not None:
        with open(fpath, 'w', encoding = "utf-8") as f:
            json.dump(dic, f, indent=4,ensure_ascii=False)
    return dic



def nfa_to_dfa(nfa0 : nfa_create, state_mapping = dict(), mutually_exclusive_sets : list | None = None):
    """将 nfa 转换为 dfa
        返回值 dfa
        通过 state_mapping 返回 nfa 中的状态对应的 dfa 的状态
        mutually_exclusive_sets 是多个集合, 如果在搜寻状态的时候, 状态不同时存在于互斥集合, 则此状态不记录到
        下一次搜寻
    """
    nfa = nfa0.copy()
    nfa.normal()

    TRUE_SET      = set(['__true'])
    DELAY_1_SET   = set(['__delay1'])

    debug_info = {}

    cur_sts : list      = [set([nfa.first_node])] # 集合构成的列表
    finded_sts : list   = [set([nfa.first_node])]
    # nfa_path_labels     = set()

    dfa = nfa_create() # dfa 只是 nfa 的一个子集, 因此直接使用 nfa_create 类型
    dfa.G = nx.MultiDiGraph()

    idx = 0
    dfa.first_node = '0'
    dfa.first_nodes = ['0']
    dfa.last_node = '-1'
    dfa.last_nodes = ['-1']
    dfa.lazy_last_node = '-2'

    dfa.G.add_node('0')
    dfa.G.add_node('-1')
    dfa.G.add_node('-2')
    debug_info['0'] = set([dfa.first_node])
    debug_info['-1'] = set([dfa.last_node])

    assert nfa.first_node != nfa.last_node


    while len(cur_sts) != 0:
        next_sts = []
        for cur_st in cur_sts:

            for index,member in enumerate(finded_sts):
                if member == cur_st:
                    cur_st_idx = index
                    break

            nfa_path_labels     = set()

            nfa_run_one_step(nfa, cur_st, TRUE_SET, path_labels = nfa_path_labels)
            # assert "__true" not in nfa_path_labels
            


            if len(nfa_path_labels |  DELAY_1_SET | TRUE_SET) == 2:
                dfa_inputs : list = [set(['__delay1'])]
            else:
                dfa_inputs : list = get_sub_sets_with_inv(nfa_path_labels - DELAY_1_SET - TRUE_SET)

            # 为当前状态添加边和子节点
            for dfa_input in dfa_inputs:
                # 搜索下一个状态
                next_st = nfa_run_one_step(nfa, cur_st, dfa_input)

                # 当前边没有子节点
                if next_st == set():
                    continue
                
                # 发现了未出现过的新状态
                if next_st not in finded_sts:
                    # 检查 next_st 是否存在于互斥状态中
                    if mutually_exclusive_sets == None:
                        pass
                    else:
                        continue_ = False
                        for set_ in mutually_exclusive_sets:
                            if next_st & set_ == set():
                                continue_ = True
                                break
                        if continue_:
                            continue

                    if nfa.last_node in next_st:
                        next_st_idx = -1
                        pass
                    elif nfa.lazy_last_node in next_st:
                        next_st_idx = -2
                        pass
                    else:
                        finded_sts  += [next_st]
                        next_sts    += [next_st]


                # 搜索 next_st 在 dfa 中的节点编号
                # 如果找不到就代表节点为 -1 或 -2, 即 last_node 或 lazy_last_node
                for index,member in enumerate(finded_sts):
                    if member == next_st:
                        next_st_idx = index
                        break

                if f"{next_st_idx}" in dfa.G.nodes():
                    # 设置 dfa.G 节点 cur_st 到 next_st 节点的边
                    dfa_input = clear_excl_mark_of_set(dfa_input)
                    # 如果已存在边 
                    if dfa.G.has_edge(f'{cur_st_idx}',f'{next_st_idx}'):
                        edges = deepcopy(dfa.G.get_edge_data(f'{cur_st_idx}', f'{next_st_idx}'))
                        new_edge = True
                        for key, elem in edges.items():
                            labal = elem["label"]
                            labal = clear_excl_mark_of_set(labal)
                            if labal & dfa_input != set():
                                edges[key]["label"] = labal & dfa_input
                                new_edge = False
                            # if labal == dfa_input :
                            #     new_edge = False
                        if new_edge:
                            edges[len(edges)] = {"label": dfa_input}
                        
                        for key, elem in edges.items():
                            dfa.G.add_edge(f'{cur_st_idx}', f'{next_st_idx}', key=key, label = elem["label"])
                            pass
                        
                    else:
                        dfa.G.add_edge(f'{cur_st_idx}',f'{next_st_idx}',label=dfa_input)
                else:
                    # 设置 dfa.G 节点 cur_st 到 next_st 节点的边
                    dfa.G.add_edge(f'{cur_st_idx}',f'{next_st_idx}',label=dfa_input)

            idx += 1
        cur_sts = next_sts
    
    for idx, elem in enumerate(finded_sts):
        state_mapping[str(idx)] = elem
    state_mapping[str(-1)] = set([nfa.last_node])
    state_mapping[str(-2)] = set([nfa.lazy_last_node])

    return dfa
    
# __episilon
# ----------------------------------------- 创建空 graph, 首尾用 __episilon 连接------------------
def create_empty_graph(nfa : nfa_create | None, name):
    """
    创建一个空的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ---
    """
    # O--- __episilon ---O
    if nfa is None:
        nfa = nfa_create()
    nfa.G = nx.DiGraph()
    G = nx.DiGraph()
    if need_kill : 
        G.add_node('kill')
    G.add_node(f's_{name}')
    G.add_node(f'e_{name}')
    G.add_edge(f's_{name}', f'e_{name}', label = set([f'__episilon']))
    nfa.G = G 
    nfa.first_node = f's_{name}'
    nfa.last_node  = f'e_{name}'
    nfa.first_nodes = [nfa.first_node]
    nfa.last_nodes  = [nfa.last_node]

    return nfa


def create_delay0_graph(nfa, name):
    """
    创建一个 0 延迟nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ---
    """
    # O--- __episilon --- O --- __delay0 --- O --- __episilon --- O
    if nfa is None: 
        nfa = nfa_create()
    nfa.G = nx.DiGraph()
    G = nx.DiGraph()
    if need_kill : G.add_node('kill')
    G.add_node(f's_{name}')
    G.add_node(f'e_{name}')
    G.add_edge(f's_{name}', f'{name}_l', label = set([f'__episilon']) )
    G.add_edge(f'{name}_l', f'{name}_r', label = set([f'__delay0']) )
    G.add_edge(f'{name}_r', f'e_{name}', label = set([f'__episilon']) )    
    nfa.G = G 
    nfa.first_node = f's_{name}'
    nfa.last_node  = f'e_{name}'
    nfa.first_nodes = [f's_{name}']
    nfa.last_nodes  = [f'e_{name}']
    return nfa

def create_false_graph(nfa, name):
    if nfa is None: 
        nfa = nfa_create()
    create_delay0_graph(nfa, name)
    nfa.G.remove_node(nfa.last_node)
    nfa.G.add_node(nfa.last_node)
    return nfa

def create_delay1_graph(nfa,name):
    """
    创建一个 1 延迟nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ---
    """
    # O--- __episilon --- O --- __delay1 --- O --- __episilon --- O
    if nfa is None: 
        nfa = nfa_create()
    nfa.G = nx.DiGraph()
    G = nx.DiGraph()
    if need_kill :
        G.add_node('kill')
    G.add_node(f's_{name}')
    G.add_node(f'e_{name}')
    G.add_edge(f's_{name}', f'{name}_l', label = set([f'__episilon']))
    G.add_edge(f'{name}_l', f'{name}_m', label = set([f'__episilon']))
    G.add_edge(f'{name}_m', f'{name}_r', label = set([f'__delay1']))
    G.add_edge(f'{name}_r', f'e_{name}', label = set([f'__episilon']))
    nfa.G = G 
    nfa.first_node = f's_{name}'
    nfa.last_node  = f'e_{name}'
    return nfa


# ----------------------------------------- 创建连续重复图 ---------------------------------------
def create_star_consecutive_repetition(nfa, name, expression : str):
    """
    创建一个 expression 重复任意次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    # O--- __episilon --- O --- __delay0 --- O --- __episilon --- O
    #                                        |
    #                                       \|/
    #                                        O --- expression --- O --- __episilon --- O
    #                                       /|\                   /
    #                                        | --- ---------- ---/
    if nfa is None: 
        nfa = nfa_create()
    create_range_consecutive_repetition(nfa, name, [0, '$'],expression)
    return nfa

def create_plus_consecutive_repetition(nfa, name, expression : str):
    """
    创建一个 expression 重复最少一次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    # O--- __episilon --- O --- __delay0 --- O
    #                                        |
    #                                       \|/
    #                                        O --- expression --- O --- __episilon --- O
    #                                       /|\                   /
    #                                        | --- ---------- ---/
    if nfa is None:
        nfa = nfa_create()
    create_range_consecutive_repetition(nfa, name, [1, '$'],expression)
    return nfa

def create_constant_consecutive_repetition(nfa , name , value : list, expression : str, need_delay0 = True):
    """
    创建一个 expression 重复 a 次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    #| <- need_delay0 ->  |< -------  一共 A 个 expression  ---------> |
    # S---  __delay0  --- O --- expression --- ... --- expression --- O
    if nfa is None: 
        nfa = nfa_create()
    if need_delay0 is not True:
        # need_delay0 == False 只用于创建延迟 nfa
        assert expression == '__delay1'
    create_empty_graph(nfa, f'{name}_empty0')

    # + 1 是为了保证 s_{name} 到 {name}0 使用 __episilon
    nfa.first_nodes = []
    nfa.last_nodes  = []

    for i in range (0,value[0]):
        nfa.G.add_edge(f's_{name}{i}'  , f'l_{name}{i}' , label = set([f'__episilon']))
        nfa.G.add_edge(f'l_{name}{i}'  , f'r_{name}{i}' , label = set([f'{expression}']))
        nfa.G.add_edge(f'r_{name}{i}'  , f'e_{name}{i}' , label = set([f'__episilon']))
        if i != 0 :
            nfa.G.add_edge(f'e_{name}{i-1}'  , f's_{name}{i}' , label = set([f'__episilon']))
        else:
            nfa.G.add_edge(nfa.last_node, f's_{name}{i}', label = set([f'__episilon']))
        nfa.last_node = f'e_{name}{i}'

        nfa.first_nodes.append(f's_{name}{i}')
        nfa.last_nodes.append(f'e_{name}{i}')
    
    nfa.G.add_edge(nfa.last_node, f'e_{name}', label = set(['__episilon']))
    nfa.last_node = f'e_{name}'

    if need_delay0:
        nfa_temp = create_delay0_graph(None, f'{name}_delay0')
    else:
        nfa_temp = create_empty_graph(None, f'{name}_empty1')
    nfa_temp = nfa_concat(nfa_temp,nfa)
    
    nfa_temp.copy(nfa)

    return nfa


def create_range_consecutive_repetition(nfa, name, value : list, expression : str,need_delay0 = True):
    """
    创建一个 expression 重复 a 到 b 次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    #| <- need_delay0 ->  |< -------  一共 A 个 expression  ---------> |  < -----------  一共 B 个 expression -- -------> |
    # S---  __delay0  --- O --- expression --- ... --- expression --- O  --- expression --- ... O ... --- expression --- E
    #                                                                \|/                        |
    #                                                                 O --- __episilon --- E   \|/
    #                                                                                           O --- __episilon --- E
    if nfa is None: 
        nfa = nfa_create()
    if value[0] == value[1]:
        create_constant_consecutive_repetition(nfa, name, [value[0]], expression, need_delay0)
        return nfa
    
    if value[1] == '$':
        if value[0] == 0:
            if need_delay0:
                nfa_temp0 = create_delay0_graph(None, f'{name}_d0')
            else:
                nfa_temp0 = create_empty_graph(None, f'{name}_d0')
            
            nfa_temp1 = create_range_consecutive_repetition(None, name, [value[0] + 1, value[1]], expression)
            nfa_or(nfa_temp0, nfa_temp1).copy(nfa)
        else:
            create_constant_consecutive_repetition(nfa, name, [value[0] + 1], expression, need_delay0)
            nfa.G.add_edge(f'{nfa.last_nodes[-1]}', nfa.last_nodes[-2], label = set([f'__episilon']))

            nfa.G.add_edge(f'{nfa.last_nodes[-2]}', nfa.last_node, label = set([f'__episilon']))
        return nfa

    assert value[0] <= value[1]
    create_constant_consecutive_repetition(nfa, name, [value[1]], expression, need_delay0)
    for i in range (value[0] , value[1] + 1):
        nfa.G.add_edge(nfa.last_nodes[i], nfa.last_node, label = set([f'__episilon']))

    
    return nfa

# ----------------------------------------- 创建延迟图 ---------------------------------------


def create_constant_delay(nfa, name, value : list):
    """
    创建一个 expression 为 __delay1 重复 a 次的 nfa 状态机, 首尾用 __episilon 连接,
    如果 a = 0 则有 delay0 开头, 否则无
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    #|    <- a == 0 ->    |< -------  一共 A 个 __delay1  ---------> |
    # S---  __delay0  --- O --- __delay1 --- ... --- __delay1 --- O
    if nfa is None: 
        nfa = nfa_create()
    if value[0] == 0:
        create_constant_consecutive_repetition(nfa,name,[value[0]],'__delay1', need_delay0 = False)
    else:
        create_constant_consecutive_repetition(nfa,name,[value[0]],'__delay1', need_delay0 = False)
    return nfa

def create_range_delay(nfa, name, value : list):
    """
    创建一个 __delay1 重复 a 到 b 次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    #| <- A == 0      ->  |< -------  一共 A 个 __delay1  --------->  |  < -----------     一共 B 个 __delay1 -- -------> |
    # S--- __episilon --- O --- __delay1   --- ... --- __delay1   --- O  --- __delay1 ---     ... O ... --- __delay1 --- E
    # |                                                              \|/                        |
    #\|/                                                              O --- __episilon --- E   \|/
    # O--- __delay0 ----- E                                                                     O --- __episilon --- E
    if nfa is None: 
        nfa = nfa_create()
    # assert(value[0] > 0) #只处理 m > 0 的情况
    if value[0] > 0:
        create_range_consecutive_repetition(nfa,name,[value[0], value[1]],'__delay1', need_delay0 = False)
    else:
        create_range_consecutive_repetition(nfa,name,[1, value[1]],'__delay1', need_delay0 = False)
        nfa_d0 = create_constant_delay(None, f'{name}crd_d0', [0])
        nfa_or(nfa_d0, nfa).copy(nfa)
    return nfa
    

def create_star_delay(nfa, name):
    """
    创建一个 __delay1 重复任意次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    # S--- __episilon --- O --- __delay1   --- O --- E
    # |                  /|\                   |
    #\|/                  |--------------------|
    # O--- __delay0 ----- E                    
    if nfa is None: 
        nfa = nfa_create()
    create_range_delay(nfa, name, [0, '$'])
    return nfa

def create_plus_delay(nfa, name):
    """
    创建一个 __delay1 至少重复 1 次的 nfa 状态机, 首尾用 __episilon 连接
    ---
    可以选择传入一个已有的 nfa 实例, 也可以传入 None, 以便创建一个新的 nfa 实例
    ------
    """
    # S--- __episilon --- O --- __delay1   --- O --- E
    #                    /|\                   |
    #                     |--------------------|

    if nfa is None: 
        nfa = nfa_create()
    create_range_delay(nfa, name, [1, '$'])
    return nfa


# ----------------------------------------- 创建序列重复图 ---------------------------------------
# 此函数会为 nfa 的每个 node 后加上 index, 因此 nfa.first_node = f'{nfa.first_node}{0}',nfa.lst_node = f'{nfa.lst_node}{value[0]}' 
# (a)[*2] = (a) ##1 (a) 而不是 (a) ##0 (a)
def create_sequence_constant_consecutive_repetition(nfa, value) :
    assert(nfa != None)
    #FIXME
    nfa_temp0 = create_empty_graph(None, f'{nfa.first_node}_sccr_delay0')
    # nfa_temp0 = create_empty_graph(None, f'{nfa.first_node}_sccr_empty')

    if(value[0] == 0):
        nfa_temp0.copy(nfa)
        return nfa

    for subfix in range (0, value[0] ):
        nfa_temp1 = copy_and_rename(nfa, subfix)
        nfa_temp1.first_nodes = [nfa_temp1.first_node]
        nfa_temp1.last_nodes = [nfa_temp1.last_node]
        nfa_delay1 = create_delay1_graph(None, f'{nfa.first_node}{subfix}_sccr_d1')

        if subfix != 0:
            nfa_delay1.first_nodes = []
            nfa_delay1.first_nodes = []
            nfa_temp0 = nfa_concat(nfa_temp0,nfa_delay1)
        nfa_temp0 = nfa_concat(nfa_temp0,nfa_temp1)

    nfa_temp0.copy(nfa)
    return nfa


def create_sequence_range_consecutive_repetition(nfa, value):
    """
    创建序列的重复, 将输入的 nfa 图 G 重复 a 到 b 次"""
    assert nfa is not None
    ori_last_node = nfa.last_node

    # m == n
    if value[0] == value[1]:
        create_sequence_constant_consecutive_repetition(nfa,[value[1]])
        return nfa 
    
    if value[1] == '$':
        create_sequence_constant_consecutive_repetition(nfa,[value[0] + 1])
    else:
        create_sequence_constant_consecutive_repetition(nfa,[value[1]])
    assert len(nfa.first_nodes) != 0

    if value[1] == '$':
        
        first_node = nfa.first_nodes[-1]
        last_node  = nfa.last_nodes [-1]
        nfa_delay1 = create_delay1_graph(None, f'{nfa.first_node}_srcr_d1')
        nfa.G = compose_digraph(nfa.G, nfa_delay1.G)


        
        nfa.G.add_edge(last_node , f's_{nfa.first_node}_srcr_d1' , label = set(['__episilon']))
        nfa.G.add_edge(f'e_{nfa.first_node}_srcr_d1' , first_node, label = set(['__episilon']))

        nfa.G.add_edge(last_node , f'e_{last_node}', label = set(['__episilon']))
        nfa.last_node      = f'e_{last_node}'
        nfa.last_nodes[-1] = f'e_{last_node}'

        nfa.G.add_edge(nfa.last_nodes[-2], last_node , label = set(['__episilon']))
            
        return nfa
    
    else:
        assert value[1] > value[0]
        last_node  = nfa.last_nodes [-1]
        for subfix in range (value[0], value[1]):
            middle_first_node = nfa.last_nodes[subfix]
            if middle_first_node == last_node:
                pass
            nfa.G.add_edge(middle_first_node,last_node , label = set(['__episilon']))
    return nfa

def create_sequence_star_consecutive_repetition(nfa):
    """创建序列重复的 star 版本"""
    if nfa is None: 
        nfa = nfa_create()
    create_sequence_range_consecutive_repetition(nfa,[0,'$'])
    return nfa

def create_sequence_plus_consecutive_repetition(nfa):
    """创建序列重复的 plus 版本"""
    if nfa is None: 
        nfa = nfa_create()
    create_sequence_range_consecutive_repetition(nfa,[1,'$'])
    return nfa

# ----------------------------------------- 创建 goto 重复 ---------------------------------------
def create_constant_goto_repetition_middle(nfa, name, expression):
    """
    此函数实现 !X[*] ##1 X, X 为输入的 expression
    """
    if nfa is None: 
        nfa = nfa_create()
    # 利用等价 X[->a] = (!X[*] ##1 X)[*a] 实现

    nfa0 = nfa_create() # !X[*]
    create_star_consecutive_repetition(nfa0, name, f'!{expression}')
    
    nfa1 = nfa_create() # ##1
    create_constant_delay(nfa1, f'{name}_delay1', [1])

    nfa2 = nfa_create() # X
    create_constant_consecutive_repetition(nfa2, f'{name}_X', [1], f'{expression}')

    nfa0 = nfa_concat(nfa0, nfa1) # nfa0 = !X[*] ##1

    nfa0 = nfa_concat(nfa0, nfa2) # nfa0 = !X[*] ##1 X

    nfa0.copy(nfa)

    return nfa



def create_constant_goto_repetition(nfa, name, value : list, expression):
    """利用等价 X[->a] = (!X[*] ##1 X)[*a] 实现 goto 操作符"""
    if nfa is None: 
        nfa = nfa_create()
    # 利用等价 X[->a] = (!X[*] ##1 X)[*a] 实现
    create_constant_goto_repetition_middle(nfa, name, expression)
    create_sequence_constant_consecutive_repetition(nfa, [value[0]])
    
    return nfa

def create_range_goto_repetition(nfa, name, value : list, expression):
    """利用等价 X[->a:b] = (!X[*] ##1 X)[*a:b] 实现 goto 操作符"""
    if nfa is None: 
        nfa = nfa_create()
    create_constant_goto_repetition_middle(nfa, name, expression)
    create_sequence_range_consecutive_repetition(nfa,value)
    return nfa


# ----------------------------------------- 创建非连续重复 ---------------------------------------
def create_constant_non_consecutive_repetition(nfa, name, value : list,expression):
    """利用等价 X[=a] = X[->a] ##1 !X[*]实现 非连续重复 操作符"""
    if nfa is None: 
        nfa = nfa_create()
    create_constant_goto_repetition(nfa,name,[value[0]],expression)
    nfa_concat(nfa, create_constant_delay(None, f'{name}_del', [1])).copy(nfa)
    nfa_concat(nfa, create_star_consecutive_repetition(None, f'{name}_star', f'!{expression}')).copy(nfa)
    return nfa
def create_range_non_consecutive_repetition(nfa, name, value : list, expression):
    """利用等价 b [=m:n] ( b [->m:n] ##1 !b [*0:$] ) 实现 非连续重复 操作符
    """
    if nfa is None: 
        nfa = nfa_create()
    create_range_goto_repetition(nfa,name,value,expression)
    nfa_concat(nfa, create_constant_delay(None, f'{name}_del', [1])).copy(nfa)
    nfa_concat(nfa, create_star_consecutive_repetition(None, f'{name}_star', f'!{expression}')).copy(nfa)
    return nfa


# ----------------------------------------- not and or ---------------------------------------
def nfa_not(nfa0 : nfa_create):
    """not 操作应当引入新的 last 节点, 并且把每个节点到下一个节点的不成立的边连接到新的 last 节点
        旧的 last 节点断开所有的连接
    """
    # return nfa
    nfa = nfa0.copy()
    # nfa 转为 dfa
    nfa = nfa_to_dfa(nfa)
    nfa.to_digraph()
    G : nx.DiGraph = nfa.G
    # 在 G 中添加新的 last 节点
    nfa_last_node = f'{nfa.last_node}_not'
    G.add_node(nfa_last_node)
    # 把每个节点到下一个节点不成立的边连接到新的 last 节点
    for node in G.nodes():
        labels = []
        # 如果边为 __episilon, __delay0 则此节点不可能停留
        # 如果边为 __true,__delay1 则不存在不成立的条件, 不需要判断
        not_include = set(["__episilon", "__true", "__delay0", "__delay1"])
        for sucss in G.successors(node):
            label = G[node][sucss]['label']
            if len(label & not_include) != 0:
                continue
            labels += [label]
        # 如果 sucss 中存在旧的 last 节点, 则应当移除 node 的到子节点的边(label 相等)
        if nfa.last_node in G.successors(node):
            remove_nodes : list = []
            label_to_last = G.get_edge_data(node, nfa.last_node)["label"]
            for sucss in G.successors(node):
                label = G[node][sucss]['label']
                if label == label_to_last:
                    remove_nodes += [sucss]
            for remove_node in remove_nodes:
                G.remove_edge(node, remove_node) 
            G.add_edge(node, nfa.last_node, label = label_to_last)

        if len(labels) != 0:
            compl_label = get_compl(labels)
            if compl_label != set():
                G.add_edge(node, nfa_last_node, label=compl_label)
        else:
            continue
        
    # 旧的 last 节点不能直接移除, 在其后接2个 __delay0 连接的边作为结束
    G.add_edge(nfa.last_node, f"{nfa.last_node}_dead0", label = set([f'__delay0']))
    G.add_edge(f"{nfa.last_node}_dead0", f"{nfa.last_node}_dead", label = set([f'__delay0']))
    # 将新的 last 节点设置为 nfa 的 last 节点 
    nfa.last_node = nfa_last_node
    nfa = copy_and_rename(nfa, nfa0.first_node)
    return nfa

    

# ----------------------------------------- 功能性函数 ---------------------------------------
# ---------------- 只存在于库中的函数 -----------------
def copy_and_rename(nfa : nfa_create, subfix):
    """复制输入的 nfa 并且为所有节点加上后缀 subfix, 并返回复制后的 nfa"""
    nfa_return = nfa.copy()
    
    mapping = {k : f"{k}{subfix}" for k in nfa.G.nodes}
    nfa_return.G = nx.relabel_nodes(nfa_return.G, mapping)

    nfa_return.first_node = f'{nfa.first_node}{subfix}'
    nfa_return.last_node  = f'{nfa.last_node}{subfix}'
    nfa_return.lazy_last_node  = f'{nfa.lazy_last_node}{subfix}'
    nfa_return.first_nodes = [f'{x}{subfix}' for x in nfa.first_nodes]
    nfa_return.last_nodes  = [f'{x}{subfix}' for x in nfa.last_nodes]
    return nfa_return


def compose_digraph(G0,G1):
    G2 = nx.compose(G0, G1)
    # assert len(G2) == len(G0) + len(G1)
    return G2


# ---------------- 可存在于类中的函数 -----------------
def rename_to_number(nfa : nfa_create):
    nodes = [x for x in nfa.G.nodes]
    mapping = {k : str(idx) for idx, k in enumerate(nodes)}

    nfa.G = nx.relabel_nodes(nfa.G, mapping)
    nfa.first_node = mapping[nfa.first_node] 
    nfa.last_node = mapping[nfa.last_node]
    nfa.first_nodes = [mapping[x] for x in nfa.first_nodes if x in mapping]
    nfa.last_nodes = [mapping[x] for x in nfa.last_nodes if x in mapping]

    return nfa


def nfa_concat(nfa0 : nfa_create, nfa1 : nfa_create):
    """串联两个 nfa 并且记录新的 first_node 和 last_node, 且反馈每个 nfa 的 first_nodes 和 last_nodes"""
    nfa0_copy = copy_and_rename(nfa0,"_cc0")
    nfa1_copy = copy_and_rename(nfa1,"_cc1")
    nfa0_copy.node_rename(nfa0_copy.lazy_last_node, '-2')
    nfa1_copy.node_rename(nfa1_copy.lazy_last_node, '-2')

    nfa = nfa_create()
    nfa.G = compose_digraph(nfa0_copy.G,nfa1_copy.G)
    nfa.G.add_edge(nfa0_copy.last_node, nfa1_copy.first_node, label = set([f'__episilon']))
    nfa.first_node  = nfa0_copy.first_node
    nfa.last_node   = nfa1_copy.last_node
    nfa.first_nodes = nfa0_copy.first_nodes + nfa1_copy.first_nodes
    nfa.last_nodes  = nfa0_copy.last_nodes  + nfa1_copy.last_nodes
    nfa.lazy_last_node = '-2'
    return nfa

def nfa_or(nfa0, nfa1):
    """并联两个 nfa 并且记录新的 first_node 和 last_node, 且反馈每个 nfa 的 first_nodes 和 last_nodes"""
    #TODO 应当增加重命名行为, 否则可能导致后续名称相同导致图合并错误
    nfa0_copy : nfa_create = copy_and_rename(nfa0, "_or0")
    nfa1_copy : nfa_create = copy_and_rename(nfa1, "_or1")
    nfa0_copy.node_rename(nfa0_copy.lazy_last_node, '-2')
    nfa1_copy.node_rename(nfa1_copy.lazy_last_node, '-2')
    
    nfa = nfa_create()
    nfa.G = compose_digraph(nfa0_copy.G,nfa1_copy.G)
    nfa.G.add_edge(f'{nfa0_copy.first_node}_or', f'{nfa0_copy.first_node}'  , label = set([f'__episilon']))
    nfa.G.add_edge(f'{nfa0_copy.first_node}_or', f'{nfa1_copy.first_node}'  , label = set([f'__episilon']))
    nfa.G.add_edge(f'{nfa0_copy.last_node}'     ,f'{nfa0_copy.last_node}_or', label = set([f'__episilon']))
    nfa.G.add_edge(f'{nfa1_copy.last_node}'     ,f'{nfa0_copy.last_node}_or', label = set([f'__episilon']))

    nfa.first_node = f'{nfa0_copy.first_node}_or'
    nfa.last_node  = f'{nfa0_copy.last_node }_or'

    nfa.first_nodes = [nfa.first_node]
    nfa.last_nodes  = [nfa.last_node ]
    nfa.lazy_last_node = '-2'
    return nfa

def nfa_intersect(nfa0 : nfa_create, nfa1 : nfa_create):
    """
    intersect 要求同时开始同时结束, 因此选择将 nfa0 和 nfa1 转换为 dfa
    为满足同时开始的条件 1:
        假设 dfa0 的起点有两个子节点且边为(A,B), A = (a0 + a1 +...), a0 为单个边, A 为多边
        dfa1 的起点有三个子节点且边为(C,D,E), 则 dfa0 的第一组边变为 (A, B)(C + D + E) = 
        (A(C+D+E), B(C+D+E)), 同理 dfa1 变为 (C(A+B), D(A+B), E(A+B))
        简化为 : 
            如果 dfa_mid 的第一组节点中的节点不同时包含s0 和 s1 则剔除
                第一组节点 : nfa 接受的第一批输入获得的 dfa 节点, 即 dfa 的 s0
    为满足同时结束的条件 2:
        在 1 的基础上添加新的起点 s_new 并且用 __episilon 连接至 dfa0 和 dfa1 的起点重命名为 nfa_new
        将 nfa_new 重新转换为 dfa_new, 如果 dfa_new 的某节点是由 dfa0 和 dfa1 的终点构成的, 则标记为
        dfa_new 的预终点之一, 通过 __episilon 连接到真正的终点
    """
    nfa0.normal().clean(2).rename_to_number()
    nfa1.normal().clean(2).rename_to_number()

    dfa0_to_nfa0_mapping = {}
    dfa1_to_nfa1_mapping = {}
    # nfa0.nfa_show()
    # nfa1.nfa_show()


    # 获取 nfa 的 last 节点
    nfa0_last = nfa0.last_node
    nfa1_last = nfa1.last_node

    # 用 or 连接两个 nfa
    nfa0_or_nfa1 = nfa_or(nfa0, nfa1)
    # nfa0_or_nfa1.nfa_show()

    nfa0_last = set([nfa0_last + "_or0"])
    nfa1_last = set([nfa1_last + "_or1"])

    nfa0_st_sets = set([x + "_or0" for x in nfa0.G])
    nfa1_st_sets = set([x + "_or1" for x in nfa1.G])

    # 删掉终节点
    nfa0_or_nfa1.G.remove_node(nfa0_or_nfa1.last_node)
    nfa0_or_nfa1.G.add_node(nfa0_or_nfa1.last_node)
    # nfa0_or_nfa1.nfa_show()

    # nfa0_or_nfa1 重新转换为 dfa_mid, 从而获取状态集合
    state_mapping = {}
    dfa_mid : nfa_create = nfa_to_dfa(nfa0_or_nfa1, state_mapping, mutually_exclusive_sets=[nfa0_st_sets, nfa1_st_sets])
    # dfa_mid.nfa_show()


    # 处理终点
    dfa_mid_nodes = [x for x in dfa_mid.G if x != "-1"]
    dfa_mid.G.add_node("-1_new")
    for dfa_mid_node in dfa_mid_nodes:
        unmap_dfa_mid_node = state_mapping[dfa_mid_node]
        # if (unmap_dfa_mid_node & nfa0_last != set()) and (unmap_dfa_mid_node & nfa1_last != set()):
        nfa_last = nfa0_last | nfa1_last
        temp = unmap_dfa_mid_node & nfa_last
        if len(temp) == 0:
            continue
        elif len(temp) == 1:
            succs = [x for x in dfa_mid.G.successors(dfa_mid_node)]
            if len(succs) == 0:
                dfa_mid.G.remove_node(dfa_mid_node)
        elif len(temp) == 2: # 只准包含原有的终态, 其他的都不算新的终态
            succs = [x for x in dfa_mid.G.successors(dfa_mid_node)]
            for idx, succ in enumerate(succs):
                edges = dfa_mid.G.get_edge_data(dfa_mid_node, succ)
                dfa_mid.G.add_edge(dfa_mid_node, f"{dfa_mid_node}_{idx}_{succ}", label = set(["__episilon"]))
                for key, label in edges.items():
                    dfa_mid.G.add_edge(f"{dfa_mid_node}_{idx}_{succ}", succ, key = key, label = label["label"])
                dfa_mid.G.remove_edge(dfa_mid_node, succ)

                pass
            dfa_mid.G.add_edge(dfa_mid_node,"-1_new", label= set(["__episilon"]))
    # dfa_mid.nfa_show()

    dfa_mid.last_node = "-1_new"
    dfa_mid.first_nodes = [dfa_mid.first_node]
    dfa_mid.last_nodes  = [dfa_mid.last_node]



    dfa_mid.to_digraph()

    # dfa_mid.nfa_show()

    return dfa_mid

def nfa_within(nfa0, nfa1):
    """
    ( R1 within R2 ) = ((1[*0:$] ##1 R1 ##1 1[*0:$]) intersect R2 )
    """
    nfa_sharp_1_name = nfa0.first_node + "_d1_" + nfa1.first_node
    nfa_true_repeat_star_name = nfa0.first_node + "_true_rp_star" + nfa1.first_node

    nfa_true_repeat_star = create_star_consecutive_repetition(nfa = None, name = nfa_true_repeat_star_name, expression="__delay1")    
    nfa_sharp_1 = create_delay1_graph(nfa = None, name = nfa_sharp_1_name)

    nfa_return = nfa_concat(nfa_true_repeat_star, nfa_sharp_1)
    nfa_return = nfa_concat(nfa_return, nfa0)
    nfa_return = nfa_concat(nfa_return, nfa_sharp_1)
    nfa_return = nfa_concat(nfa_return, nfa_true_repeat_star)
    nfa_return = nfa_intersect(nfa_return, nfa1)
    return nfa_return

def nfa_throughout(expression_or_dist : str , nfa0 : nfa_create):
    """
    ( R1 within R2 ) = ((1[*0:$] ##1 R1 ##1 1[*0:$]) intersect R2 )
    """
    rep_name = "throughout" + nfa0.first_node
    star_rep = create_star_consecutive_repetition(None, rep_name, expression_or_dist)
    nfa_return = nfa_intersect(star_rep, nfa0)
    return nfa_return

def nfa_and(nfa0_ : nfa_create, nfa1_ : nfa_create) -> nfa_create:
    """
    ( R1 and R2 ) = ((( R1 ##1 1[*0:$]) intersect R2 ) or ( R1 intersect ( R2 ##1 1[*0:$])))
    eq_l = ((( R1 ##1 1[*0:$]) intersect R2 )
    eq_r = ( R1 intersect ( R2 ##1 1[*0:$])))
    """
    nfa0 = nfa0_.copy()
    nfa1 = nfa1_.copy()
    eq_l : nfa_create
    eq_r = nfa_create
    r1 = nfa0.normal().clean(2)
    r2 = nfa1.normal().clean(2)
    # r1.nfa_show()
    # r2.nfa_show()

    nfa_sharp_1_name = nfa0.first_node + "_d1_" + nfa1.first_node
    nfa_true_repeat_star_name = nfa0.first_node + "_true_rp_star" + nfa1.first_node
    nfa_true_repeat_star = create_star_consecutive_repetition(nfa = None, name = nfa_true_repeat_star_name, expression="__delay1")    
    nfa_sharp_1 = create_constant_delay(nfa = None, name = nfa_sharp_1_name, value = [1])

    eq_l = nfa_concat(r1, nfa_sharp_1)
    eq_l = nfa_concat(eq_l, nfa_true_repeat_star)
    eq_l = nfa_intersect(eq_l, r2)
    # eq_l.nfa_show()

    eq_r = nfa_concat(r2, nfa_sharp_1)
    eq_r = nfa_concat(eq_r, nfa_true_repeat_star)
    eq_r = nfa_intersect(eq_r, r1)
    # eq_r.nfa_show()


    nfa_return = nfa_or(eq_l, eq_r)
    return nfa_return

def nfa_overlap_implication(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    R |-> P = 特殊处理的 (not R ##1 ) or (dfa(R) ## 0 P)
    要断开 (not (R ##1)) 到 last 节点的连接, 连接到 lazy_last, 此节点不报 finish 和 error
    """
    d1_name = nfa0.first_node + "_d1_" + nfa1.first_node
    not_r = nfa_not(nfa_concat(nfa0, create_delay1_graph(None, d1_name)))

    d0_name = nfa0.first_node + "_d0_" + nfa1.first_node
    # nfa0 转换成 dfa 后可以消除同时存在的终态和中间状态, 因为 R |-> P 要求 R 出现了终态就向后执行
    # 如果保留 终态和中间状态 同时存在的行为, 会导致多次启动 P
    dfa0 = nfa_to_dfa(nfa0).to_digraph()
    r_sharp0_p = nfa_concat(dfa0, create_constant_delay(None,d0_name,[0]))
    r_sharp0_p = nfa_concat(r_sharp0_p, nfa1)


    # not_r.nfa_show()
    # r_sharp0_p.nfa_show()

    G0 = not_r.G.copy()
    G1 = r_sharp0_p.G.copy()
    composed_G : nx.DiGraph = compose_digraph(G0,G1)
    
    start_node = "s_" + not_r.first_node + "_" + r_sharp0_p.first_node
    last_node = "e_" + not_r.last_node + "_" + r_sharp0_p.last_node
    lazy_last_node = not_r.last_node + "_lazy"
    befor_lazy_last_node = lazy_last_node + "_d0"

    epi_set = set(["__episilon"])
    composed_G.add_edge(start_node, not_r.first_node, label = epi_set)
    composed_G.add_edge(start_node, r_sharp0_p.first_node, label = epi_set)
    composed_G.add_edge(r_sharp0_p.last_node, last_node, label = epi_set )
    composed_G.add_edge(not_r.last_node, befor_lazy_last_node, label = set(["__delay0"]))
    composed_G.add_edge(befor_lazy_last_node, lazy_last_node, label = set(["__delay1"]))

    nfa_return = nfa_create()
    nfa_return.first_node = start_node
    nfa_return.last_node  = last_node
    nfa_return.first_nodes = [nfa_return.first_node]
    nfa_return.last_nodes = [nfa_return.last_nodes]
    nfa_return.lazy_last_node = lazy_last_node
    nfa_return.G = composed_G
    # nfa_return.nfa_show()
    return nfa_return

def nfa_non_overlap_implication(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    (R |=> P) ((R ##1 1) |-> P)
    """
    d1_name = nfa0.first_node + "_d1"
    true_name = nfa0.first_node + "_true"
    d1 = create_delay1_graph(None, d1_name)
    tru = create_constant_consecutive_repetition(None, true_name, [1], "__delay1")
    nfa0_sharp1_true = nfa_concat(nfa0, d1)
    nfa0_sharp1_true = nfa_concat(nfa0_sharp1_true, tru)

    nfa_return = nfa_overlap_implication(nfa0_sharp1_true, nfa1)
    return nfa_return

def nfa_overlap_follow_by(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """sequence_expr #-# strong(sequence_expr1) ≡ strong(sequence_expr ##0 sequence_expr1) """
    nfa_return = nfa_concat(nfa0, nfa1)
    return nfa_return

def nfa_non_overlap_follow_by(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """sequence_expr #-# strong(sequence_expr1) ≡ strong(sequence_expr ##1 sequence_expr1) """
    d1_name = nfa0.first_node + "_d1"
    d1 = create_delay1_graph(None, d1_name)

    nfa_return = nfa_concat(nfa0, d1)
    nfa_return = nfa_concat(nfa_return, nfa1)
    return nfa_return

def nfa_until(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    p until q ->
    q or (p.dfa.start |-> p[+] or (1[*] ##1 q))
    q or {   dfa[ (p[+] or (1[*] ##1 q)).去除 p[+]到终点的连接 ]    }
    """
    p = nfa0
    q = nfa1

    # tru_name = q.first_node + "_true"
    # tru = create_constant_consecutive_repetition(None, tru_name, [1], "__delay1")
    # q_tru = nfa_overlap_implication(q, tru)
    # q_tru.nfa_show()

    p_dfa = nfa_to_dfa(p)
    
    # 构建 p_dfa_start
    p_dfa_start = p_dfa.copy()
    nodes = set([x for x in p_dfa_start.G])
    nodes -= set([x for x in p_dfa_start.G.successors(p_dfa_start.first_node)])
    nodes -= set([p_dfa_start.first_node])
    for node in nodes:
        p_dfa_start.G.remove_node(node)
    p_dfa_start.G.add_node(p_dfa_start.last_node)

    for succ in p_dfa_start.G.successors(p_dfa_start.first_node):
        if succ != p_dfa_start.last_node:
            p_dfa_start.G.add_edge(succ, p_dfa_start.last_node, label = set(["__episilon"]))
    
    p_dfa_start.to_digraph()
    # p_dfa_start.nfa_show()

    # p[+].dfa 的每个节点连接到 q.dfa 的起点的下一组节点
    p_plus = create_sequence_plus_consecutive_repetition(p)
    # 1[*] ##1 q
    tru_star_name = q.first_node + "_true_star"
    d1_name = q.first_node + "_d0"
    tru_star = create_star_consecutive_repetition(None, tru_star_name, "__delay1")
    d1 = create_delay1_graph(None, d1_name)
    tru_d0_q = nfa_concat(tru_star,nfa_concat(d1,q))

    # p[+] or 1[*] ##1 q 在去除 p[+] 到终点的连接后求 dfa, 并且给定互斥集合
    nfa_return = nfa_or(p_plus, tru_d0_q)
    nfa_return.G.remove_edge(p_plus.last_node + "_or0", nfa_return.last_node)
    # nfa_return.nfa_show()
    
    mutually_exclusive_sets = []
    mutually_exclusive_sets += [set([x + "_or0" for x in p_plus.G])]
    mutually_exclusive_sets += [set([x + "_or1" for x in tru_d0_q.G])]

    nfa_return = nfa_to_dfa(nfa_return, mutually_exclusive_sets = mutually_exclusive_sets)
    # nfa_return.nfa_show()
    nfa_return.to_digraph()

    # p_dfa_start
    # nfa_return = nfa_overlap_implication(p_dfa_start, nfa_return)

    # 结束
    # nfa_return.nfa_show()
    nfa_return = nfa_or(nfa_return, q)
    # nfa_return.nfa_show()

    return nfa_return

def nfa_until_with(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    — (p until_with q) = ((p until (p and q)).
    """
    p = nfa0
    q = nfa1
    p_and_q = nfa_and(p,q)
    nfa_return = nfa_until(p, p_and_q)
    return nfa_return

def nfa_always(nfa0 : nfa_create) -> nfa_create:
    """
    — (always p) = (p until 0).
    """
    p = nfa0
    false_name = p.first_node + "_false"
    # fal = create_constant_consecutive_repetition(None, false_name, [1],"__delay1")
    fal = create_false_graph(None, false_name)
    
    nfa_return = nfa_until(p, fal)
    return nfa_return

def nfa_implies(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    — p implies q = ( (not p) or q ).
    """
    p = nfa0
    q = nfa1
    not_p = nfa_not(p)
    nfa_return = nfa_or(not_p, q)
    return nfa_return

def nfa_iff(nfa0 : nfa_create, nfa1 : nfa_create) -> nfa_create:
    """
    — p iff q = ((p implies q) and (q implies p)).
    """
    p = nfa0
    q = nfa1
    # p.nfa_show()
    p.normal()
    # p.nfa_show()

    p_implies_q = nfa_implies(p,q)
    q_implies_p = nfa_implies(q,p)
    nfa_return = nfa_and(p_implies_q, q_implies_p)
    # nfa_return.nfa_show()
    nfa_return.clean(2)
    # nfa_return.nfa_show()
    return nfa_return

# 暂时只能移除为 episilon 出边的节点
def nfa_remove_node(nfa : nfa_create, node):
    """移除某些节点, 主要被用于 clean 函数"""
    assert(node in nfa.G)
    predecessors = list(nfa.G.predecessors(node))
    successors   = list(nfa.G.successors(node)  )
    for predecessor in predecessors:
        label = nfa.G.get_edge_data (predecessor,node)['label']
        for successor in successors:
            # assert(set(['__episilon']) == nfa.G.get_edge_data(node,successor)['label'])
            # if successor != predecessor: # 避免错误的形成环
            if nfa.G.has_edge(predecessor, successor):
                label_ori = nfa.G.get_edge_data(predecessor, successor)["label"]
                new_label = label_ori & label
                assert new_label != set()
                nfa.G.add_edge(predecessor, successor, label = new_label)
            else:
                nfa.G.add_edge(predecessor, successor, label = label)
    nfa.G.remove_node(node)
    return nfa


# 如果一个节点所有入边和出边都是 __episilon 则可以移除, 除了 s_, e_ 和他们两个前后的节点还有
def nfa_clean(nfa : nfa_create, level = 0):
    """
    不会删除头尾节点
    level = 0 : 删除所有出入边都为 __episilon 的节点, 不包括头节点的后继节点和尾节点的前驱节点
    level = 1 : 删除所有出边都为 __episilon 的节点, 不包括头节点的后继节点和尾节点的前驱节点
    level = 2 : 删除所有出边都为 __episilon 的节点, 包括头节点的后继节点和尾节点的前驱节点
    """
    if isinstance(nfa.G, nx.MultiDiGraph):
        nfa.to_digraph()
    # nfa.rename_to_number()
    
    if level == 0:
        return nfa
    loop = True
    set_epi = set(["__episilon"])
    set_d0 = set(["__delay0"])
    set_d1 = set(["__delay1"])
    remove_able_label = set_epi | set_d0 | set_d1
    while loop:
        loop = False
        F : nx.DiGraph = nfa.G.copy()
        for node in F:
            if node == nfa.first_node:
                continue
            if node == nfa.last_node:
                continue
            succ_labels = set()
            for succ in F.successors(node):
                label = F.get_edge_data(node, succ)["label"]
                succ_labels |= label
            
            common = succ_labels & set_epi
            if common != set():
                assert common == set_epi
                for pre in F.predecessors(node):
                    label_pre = F.get_edge_data(pre, node)["label"]
                    if label_pre & remove_able_label != set():
                        nfa.remove_node(node)
                        loop = True
                        break

    return nfa

def nfa_node_rename(nfa, src_name, dst_name):
    """重命名 nfa 中某个节点的名字"""
    assert src_name in nfa.G
    assert dst_name not in nfa.G
    predecessors = nfa.G.predecessors(src_name)
    successors   = nfa.G.successors(src_name)
    for predecessor in predecessors:
        label = nfa.G.get_edge_data(predecessor,src_name)['label']
        nfa.G.add_edge(predecessor, dst_name,label = label)
    for successor in successors:
        label = nfa.G.get_edge_data(successor,src_name)['label']
        nfa.G.add_edge(successor, dst_name,label = label)
    nfa.G.remove_node(src_name)
    return nfa

def nfa_kill_to_lazy_kill(nfa):
    """好像没啥用了, 别调用"""
    assert False
    if need_kill:
        nfa_node_rename(nfa,'kill','lazy_kill')
    return nfa





def get_pos(G, first_node : str, last_node : str):
    """手动构造图 G 中节点的位置, 主要用于调试"""
    pos = nx.kamada_kawai_layout(G)
    node_list = [first_node]
    finded_node = []
    x_label = 0
    y_label = 0
    # 
    while(len(node_list) != 0):
        y_label = 0
        next_nodes = []
        for node in node_list:
            pos[node][0] = x_label
            pos[node][1] = y_label
            y_label += 1.5
            next_nodes += list(G.successors(node))
        finded_node += node_list
        node_list = []
        for next_node in next_nodes:
            if next_node not in finded_node:
                node_list += [next_node]
        x_label += 1
    pos[f'{last_node}'][0] = 6
    pos[f'{last_node}'][1] = 6
    if('kill' in pos):
        pos[f'kill'][0] = 4
        pos[f'kill'][1] = 6
    if('lazy_kill' in pos):
        pos[f'lazy_kill'][0] = 2
        pos[f'lazy_kill'][1] = -3
    return pos

def nfa_show( nfa : nfa_create):
    """展示 nfa, 主要用于调试"""
    if not isinstance(nfa.G, nx.MultiDiGraph):
        # nfa.clean(1)
        pass


    # 将 networkx 图转换为 pydot 图
    pydot_graph = nx.nx_pydot.to_pydot(nfa.G)

    # render the `pydot` by calling `dot`, no file saved to disk
    png_str = pydot_graph.create_png(prog='dot')

    # treat the DOT output as an image file
    sio = io.BytesIO()
    sio.write(png_str)
    sio.seek(0)
    img = mpimg.imread(sio)

    # plot the image
    imgplot = plt.imshow(img, aspect='equal')
    plt.show()




## ------------ test code ----------------

if __name__ == "__main__" :

    def test():
        """测试函数"""
        nfa = nfa_create()

        tests = [
            # ['constant_consecutive_repetition', 2,      'a'],
            # ['range_consecutive_repetition', 0, 1  , 'a'],
            # ['range_consecutive_repetition', 0, 2  , 'a'],
            # ['range_consecutive_repetition', 1, 3  , 'a'],
            # ['range_consecutive_repetition'   , 2, 5,   'b'],
            # ['range_consecutive_repetition'   , 3, '$',   'b'],
            # ['star_consecutive_repetition'    ,         'c'],
            # ['plus_consecutive_repetition'    ,         'd'],

            # ['constant_delay', [0]],
            # ['constant_delay', [1]],
            # ['constant_delay', [5]],
            # ['range_delay', 1, 3],
            ['star_delay'],
            # ['plus_delay'],


            # ['seq_cons_rep', 0],
            # ['seq_cons_rep', 1],
            # ['seq_cons_rep', 2],

            # ['seq_range_rep', 0,2],
            # ['seq_range_rep', 1,2],
            # ['seq_plus_rep'],
            # ['seq_star_rep'],

            # ['goto_const_rep', 0],
            # ['goto_const_rep', 1],
            # ['goto_const_rep', 2],
            # ['goto_range_rep', 0,2],
            # ['goto_range_rep', 1,2],
            # ['goto_range_rep', 0,'$'],
            # ['goto_range_rep', 1,'$'],

            # ['const_non_cons_rep',1],
            # ['const_non_cons_rep',2],


        ]
        temp = ['seq', 2,      ['a']]
        file_name = 'default'
        cnt = 0
        for test in tests:
            if 0 :
                pass
            elif test[0] == 'constant_consecutive_repetition' :
                nfa.create_constant_consecutive_repetition(test[0], test[1:2],test[2])
            elif test[0] == 'range_consecutive_repetition'  : 
                nfa.create_range_consecutive_repetition(test[0], test[1:3],test[3])
            elif test[0] == 'star_consecutive_repetition'   : 
                nfa.create_star_consecutive_repetition(test[0],[],test[1])
            elif test[0] == 'plus_consecutive_repetition'   : 
                nfa.create_plus_consecutive_repetition(test[0],[],test[1])
            elif test[0] == 'constant_delay' :
                nfa.create_constant_delay(test[0],test[1])
            elif test[0] == 'range_delay' :
                nfa.create_range_delay(test[0],test[1:3])
            elif test[0] == 'star_delay' :
                nfa.create_star_delay(test[0])
            elif test[0] == 'plus_delay':
                nfa.create_plus_delay(test[0])
            elif test[0] == 'seq_cons_rep':
                nfa.create_constant_consecutive_repetition(temp[0], temp[1:2],temp[2][0])
                create_sequence_constant_consecutive_repetition(nfa,[test[1]])
            elif test[0] == 'seq_range_rep':
                nfa.create_constant_consecutive_repetition(temp[0], temp[1:2],temp[2][0])
                create_sequence_range_consecutive_repetition(nfa,[test[1],test[2]])
            elif test[0] == 'seq_star_rep':
                nfa.create_constant_consecutive_repetition(temp[0], temp[1:2],temp[2][0])
                create_sequence_star_consecutive_repetition(nfa)
            elif test[0] == 'seq_plus_rep' :
                nfa.create_constant_consecutive_repetition(temp[0], temp[1:2],temp[2][0])
                create_sequence_plus_consecutive_repetition(nfa)
            elif test[0] == 'goto_const_rep' :
                nfa.create_constant_goto_repetition('goto_rep', test[1:2], 'X')
            elif test[0] == 'goto_range_rep' :
                nfa.create_range_goto_repetition('goto_rep', test[1:3], 'X')
            elif test[0] == 'const_non_cons_rep' :
                nfa.create_constant_non_consecutive_repetition('const_non_cons_rep', test[1:2], 'X')


            else:
                continue
            file_name = f'{cnt}_{test[0]}'
            cnt += 1
            nfa.clean(2)
            # nfa_show(nfa)
            pydot_graphic  = to_pydot(nfa.G)
            pydot_graphic.write(f'./output/img/{file_name}.png', format='png', prog="dot")

            ####
    test()


