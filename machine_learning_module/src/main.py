"""
基于全连接神经网络的关联关系量化方法
@author: yagol

"""

import os
import sys

import loguru
import numpy
import socket
import time
import argparse

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 将项目添加到PATH里
sys.path.append(BASE_DIR)

import train_dataset_generator
from bb_list_getter import get_wanted_label_with_low_coverage
from sklearn_test import train_sk_model
from train_dataset_generator import read_afl_testcase
from weight_diff_calculate import calculate_weight_diff_for_each_output
import utils

max_features = 100
PORT = 12012  # UDP端口
SOCKET_MODE = True  # 是否启用SOCKET模式，不启用就是单机测试模式
hidden_layer_sizes = (3, 3, 3,)  # 隐藏层
py_output_dir_name = 'py_out'
total_train_testcase_size = 0


def test_case_type_1():
    """
    比特序列，即每一个元素是[0,0,1,1,1,1,...]
    弃用，用于基础测试

    :return:
    """
    return train_dataset_generator.gen_train_dataset_with_bits_array(max_feature_length=max_features)


def test_case_type_2():
    """
    字节序列，即每一个元素是[\x00,\x00,\x01,\x01,\x01,\x01,...]
    弃用，用于基础测试

    :return:
    """
    return train_dataset_generator.gen_train_dataset_with_bytes_array(max_feature_length=max_features)


@loguru.logger.catch()
def start_module(printer=True, test_case_path=None):
    x_data, y_data, is_first_read = read_afl_testcase(
        max_feature_length=max_features,
        # 最大特征长度, 也就是字节序列的长度，不够的话，后面补0，够的话，取前面的
        base_testcase_path=test_case_path,
        # fuzz的out文件夹的地址，会自动搜寻crash/hang/ya等文件夹
    )
    x_data, y_data = numpy.array(x_data), numpy.array(y_data)
    assert x_data.shape[0] == y_data.shape[0]
    loguru.logger.debug(f"total train data size: {x_data.shape[0]}")
    global total_train_testcase_size
    total_train_testcase_size += x_data.shape[0]
    feature_size = x_data.shape[1]
    label_size = y_data.shape[1]
    model = train_sk_model(
        x_data,  # 特征
        y_data,  # 标签
        is_test=True,  # 是否切割数据集，用于输出f1值
        partial_fit=not is_first_read
    )
    bb_list_wanted = get_wanted_label_with_low_coverage(y_data, size=10)  # 根据覆盖情况，获得最差的size个基本块的序号
    return calculate_weight_diff_for_each_output(
        feature_size,  # 特征的长度
        label_size,  # 标签的长度
        hidden_layer_sizes,  # 隐藏层
        clf=model,  # 模型
        printer=printer,  # 是否打印计算过程
        label_list_wanted=bb_list_wanted,  # 想要优先覆盖的基本块的序号
        summaries_path=os.path.join(test_case_path, py_output_dir_name),  # 输出的文件夹，会自动创建fusion.csv
        top_k=None,  # 只输出前top_k个字节序列,None表示全部输出，也就是输出feature_size个
    )


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-path", help="日志文件保存位置", type=str)
    parser.add_argument("--skip-log-stdout", help="阻止通过stdout输出日志信息", action="store_true")
    return parser.parse_args()


"""
命令行示例
python main.py --log-path where_is_log --skip-log-stdout
       0           
"""
if __name__ == '__main__':
    loguru.logger.info("start py module...ok")
    time_used = []
    if SOCKET_MODE:
        args = get_args()
        if args.skip_log_stdout:
            loguru.logger.remove()
        loguru.logger.add(args.log_path)
        utils.kill_process_by_socket_port(PORT)
        train_times = 0
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internet udp模式
        address = ("127.0.0.1", PORT)
        server_socket.bind(address)  # 绑定开启socket端口
        loguru.logger.info(f"绑定SOCKET端口成功, 开始监听{PORT}...")
        while True:
            receive_data, client = server_socket.recvfrom(1024)
            data = receive_data.decode("utf-8")
            loguru.logger.info(f"receive data: {data}")
            if data.startswith("/"):
                time1 = time.time()
                res = start_module(printer=False, test_case_path=data)  # 返回值是fusion的文件地址
                server_socket.sendto(res.encode("utf-8"), client)
                time_used.append(time.time() - time1)
                train_times += 1
                loguru.logger.info(
                    f"\nNO.{train_times}\n\tTIME USED: {time_used[-1]}\n"
                    f"\tTOTAL TIME USED: {sum(time_used)}\n"
                    f"\tTOTAL TRAIN TESTCASE SIZE: {total_train_testcase_size}\n========")
    else:  # 不启用SOCKET，单机测试
        start_module(printer=True, test_case_path="/home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/out")
