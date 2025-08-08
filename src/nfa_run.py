# import networkx as nx
# import matplotlib.pyplot as plt
# import graphviz as gz
import enum
from typing import TYPE_CHECKING
from networkx.drawing.nx_pydot import to_pydot
from .label_tools import *

if TYPE_CHECKING:
    from .gen_network import nfa_create
nfa_run_debug = False
report_status = False

def check_node_has_label(G, node, label) -> set:
    """检查图 G 的节点 node 到其后继是否有特定 label"""
    return_node_set = set()
    if node == '0_constant_goto_repetition1_epi0' :
        pass
    for successor in G.successors(node):
        if label == G.get_edge_data(node, successor)['label']:
            return_node_set |=set([successor])
    return return_node_set



def nfa_run_one_step(nfa: "nfa_create", cur_st: set, input_set: set, iter_ = False, fd = None, path_labels = set()):
    next_st = set()
    cur_st_loop = cur_st.copy()
    while(len(cur_st_loop) != 0):
        cur_st_temp = set()
        for node in cur_st_loop:
            if node == 'kill':
                continue
            elif node == 'lazy_kill':
                pass
                continue
            elif node == nfa.last_node:
                # next_st |= set([node])
                continue
            
            
            
            for successor in nfa.G.successors(node):
                label = nfa.G.get_edge_data(node, successor)['label']
                
                if '__delay0' in label:
                    # 如果 label 为 delay0, 则代表在当前的输入情况下 successor 状态开始再执行一次 nfa_run_one_step, 并且这次执行的状态
                    # 到 next_st 中
                    next_st |= nfa_run_one_step(nfa, [successor], input_set,path_labels=path_labels)
                else:
                    suspect_next_st_set = set() # 匹配了的 successor 并不全是 next_st, 要对 successor 的下一级进行检测查看是否有 __delay0
                    suspect_next_st_set_is_iter = {}

                    if '__episilon' in label:
                        cur_st_temp |= set([successor])
                    elif '__true' in label:
                        suspect_next_st_set |= set([successor])
                        path_labels |= set(['__true'])
                    elif '__delay1' in label:
                        suspect_next_st_set |= set([successor])
                        path_labels |= set(['__delay1'])
                    else:

                        label = clear_excl_mark_of_set(label)
                        input_set = clear_excl_mark_of_set(input_set)
                        if '__true' in input_set or "__delay1" in input_set:
                            suspect_next_st_set |= set([successor])
                            path_labels |= label
                        else:
                            
                            
                            if len(label) == len(label & input_set) :
                                suspect_next_st_set |= set([successor])
                                # 只保留真条件
                                path_labels |= label
                
                    suspect_next_st_list = list(suspect_next_st_set)
                    while len(suspect_next_st_list) != 0:
                        
                        delay0_nodes = check_node_has_label(nfa.G, suspect_next_st_list[-1],set(['__delay0']))
                        epi_nodes    = check_node_has_label(nfa.G, suspect_next_st_list[-1],set(['__episilon']))
                        
                        suspect_next_st = suspect_next_st_list.pop()
                        if(len(delay0_nodes) == 0 and len(epi_nodes) == 0):
                            next_st |= set([suspect_next_st])
                            continue 
                        
                        for delay0_node in delay0_nodes:
                            # delay0_node 可能是终点, 如果是终点则直接添加到 next_st 中
                            if delay0_node == nfa.last_node:
                                next_st |= set([nfa.last_node])
                                continue
                            next_st |= nfa_run_one_step(nfa, [delay0_node], input_set,path_labels=path_labels)
                        for epi_node in epi_nodes:
                            # 不会有 episilon 环
                            if epi_node == suspect_next_st:
                                assert False
                            
                        suspect_next_st_list += list(epi_nodes)

        cur_st_loop = cur_st_temp
    return next_st

def nfa_run_n_step(nfa, cur_st , input_lists , times):
    """nfa 从状态 cur_st 向后运行 n 次"""
    cst = cur_st.copy()
    for i,_ in enumerate(input_lists):
        if i > times - 1 :
            break 
        # 打断点用
        if i == 0:
            pass
        print(f'run times = {i}')
        input_set = input_lists[i]
        next_st = nfa_run_one_step(nfa, cst, input_set)
        cst = next_st
    return next_st

