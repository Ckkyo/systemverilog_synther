from tkinter import N
import networkx as nx

class OperatorCreate():
    """生成一个操作符节点"""
    def __init__(self,op_type :str, value = None):
        self.op_type : str = op_type
        self.value : list  = value if isinstance(value, list) else []
        assert self.op_type is not None
    def get_op_type(self) -> str:
        """获取操作符类型"""
        return self.op_type
    def get_op_value(self) -> list:
        """获取操作符值"""
        return self.value
    

class AstCreate():
    """用 nx.DiGraph 生成一个 ast 节点"""
    def __init__(self,  ast_type : str,         op : OperatorCreate | None = None,
                        sub_asts : list | None = None, name : str = ''):
        self.ast_type   = ast_type
        self.op         = op if op is not None else None
        self.sub_asts   = sub_asts if sub_asts is not None else []
        self.name       = name if name is not None else ''
        assert isinstance(self.ast_type, str)

    def get_ast_type (self) -> str:
        """获取 ast 类型"""
        return self.ast_type
    def get_op (self) -> OperatorCreate | None:
        """获取 ast 操作符"""
        return self.op
    def get_sub_asts (self) -> list:
        """获取 ast 子节点"""
        return self.sub_asts
    def get_name (self) -> str:
        """获取 ast 名称"""
        return self.name

    def ast_gen_g( self ):
        """生成 ast 的图"""
        def inner(ast,x,y):

            g_inner = nx.DiGraph()
            if ast.ast_type == 'expression':
                first_node = f'{ast.name}_{x}_{y}'
                y += 1
                return [g_inner,x,y,first_node]

            first_node = f'{ast.ast_type}_{x}_{y}'
            g_inner.add_node(first_node)
            y += 1
            if ast.op is not None:
                g_inner.add_node(f'{ast.op.get_op_type()}_{x+1}_{y}')
                g_inner.add_edge(first_node, f'{ast.op.get_op_type()}_{x+1}_{y}')
                y += 1

            for _,sub_ast in enumerate(ast.sub_asts):
                ret = inner(sub_ast, x + 1 , y)
                g_inner = nx.compose(g_inner,ret[0])
                g_inner.add_edge(first_node, ret[3])
                y = ret[2]

            return [g_inner,x,y,first_node]
        x = 0
        y = 0
        return inner(self, x, y)[0]
    
