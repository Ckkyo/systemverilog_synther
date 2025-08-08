import os.path
import os

import src.sva_synth as sva_synth
from src import gen_network

import argparse

def parse_args():
    parser = argparse.ArgumentParser(
        description="SVA综合工具: 将SVA文件转换为NFA、DFA及Verilog FSM"
    )
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument(
        "-f", "--file_", type=str, nargs='+', default=[],
        help="被综合的SVA文件路径( 可指定多个, 用空格分隔 ), NFA->DFA->Verilog FSM均会被生成"
    )
    input_group.add_argument(
        "-F", "--folder_", type=str, nargs='+', default=[],
        help="包含待综合SVA文件的文件夹(可指定多个, 用空格分隔), 文件夹下所有文件均会被综合"
    )
    parser.add_argument(
        "-o", "--output_", type=str, required=True,
        help="输出目录, 必须指定, 若不存在则会被创建。相对路径以python命令运行目录为根"
    )
    parser.add_argument(
        "--suffix_", type=str, nargs='+', default=['.sv', '.svh', '.svp', '.v'],
        help="需要解析的文件后缀, 在指定输入为文件夹的情况下会搜索相应后缀文件, 默认: .sv, .svh, .svp, .v"
    )
    # 限制图片格式为svg, png, jpg
    parser.add_argument(
        "--img_format", type=str, default="svg", choices=["svg", "png", "jpg"],
        help="生成图片的格式, 仅支持svg, png, jpg, 默认svg"
    )
    args = parser.parse_args()
    return args

def get_sva_files_path(args):
    current_dir = os.getcwd()
    sva_files_path = []
    # 如果以 -f 指定文件
    if args.file_:
        for f in args.file_:
            file_full_path = os.path.join(current_dir, f)
            if not os.path.exists(file_full_path):
                print(f"[Warning] 文件 {file_full_path} 不存在")
            print(f"待解析文件路径: {file_full_path} ")
            sva_files_path.append(file_full_path)
    # 如果以 -F 指定文件夹, 递归遍历文件夹及其所有子目录，搜索所有符合后缀的文件  
    if args.folder_:
        for folder in args.folder_:
            folder_full_path = os.path.join(current_dir, folder)
            if not os.path.exists(folder_full_path):
                print(f"[Warning] 文件夹 {folder_full_path} 不存在")
                continue
            print(f"待解析文件夹路径: {folder_full_path}")
            # 递归遍历所有子目录
            for root, dirs, files in os.walk(folder_full_path):
                for file in files:
                    # 检查文件后缀是否符合要求
                    if any(file.endswith(suffix) for suffix in args.suffix_):
                        file_path = os.path.join(root, file)
                        sva_files_path.append(file_path)
                        print(f"待解析文件路径: {file_path}")
    return sva_files_path

def main():
    args = parse_args()
    print(args)
    # 获取当前 python 的执行路径
    current_dir = os.getcwd()
    print(current_dir)

    sva_files_path = get_sva_files_path(args)
    # print(sva_files_path)
    # 获取输出文件夹路径
    output_dir = os.path.join(current_dir, args.output_)
    # 输出文件
    for sva_file_path in sva_files_path:
        sva_file_name = os.path.basename(sva_file_path)
        output_folder_path = os.path.join(output_dir, sva_file_name)
        print(f"输出文件夹路径: {output_folder_path}")
        # 创建输出文件夹
        os.makedirs(output_folder_path, exist_ok=True)
        # 创建输出文件
        sva_synth.sva_synth(sva_file_path, output_folder_path, sva_file_name)


if __name__ == "__main__":
    main()