def nfa_run_n_step_multi_thread(nfa: "nfa_create", cur_st , input_lists , times, fd = None):
    """nfa 从状态 cur_st 向后运行 n 到 1 次
    第一次循环开始 : next_st_list = [cur_st]
    第二次循环开始 : next_st_list = [cur_st, nfa_run_n_step(nfa,cur_st, input_lists,times = 1)]
    第二次循环开始 : next_st_list = [cur_st, nfa_run_n_step(nfa,cur_st, input_lists,times = 2), nfa_run_n_step(nfa,cur_st, input_lists,times = 1)]
    """
    cst = cur_st.copy()
    next_st_list = [cst]
    
    for i, _ in enumerate(input_lists):
        if report_status:
            # 获得 next_st_list 的非空集合
            report_st_list = [x for x in next_st_list if len(x) != 0]
            # print(f'# 当前状态 : {report_st_list}\n')
            fd.write(f'# 当前状态 : {report_st_list}\n')

        if i > times - 1 :
            break 
        s = f'run times = {i}\n'
        if fd is None:
            print(s)
        else:
            fd.write(s)

        input_set = set(input_lists[i])
        remove_idx_list = []
        # xxx 在执行断言的时候, 如果开始于不同时刻的序列结束于相同时刻, 则只会执行一次 action_block, 且 else 优先
        do_if_action_block0 = False
        do_else_action_block1 = False
        for idx, _ in enumerate(next_st_list):
            st = next_st_list[idx]
            # # 打断点用
            # if(i >= 0):
            #     if(idx == 56):
            #         pass
            #     pass
            
            if(len(st) != 0):
                path_labels = set()
                next_st = nfa_run_one_step(nfa, st, input_set , fd = fd,path_labels = path_labels)
                if nfa_run_debug:
                    print(f'at {i} {idx} through path = {path_labels}')
                if(len(next_st) == 0):
                    if nfa_run_debug : 
                        print(f'at time {i} idx {idx} cal error')
                    do_else_action_block1 = True

                    s = f'error\n'
                    fd.write(s)
                else:
                    if nfa.last_node in next_st:
                        if nfa_run_debug : 
                            print(f'at time {i} idx {idx} cal finish')
                        do_if_action_block0 = True 
                        next_st = set()

                        s = f'finish\n'
                        fd.write(s)
                    elif nfa.lazy_last_node in next_st:
                        next_st = set()
            else:
                next_st = set()
            next_st_list[idx] = next_st
        
        # if do_else_action_block1 or do_if_action_block0:
            
        #     if (do_else_action_block1):
        #         s = f'error\n'
        #         fd.write(s)
        #         # next_st_list = [[]] * len(next_st_list)
        #     elif (do_if_action_block0):
        #         s = f'finish\n'
        #         fd.write(s)
        next_st_list.append([nfa.first_node])


    return next_st

class nfa_runner_create():
    """nfa 运行器类, 保存一个 nfa, 并且保存当前状态和运行次数"""
    def __init__(self, nfa):
        self.nfa    = nfa
        self.cur_st = set([nfa.first_node])
        self.run_times = 0
    
    def nfa_run_one_step(self, input_set : list):
        self.cur_st = nfa_run_one_step(self.nfa, self.cur_st, input_set)

    def nfa_run_n_step(self, input_lists , times):
        self.cur_st = nfa_run_n_step(self.nfa, self.cur_st , input_lists , times)
        self.run_times += times

    def nfa_run_n_step_multi_thread(self, input_lists , times, fd = None):
        self.cur_st = nfa_run_n_step_multi_thread(self.nfa, self.cur_st , input_lists , times, fd)
        self.run_times += times

if __name__ == '__main__':
    from gen_network import *
    def test():
        """测试"""

        nfa        = nfa_create()

        tests = [
            ['goto_const_rep', 0],
            ['goto_const_rep', 1],
            ['goto_const_rep', 2],
            ['goto_range_rep', 0,2],
            ['goto_range_rep', 1,2],
            ['goto_range_rep', 0,'$'],
            ['goto_range_rep', 1,'$'],
        ]
        file_name = 'default'
        cnt = 0
        for t in tests:
            if False:
                pass
            elif t[0] == 'goto_const_rep' :
                nfa.create_constant_goto_repetition('goto_rep', t[1:2], 'X')
            elif t[0] == 'goto_range_rep' :
                nfa.create_range_goto_repetition('goto_rep', t[1:3], 'X')
            else:
                continue

            

            file_name = f'{cnt}_{test[0]}'

            nfa.clean(1)
            # nfa_show(nfa)

            pydot_graphic  = to_pydot(nfa.G)
            pydot_graphic.write(f'./output/img/{file_name}.png', format='png', prog="dot")

            input_lists = [
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['X'],
                ['__delay1'],

                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['X'],
                ['__delay1'],

                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['!X'],
                ['__delay1'],
                ['X'],
                ['__delay1'],

                ['!X'],
                ['__delay1'],
            ]
            times = 32

            print(' -----------------------------------\n')
            nfa_runner = nfa_runner_create(nfa)
            nfa_runner.nfa_run_n_step(input_lists, times)
            print('\n\n\n\n')

            cnt += 1
    test()
