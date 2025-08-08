import sys

from src import gen_network
# sys.path.append("./src")

import os.path
import os
# 用于远程 ssh 访问虚拟机
import paramiko

import src.sva_synth as sva_synth
import src.nfa_run as nfa_run

DISPLAY = True
#       0                   1                   2
#       3                   4                   5
#       6

a = [   1,0,0,0,1,0,0,0,1,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,
        0,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,
        1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,
        1,0,1,0,1,0,1,0
        ]
b = [   1,1,0,0,0,0,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,0,1,
        0,1,0,1,0,0,0,0,0,1,1,1,0,1,0,1,0,1,0,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0,1,0,0,0,0,1,1,0,0,0,1,0,0,0,0,1,0,0,0,0,1,0,
        0,0,0,1,0,0,0,0
        ]
c = [   1,1,1,1,1,0,1,1,1,1,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,0,0,0,0,0,1,1,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,0,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1
        ]
d = [   1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
        1,1,1,1,1,1,1,1
        ]


def get_inputlist():
    """获取输入列表"""
    input_lists_ = []
    for (i,_) in enumerate(a):
        input_list = []
        if a[i]:
            input_list.append('a')
        else :
            input_list.append('!a')
        if b[i]:
            input_list.append('b')
        else :
            input_list.append('!b')
        if c[i]:
            input_list.append('c')
        else :
            input_list.append('!c')
        if d[i]:
            input_list.append('d')
        else :
            input_list.append('!d')
        input_lists_.append(input_list.copy())
    return input_lists_
# input_lists = get_inputlist()

def log_parser(log_ori : list) -> dict: # {time : {answer : times}}
    """解析打印的 log"""
    # 去除空白行和注释开头的行
    remove_commond_and_blank = [x for x in log_ori if x != '' and not x.startswith('#')]
    ret_val = {}
    time = None
    for elem in remove_commond_and_blank:
        if "run times" in elem:
            time = int(elem.split("=")[-1].strip())

        if time == None:
            continue
        if time not in ret_val:
            ret_val[time] = {"finish":0,"error":0}
        elif "finish" in elem:
            ret_val[time]["finish"] += 1
        elif "error" in elem:
            ret_val[time]["error"] += 1
    return ret_val
def check_log(log0 : list | str, log1: list | str) -> bool:
    if isinstance(log0, str):
        with open(log0, 'r', encoding='utf-8') as f:
            nfa_log_ori = f.readlines()
    else:
        nfa_log_ori = log0
    if isinstance(log1, str):
        with open(log1, 'r', encoding='utf-8') as f:
            sim_log_ori = f.readlines()
    else:
        sim_log_ori = log1
    
    parsed_nfa_log = log_parser(nfa_log_ori)
    parsed_sim_log = log_parser(sim_log_ori)
    no_error = True
    for key, value in parsed_nfa_log.items():
        assert key in parsed_sim_log
        no_error &= value["finish"] == parsed_sim_log[key]["finish"]
        no_error &= value["error"]  == parsed_sim_log[key]["error"]
        if not no_error:
            print(f"Dont Match At time = {key} : {log0} {log1}")
            break
    return no_error

class SummerSSH():
    """创建一个固定连接到summer的类"""
    # SSH连接参数
    HOSTNAME = "192.168.1.105"  # 远程主机的IP地址或域名
    PORT = 22  # SSH端口，默认为22
    USERNAME = "summer"  # SSH用户名
    PASSWORD = "815521"  # SSH密码

    # 创建SSH客户端对象
    ssh_client = paramiko.SSHClient()

    # 自动添加主机密钥 (不安全，请根据需求修改)
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    def connect(self):
        """连接到远程主机"""
        SummerSSH.ssh_client.connect(SummerSSH.HOSTNAME, SummerSSH.PORT, SummerSSH.USERNAME, SummerSSH.PASSWORD)
    
    # 断开连接
    def close(self):
        """断开远程连接"""
        SummerSSH.ssh_client.close()
    
    def run_cmd(self, cmd, silent = False):
        """通过 ssh 在远程主机运行命令"""
        stdin, stdout, stderr = SummerSSH.ssh_client.exec_command(cmd)
        # print(f"stdin: {stdin}\nstdout: {stdout}\nstderr: {stderr}")
        s = stdout.read().decode('utf-8') # 阻塞
        s += stderr.read().decode('utf-8')
        if not silent:
            print(f"[Info] run ssh cmd : {cmd}")
            # print(s)
        return s

