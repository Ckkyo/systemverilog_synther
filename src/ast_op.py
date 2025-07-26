"""
提供一些操作 ast 的函数
"""

from networkx.drawing.nx_pydot import to_pydot

import gen_network
# from sva_ast import OperatorCreate
from sva_ast import AstCreate



def depth_first_search(ast) -> gen_network.nfa_create:
    """通过深度优先算法将 ast 转换为 nfa 状态机"""
    search_count = 0
    def inner(ast : AstCreate) -> gen_network.nfa_create:
        nonlocal search_count
        ast_type     = ast.get_ast_type()
        sub_asts     = ast.get_sub_asts()
        sub_asts_nfa = []

        assert( 'property_expr' in ast_type or 'sequence_expr' in ast_type or 'expression_or_dist' in ast_type \
                or 'empty' in ast_type)

        for _,sub_node in enumerate(sub_asts):
            sub_ast_type = sub_node.ast_type
            if sub_ast_type != 'expression_or_dist':
                sub_asts_nfa += [inner(sub_node)]
                # gen_network.nfa_show(sub_asts_nfa[idx])

        nfa = gen_network.nfa_create()
        if ast_type == 'sequence_expr' :
            ast_op = ast.get_op()
            assert ast_op is not None
            ast_op_type  = ast_op.get_op_type()
            ast_op_value = ast_op.value
            try:
                create_func = getattr(nfa, f'create_{ast_op_type}') # 获取 nfa 中对应的函数
            except:
                create_func = None
            base_name = f'{search_count}_{ast_op_type}'
            if False:
                pass
            elif 'repetition' in ast_op_type:
                assert create_func is not None
                # The issue was added to the bug tracker: 我也不记得这里错了啥
                sub_node = sub_asts[0]  # 对于 repetition 系列的 ast_op_type, 一定只有一个 sub_node
                                        # 而且 sub_node 对应的 type 一定是 expression_or_dist
                expression_or_dist = sub_node.sub_asts[0].name
                create_func(base_name, ast_op_value, expression_or_dist)
            elif 'delay' in ast_op_type or 'or' in ast_op_type or 'and' in ast_op_type or 'intersect' in ast_op_type \
                or 'within' in ast_op_type :
                # 对于 delay 系列的 ast_op_type, 一定有两个 sub_node(其中一个可能完全由 __episilon 构成)
                # 如果执行到这一步, 代表已经获取到 sub_asts_nfa 中所需的信息了
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                if 'delay' in ast_op_type:
                    assert create_func is not None
                    create_func(base_name, ast_op_value)
                    sub_node0_nfa.nfa_concat(nfa)
                    sub_node0_nfa.nfa_concat(sub_node1_nfa)
                    nfa = sub_node0_nfa
                elif 'or' in ast_op_type:
                    nfa = gen_network.nfa_or(sub_node0_nfa, sub_node1_nfa)
                elif 'and' in ast_op_type:
                    nfa = gen_network.nfa_and(sub_node0_nfa, sub_node1_nfa)
                elif 'intersect' in ast_op_type:
                    nfa = gen_network.nfa_intersect(sub_node0_nfa, sub_node1_nfa)
                elif "within" in ast_op_type:
                    nfa = gen_network.nfa_within(sub_node0_nfa, sub_node1_nfa)
                    
            elif "throughout" in ast_op_type:
                # throughout 左边是 expression_or_dist, 右边是 seq expr
                # # 取出表达式
                sub_node = sub_asts[0]  
                expression_or_dist = sub_node.sub_asts[0].name
                # # 取出 sub nfa
                sub_node0_nfa = sub_asts_nfa[0]
                # # 生成
                nfa = gen_network.nfa_throughout(expression_or_dist, sub_node0_nfa)
            elif "first_match" in ast_op_type:
                # nfa = gen_network.nfa_to_dfa()
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node0_dfa = gen_network.nfa_to_dfa(sub_node0_nfa.normal())
                nfa = sub_node0_dfa.to_digraph()
                pass
            else:
                assert False
                nfa.create_empty_graph(f'{search_count}_empty')

        elif ast_type == 'sequence_expr_delay_before_expr':
            ast_op      = ast.get_op()
            assert ast_op is not None
            ast_op_type = ast_op.get_op_type()
            ast_op_value= ast_op.value
            create_func = getattr(nfa, f'create_{ast_op_type}') # 获取 nfa 中对应的函数
            base_name = f'{search_count}_{ast_op_type}'

            sub_node0_nfa = sub_asts_nfa[0]
            sub_node1_nfa = sub_asts_nfa[1]

            nfa_temp0 = gen_network.create_empty_graph(None, f'{base_name}_empty0')
            nfa_temp1 = gen_network.create_empty_graph(None, f'{base_name}_empty1')
            if   ast_op_type == 'constant_delay':
                nfa_temp0 = gen_network.create_constant_consecutive_repetition\
                    (None, f'{base_name}_0', ast_op_value, '__delay1')
                nfa_temp1 = gen_network.create_delay1_graph(None, f'{base_name}_1')
            elif ast_op_type == 'range_delay' :
                nfa_temp0 = gen_network.create_range_consecutive_repetition\
                    (None, f'{base_name}_0', ast_op_value, '__delay1')
                nfa_temp1 = gen_network.create_delay1_graph(None, f'{base_name}_1')
            elif ast_op_type == 'star_delay'  :
                nfa_temp0 = gen_network.create_range_consecutive_repetition\
                    (None, f'{base_name}_0', [0, '$'], '__delay1')
            elif ast_op_type == 'plus_delay'  :
                nfa_temp0 = gen_network.create_range_consecutive_repetition\
                    (None, f'{base_name}_0', [1, '$'], '__delay1')
            nfa = gen_network.nfa_concat(nfa_temp0, nfa_temp1)
            nfa = gen_network.nfa_concat(nfa, sub_node1_nfa)
        elif ast_type == "property_expr":
            ast_op = ast.get_op()
            assert ast_op is not None
            ast_op_type  = ast_op.get_op_type()
            ast_op_value = ast_op.value
            # create_func = getattr(nfa, f'create_{ast_op_type}') # 获取 nfa 中对应的函数
            # base_name = f'{search_count}_{ast_op_type}'
            if False:
                pass
            elif ast_op_type == 'not'  :
                assert len(sub_asts_nfa) == 1
                nfa = sub_asts_nfa[0]
                nfa = gen_network.nfa_not(nfa)
            elif ast_op_type == 'overlap_implication':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_overlap_implication(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'non_overlap_implication':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_non_overlap_implication(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'overlap_follow_by':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_overlap_follow_by(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'non_overlap_follow_by':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_non_overlap_follow_by(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'until':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_until(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'until_with':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_until_with(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'always':
                sub_node0_nfa = sub_asts_nfa[0]
                nfa = gen_network.nfa_always(sub_node0_nfa)
            elif ast_op_type == 'implies':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_implies(sub_node0_nfa, sub_node1_nfa)
            elif ast_op_type == 'iff':
                sub_node0_nfa = sub_asts_nfa[0]
                sub_node1_nfa = sub_asts_nfa[1]
                nfa = gen_network.nfa_iff(sub_node0_nfa, sub_node1_nfa)
            else:
                assert False

        elif ast_type == 'empty':
            nfa.create_delay0_graph(f'{search_count}_empty')
        else:
            assert False
            nfa.create_empty_graph('temp1')

        search_count += 1
        assert nfa.first_node is not None
        return nfa

    nfa = inner(ast)

    return nfa





def cur_module_test():
    """测试当前模块的代码"""
    #['sequence_expr', ['range_delay', [1, 3]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['!a']], ['sequence_expr', ['constant_delay', [10]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['b']], ['sequence_expr', ['constant_delay', [1]], ['sequence_expr', ['star_consecutive_repetition', 0], ['c']], ['sequence_expr', ['range_consecutive_repetition', [1, 3]], ['d']]]]]

    ast = ['sequence_expr', ['range_delay', [1, 3]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['expression_or_dist', ['__nope', [0]], ['!a']]], ['sequence_expr', ['constant_delay', [2]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['expression_or_dist', ['__nope', [0]], ['b']]], ['sequence_expr', ['constant_delay', [1]], ['sequence_expr', ['star_consecutive_repetition', [0]], ['expression_or_dist', ['__nope', [0]], ['c']]], ['sequence_expr', ['range_consecutive_repetition', [1, 3]], ['expression_or_dist', ['__nope', [0]], ['d']]]]]]
    ast = ['sequence_expr', ['range_delay', [1, '$']], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['expression_or_dist', ['__nope', [0]], ['!a']]], ['sequence_expr', ['constant_delay', [3]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['expression_or_dist', ['__nope', [0]], ['b']]], ['sequence_expr', ['constant_consecutive_repetition', [1]], ['expression_or_dist', ['__nope', [0]], ['c']]]]]

    nfa = depth_first_search(ast)




    pydot_graphic = to_pydot(nfa.G)
    pydot_graphic.write('./output/oriG.png', format='png', prog="dot")
    nfa.clean(1)
    pydot_graphic = to_pydot(nfa.G)
    pydot_graphic.write('./output/G.png', format='png', prog="dot")

    # gen_network.nfa_show(nfa)

if __name__ == '__main__':
    cur_module_test()
