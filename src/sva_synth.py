import os
import sys
import shutil
import argparse
import networkx as nx
from networkx.drawing.nx_pydot import to_pydot

import sva_ast
import sva_parser
import ast_op
import gen_network
import gen_network
import sva_to_sv


def sva_synth(source_file_path, output_dir, tar_file_root_name) -> dict:
    """将 sva 转换为 sv 状态机以及生成中间一系列文件
    生成的 sv 模块名为 {tar_file_root_name}, 文件名为 {tar_file_root_name}.sv
    """
    mod_dir = os.path.dirname(__file__)

    source_file_content : str

    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    tar_file_root_path = f"{output_dir}/{tar_file_root_name}"
    
    ast_img_path = f'{tar_file_root_path}.ast.png'

    nfa_img_path  = f'{tar_file_root_path}.nfa.png'
    nfa_json_path = f'{tar_file_root_path}.nfa.json'

    nfa_renamed_img_path  = f'{tar_file_root_path}.renamed.nfa.png'
    nfa_renamed_json_path = f'{tar_file_root_path}.renamed.nfa.json'

    dfa_img_path  = f'{tar_file_root_path}.dfa.png'
    dfa_json_path = f'{tar_file_root_path}.dfa.json'

    dfa_digraph_img_path  = f'{tar_file_root_path}.dfa_digraph.png'
    dfa_digraph_json_path = f'{tar_file_root_path}.dfa_digraph.json'

    sv_path    = f'{tar_file_root_path}.sv'
    sv_module_name = tar_file_root_name
    sv_tb_path = f'{tar_file_root_path}.tb.sv'
    tb_filelist_path = f'{tar_file_root_path}.fl'

    tpls_dir = f"{mod_dir}/template"
    sv_tpl_path = f"{tpls_dir}/sva_fsm.tpl.sv"
    tb_tpl_path = f"{tpls_dir}/tb_dfa.tpl.sv"
    

    # 检查目标生成路径是否存在
    if not os.path.exists(output_dir):
        print(f"[Info] create directory : {output_dir}")
        try:
            os.makedirs(output_dir)
        except BaseException:
            print(f"[Error] can not create directory : {output_dir}")
            sys.exit(-1)

    # 读取源文件
    try:
        with open(source_file_path,"r",encoding='utf-8') as fp:
            source_file_content = fp.read()
    except RuntimeError:
        print(f"[Error] not such file or directory : {source_file_path}")
        sys.exit(-1)

    # 生成 ast
    print(f"\n[Info] 正在生成 ast ")
    ast : sva_ast.AstCreate = sva_parser.parser.parse(source_file_content)
    ast_G = ast.ast_gen_g()
    pydot_graphic = to_pydot(ast_G)
    pydot_graphic.write(ast_img_path, format='png', prog="dot")
    print(f"[Info] ast 图生成路径 : {ast_img_path}")


    # 生成 nfa
    print(f"\n[Info] 正在生成 nfa ")
    nfa : gen_network.nfa_create = ast_op.depth_first_search(ast)
    # nfa.nfa_show()
    nfa.normal()
    nfa.clean(2)
    # nfa.nfa_show()
    pydot_graphic  = to_pydot(nfa.G)
    pydot_graphic.write(nfa_img_path, format='png', prog="dot")
    gen_network.nfa_to_json(nfa,nfa_json_path)
    print(f"[Info] nfa 图生成路径 : {nfa_img_path}")
    print(f"[Info] nfa json 路径 : {nfa_json_path}")
    # 生成 rename 后的 nfa, 方便展示
    nfa_renamed = nfa.copy()
    nfa_renamed.last_nodes = []
    nfa_renamed.first_nodes = []
    gen_network.rename_to_number(nfa_renamed)
    nfa_renamed.clean(2)
    pydot_graphic  = to_pydot(nfa_renamed.G)
    pydot_graphic.write(nfa_renamed_img_path, format='png', prog="dot")
    gen_network.nfa_to_json(nfa_renamed,nfa_renamed_json_path)
    print(f"[Info] nfa_renamed 图生成路径 : {nfa_renamed_img_path}")
    print(f"[Info] nfa_renamed json 路径 : {nfa_renamed_json_path}")

    # 生成 dfa
    print(f"\n[Info] 正在生成 dfa ")
    dfa = gen_network.nfa_to_dfa(nfa)
    pydot_graphic  = to_pydot(dfa.G)
    pydot_graphic.write(dfa_img_path, format='png', prog="dot")
    gen_network.nfa_to_json(dfa,dfa_json_path)
    print(f"[Info] dfa 图生成路径 : {dfa_img_path}")

    # 生成 dfa_digraph
    dfa_digraph = dfa.copy()
    dfa_digraph.to_digraph()
    pydot_graphic  = to_pydot(dfa_digraph.G)
    pydot_graphic.write(dfa_digraph_img_path, format='png', prog="dot")
    gen_network.nfa_to_json(dfa_digraph,dfa_digraph_json_path)
    print(f"[Info] dfa_digraph 图生成路径 : {dfa_digraph_img_path}")

    # 生成 sv 状态机
    print(f"\n[Info] 正在生成 sv 状态机 ")
    sva_to_sv.dfa_to_sv(dfa_json_path,sv_path,sv_tb_path,sv_module_name,sv_tpl_path,tb_tpl_path)
    with open(tb_filelist_path,"w",encoding="utf-8") as fp:
        fp.write(f"${{FILE_LIST_DIR}}/{os.path.basename(sv_path)}\n" )
        fp.write(f"${{FILE_LIST_DIR}}/{os.path.basename(sv_tb_path)}\n" )
    print(f"[Info] sv 路径 : {sv_path}")
    print(f"[Info] tb(只用于测试) 路径 : {sv_tb_path}")
    print(f"[Info] filelist(只用于测试) 路径 : {tb_filelist_path}")

    print(f"nfa 状态数量 {len(nfa.G)} dfa 状态数量 {len(dfa.G)}")

    return {"nfa":nfa,"dfa":dfa, "dfa_digraph":dfa_digraph}

if __name__ == "__main__":
    mod_running_dir = os.getcwd()
    mod_path         = __file__
    # print(mod_running_dir)
    # print(mod_path)

    parser = argparse.ArgumentParser(description='帮助')
    # 添加参数
    # -f/--file 是一个可选参数，需要一个文件路径
    parser.add_argument('-f', '--source_file_path'     , type=str  , required=True             , help='输入文件的路径')
    parser.add_argument('-od','--output_dir'        ,type=str   , default=mod_running_dir   ,help="目标输出文件夹")
    parser.add_argument('-o','--tar_file_root_name' ,type=str   , default="sva_o"           ,help="输出文件根名称")
    
    # 解析参数
    args = parser.parse_args()
    print(args.source_file_path)

    if args.source_file_path:
        print(f"输入文件路径：{args.source_file_path}")
        source_file_path = args.source_file_path
    else:
        assert False
    
    if args.output_dir:
        print(f"输出文件目录：{args.output_dir}")
        output_dir = args.output_dir
    else:
        assert False
    
    if args.tar_file_root_name:
        print(f"输出文件根名称：{args.tar_file_root_name}")
        tar_file_root_name = args.tar_file_root_name
    else:
        assert False
    
    sva_synth(source_file_path, output_dir, tar_file_root_name)
