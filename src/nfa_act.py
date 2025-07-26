# import re
# import json
# from copy import deepcopy
# from functools import reduce
# from networkx.drawing.nx_pydot import to_pydot
# import networkx as nx

# from nfa_run import nfa_run_one_step
# from label_tools import clear_excl_mark_of_set
# from gen_network import nfa_create
# from label_tools import *


# def nfa_to_json(nfa : nfa_create, fpath = None):
#     """将 nfa 转换为 json"""
#     dic = {}
#     for node in nfa.G.nodes():
#         dic[node] = {}
#         for succ in nfa.G.successors(node):
#             dic[node][succ] = list(nfa.G[node][succ]['label'])
#     # 输出漂亮的 json 格式文件
#     if fpath is not None:
#         with open(fpath, 'w', encoding = "utf-8") as f:
#             json.dump(dic, f, indent=4,ensure_ascii=False)
#     return dic



# def nfa_to_dfa(nfa):
#     """将 nfa 转换为 dfa"""
#     TRUE_SET      = set(['__true'])
#     DELAY_1_SET   = set(['__delay1'])

#     debug_info = {}

#     cur_sts : list      = [set([nfa.first_node])] # 集合构成的列表
#     finded_sts : list   = [set([nfa.first_node])]
#     # nfa_path_labels     = set()

#     dfa = nfa_create() # dfa 只是 nfa 的一个子集, 因此直接使用 nfa_create 类型
#     idx = 0
#     dfa.first_node = '0'
#     dfa.first_nodes = ['0']
#     dfa.last_node = '-1'
#     dfa.last_nodes = ['-1']
#     dfa.G.add_node('0')
#     dfa.G.add_node('-1')
#     debug_info['0'] = set([dfa.first_node])
#     debug_info['-1'] = set([dfa.last_node])

#     assert nfa.first_node != nfa.last_node


#     while len(cur_sts) != 0:
#         next_sts = []
#         for cur_st in cur_sts:

#             for index,member in enumerate(finded_sts):
#                 if member == cur_st:
#                     cur_st_idx = index
#                     break

#             nfa_path_labels     = set()

#             nfa_run_one_step(nfa, cur_st, TRUE_SET, path_labels = nfa_path_labels)
#             # assert "__true" not in nfa_path_labels
            


#             if len(nfa_path_labels |  DELAY_1_SET | TRUE_SET) == 2:
#                 dfa_inputs : list = [set(['__delay1'])]
#             else:
#                 dfa_inputs : list = get_sub_sets_with_inv(nfa_path_labels - DELAY_1_SET - TRUE_SET)

#             # 为当前状态添加边和子节点
#             for dfa_input in dfa_inputs:
#                 # 搜索下一个状态
#                 next_st = nfa_run_one_step(nfa, cur_st, dfa_input)

#                 # 当前边没有子节点
#                 if next_st == set():
#                     continue
                
#                 # 发现了未出现过的新状态
#                 if next_st not in finded_sts:
#                     if nfa.last_node in next_st:
#                         pass
#                     else:
#                         finded_sts  += [next_st]
#                         next_sts    += [next_st]


#                 # 搜索 next_st 在 dfa 中的节点编号
#                 next_st_idx = -1 # 如果找不到就代表节点为 -1, 即 last_node
#                 for index,member in enumerate(finded_sts):
#                     if member == next_st:
#                         next_st_idx = index
#                         break

#                 if f"{next_st_idx}" in dfa.G.nodes():
#                     # 设置 dfa.G 节点 cur_st 到 next_st 节点的边
#                     dfa_input = clear_excl_mark_of_set(dfa_input)
#                     # 如果已存在边
#                     if dfa.G.has_edge(f'{cur_st_idx}',f'{next_st_idx}'):
#                         # 将边的 'label' 更改为 dfa_input
#                         dfa.G[f'{cur_st_idx}'][f'{next_st_idx}']['label'] = clear_excl_mark_of_set(dfa.G[f'{cur_st_idx}'][f'{next_st_idx}']['label'])
#                         dfa.G[f'{cur_st_idx}'][f'{next_st_idx}']['label'] &= dfa_input
#                     else:
#                         dfa.G.add_edge(f'{cur_st_idx}',f'{next_st_idx}',label=dfa_input)
#                 else:
#                     # 设置 dfa.G 节点 cur_st 到 next_st 节点的边
#                     dfa.G.add_edge(f'{cur_st_idx}',f'{next_st_idx}',label=dfa_input)

#             idx += 1
#         cur_sts = next_sts
#     # print(f"debug_info : {debug_info}" )
#     return dfa

# if __name__ == '__main__':
#     import os.path
#     import os
#     import sva_parser 

#     from ast_op import *
#     from gen_network import *

#     def test():

#         try:
#             os.mkdir('./output/img')
#         except:
#             pass


#         min = 0
#         max = 28
#         test_files = os.listdir('./test_files')
#         display = True
#         for test_file in test_files:
#             need_skip = True
#             for i in range(min, max + 1):
#                 if f'test{i}.sv' == test_file:
#                     need_skip = False
#             if need_skip:
#                 continue
#             with open(f'./test_files/{test_file}',mode='r',encoding="utf-8") as f_test:
#                 if display:
#                     print('\n\n\n\n\n')
#                 s = f_test.read()
#                 if display:
#                     print(s)
#                 ast = sva_parser.parser.parse(s)
#                 if display:
#                     print('---------------------- parser answer ----------------------')
#                 if display:
#                     print(f'file = {test_file}')
#                 if display:
#                     print(ast)
#                 nfa = depth_first_search(ast)
#                 nfa.clean(2)
#                 pydot_G = to_pydot(nfa.G)
#                 pydot_G.write_dot(f'./output/img/{test_file}_nfa.png', f='png')


#                 dfa = nfa_to_dfa(nfa)
#                 G = dfa.G
#                 pydot_G = to_pydot(G)
#                 pydot_G.write_dot(f'./output/img/{test_file}_dfa.png', f='png')
#                 print(dfa.last_nodes)
#                 pass
                
#     test()