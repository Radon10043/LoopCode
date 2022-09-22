"""
基于全连接神经网络的关联关系量化方法
@author: yagol

"""

import os
import sys
from threading import Thread

import loguru
import numpy
import socket
import time
import argparse
import clustering
import real_time_data as rtd

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 将项目添加到PATH里
sys.path.append(BASE_DIR)

import utils
import keep_showmap

max_features = 100
PORT = 12012  # UDP端口
SOCKET_MODE = True  # 是否启用SOCKET模式，不启用就是单机测试模式
hidden_layer_sizes = (3, 3, 3,)  # 隐藏层
py_output_dir_name = 'py_out'
total_train_testcase_size = 0


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-path", help="日志文件保存位置", type=str, required=True)
    parser.add_argument("--skip-log-stdout", help="阻止通过stdout输出日志信息", action="store_true")
    parser.add_argument("--pre-train", help="仅预训练", action="store_true")
    parser.add_argument("--pre-train-testcase", help="预训练时，模型的训练材料的本地地址", type=str)
    # parser.add_argument("--model-save-path", help="预训练时，模型的保存地址", type=str)
    # parser.add_argument("--model-load-path", help="非预训练模式时，预训练模型的地址，后续更新迭代模型也在该地址中", type=str)
    parser.add_argument("--log-level", help="日志的输出等级", type=str, default="INFO")  # 1:debug 2:info
    parser.add_argument("--gcc-version-bin", help="gcc编译出来的可执行被测文件地址", type=str)
    parser.add_argument("--append-args", help="被测文件的参数", type=str)
    parser.add_argument("--testcase-dir-path", help="测试用例的输出位置，用于监控路径覆盖情况", type=str)
    parser.add_argument("--good-seeds-path", help="存储选出种子文件名的位置", type=str)
    parser.add_argument("--out-path", help="记录输出文件地址", type=str)
    parser.add_argument("--fuzzer-stats", help="afl文件地址", type=str)
    return parser.parse_args()


@loguru.logger.catch()
def main():
    loguru.logger.info("start k-means_py module...ok")
    if SOCKET_MODE:
        utils.kill_process_by_socket_port(PORT)
        args = get_args()
        if args.skip_log_stdout:
            loguru.logger.remove()
        else:
            loguru.logger.level("INFO")
        timestamp = time.time()
        log_label = "pre_train" if args.pre_train else "afl"
        log_path = os.path.join(args.log_path, f"{log_label}_{timestamp}_py.log")
        if args.log_level in ['INFO', 'DEBUG']:
            loguru.logger.info(f"设置日志等级为{args.log_level}")
            loguru.logger.add(log_path, level=args.log_level)
        else:
            loguru.logger.warning("参数--log-level设置错误")
            loguru.logger.add(log_path, level="INFO")
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internet UDP模式
        address = ("127.0.0.1", PORT)
        server_socket.bind(address)  # 绑定开启socket端口
        loguru.logger.info(f"绑定SOCKET端口成功, 开始监听{PORT}...")
        t1 = Thread(target=rtd.recordData, args=(args.out_path, args.fuzzer_stats))
        t1.start()
        # showmap_thread = Thread(target=keep_showmap.runner, args=(args.testcase_dir_path, args.gcc_version_bin, args.append_args, os.path.join(args.log_path, "edge_cov.info")))
        # showmap_thread.start()
        # k_means_thread = Thread(target=kMeans.k_means_main, args=(args.testcase_dir_path, args.good_seeds_path))
        # k_means_thread.start()
        # kMeans.k_means_main(seed_path=args.testcase_dir_path, out_path=args.good_seeds_path)
        print('>>>Begin>>>')
        while True:
            print('>>>while True')
            receive_data, client = server_socket.recvfrom(1024)
            data = receive_data.decode("utf-8")
            loguru.logger.info(f"receive data: {data}")
            if data.startswith("/"):
                print('>>>data.startswith')
                res = args.good_seeds_path
                loguru.logger.info(f"good_seeds_path: {res}")
                # clustering.k_means_main(seed_path=args.testcase_dir_path, out_path=res)
                # clustering.db_scan_main(seed_path=args.testcase_dir_path, out_path=res)
                clustering.k_means_main(seed_path=args.testcase_dir_path, out_path=res)
                server_socket.sendto(res.encode("utf-8"), client)
    # else:  # 不启用SOCKET，单机测试
        # start_module(printer=True, test_case_path="/home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/out")


"""
命令行示例
python main.py --log-path where_is_log --skip-log-stdout
       0           
"""
if __name__ == '__main__':
    main()