def main_nfa_run(min_test_id,max_test_id, test_tar : str = "nfa", simulation=False):
    """
    遍历指定的测试文件, 为每个测试文件生成 ast, 将 ast 输入 nfa 生成器
    Parameters
    ----------
    min_test_id : int
        最小测试编号
    max_test_id : int
        最大测试编号
    """
    if simulation:
        ssh_summer = SummerSSH()
        ssh_summer.connect()

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

        ori_sim_log_path    = f"{output_dir}/{test_file_name}.ori.log"
        nfa_log_path        = f"{output_dir}/{test_file_name}.nfa.log"
        dfa_log_path        = f"{output_dir}/{test_file_name}.dfa.log"
        sv_sim_log_path     = f"{output_dir}/{test_file_name}.log"

        if simulation:
            # 仿真原始文件
            ssh_summer.run_cmd(f"clear;clear;cd {mod_dir_linux}/sim/sim && rm -rf ~/sva_synth_sim_work/vcs && \
                            SIM=vcs make sim_vcs FILE_LIST_PATH={mod_dir_linux}/sim/sim/filelist.f \
                                SV_LOG_FILE_PATH={output_dir_linux}/{test_file_name}.ori.log \
                                FILE_LIST_DIR={mod_dir_linux}/sim/sim/\
                                TEST_CASE={test_file_name} > {output_dir_linux}/{test_file_name}.vcs.ori.log")
        
            input_lists = get_inputlist()
            nfa_run.report_status = True

            nfa = sva_synth_ret_val["nfa"]
            nfa_runner = nfa_run.nfa_runner_create(nfa)
            with open (f"{output_dir}/{test_file_name}.nfa.log", "w", encoding="utf-8") as f:
                nfa_runner.nfa_run_n_step_multi_thread(input_lists,len(input_lists),f)

            dfa : gen_network.nfa_create = sva_synth_ret_val["dfa_digraph"]
            dfa_runner = nfa_run.nfa_runner_create(dfa)
            with open (f"{output_dir}/{test_file_name}.dfa.log", "w", encoding="utf-8") as f:
                dfa_runner.nfa_run_n_step_multi_thread(input_lists,len(input_lists),f)

            # # 仿真生成的 sv 状态机
            ssh_summer.run_cmd(f"clear;clear;cd {mod_dir_linux}/sim/sim && rm -rf ~/sva_synth_sim_work/vcs && \
                            SIM=VCS make sim_vcs FILE_LIST_PATH={output_dir_linux}/{test_file_name}.fl \
                                SV_LOG_FILE_PATH={output_dir_linux}/{test_file_name}.log \
                                FILE_LIST_DIR={output_dir_linux} > {output_dir_linux}/{test_file_name}.vcs.log   ")

            check_answer = True

            check_answer &= check_log(ori_sim_log_path, nfa_log_path)
            if check_answer:
                print(f"[Success] nfa passed test {test_file_name}")
            else:
                sys.exit(-1)

            check_answer &= check_log(ori_sim_log_path, dfa_log_path)
            if check_answer:
                print(f"[Success] dfa passed test {test_file_name}")
            else:
                sys.exit(-1)

            check_answer &= check_log(ori_sim_log_path, sv_sim_log_path)
            if check_answer:
                print(f"[Success] sv passed test {test_file_name}")
            else:
                sys.exit(-1)


test_cases = [(401, 401)]
for test_case in test_cases:
    (TEST_MIN, TEST_MAX) = test_case
    main_nfa_run(TEST_MIN, TEST_MAX,test_tar="dfa")

# test_cases = [(0,30), (100,133)]
# test_cases = [(17, 17)]
# for test_case in test_cases:
#     (TEST_MIN, TEST_MAX) = test_case
#     main_nfa_run(TEST_MIN, TEST_MAX,test_tar="dfa", simulation=True)
