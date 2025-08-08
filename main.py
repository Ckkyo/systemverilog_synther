import os.path
import os

import src.sva_synth as sva_synth
from src import gen_network

DISPLAY = True

def main_nfa_run(min_test_id,max_test_id, test_tar : str = "nfa",):
    """
    遍历指定的测试文件, 为每个测试文件生成 ast, 将 ast 输入 nfa 生成器
    Parameters
    ----------
    min_test_id : int
        最小测试编号
    max_test_id : int
        最大测试编号
    """

    mod_dir = os.path.dirname(__file__)
    mod_dir_linux = "/home/summer/prj/sva_synth/python/lex"
    for i in range(min_test_id, max_test_id + 1):
        test_file_name = f"test{i}"

        test_file_path = f"{mod_dir}/test_files/{test_file_name}.sv"
        output_dir = f"{mod_dir}/output/test{i}"

        test_file_path_linux = f"{mod_dir_linux}/test_files/{test_file_name}.sv"
        output_dir_linux = f"{mod_dir_linux}/output/test{i}"

        # 生成 sv 以及全部中间文件, 输出结果在 output_dir
        sva_synth_ret_val = sva_synth.sva_synth(test_file_path, output_dir, test_file_name)


if __name__ == "__main__":
    # test_cases = [(401, 401)]
    # for test_case in test_cases:
    #     (TEST_MIN, TEST_MAX) = test_case
    #     main_nfa_run(TEST_MIN, TEST_MAX,test_tar="dfa")

    test_cases = [(0,30), (100,133)]
    # test_cases = [(17, 17)]
    for test_case in test_cases:
        (TEST_MIN, TEST_MAX) = test_case
        main_nfa_run(TEST_MIN, TEST_MAX,test_tar="dfa")
