"""
基于全连接神经网络的关联关系量化方法
@author: yagol

"""

import os
import sys
import numpy
import socket
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 将项目添加到PATH里
sys.path.append(BASE_DIR)

import train_dataset_generator
from bb_list_getter import get_wanted_label_with_low_coverage
from sklearn_test import train_sk_model
from train_dataset_generator import read_afl_testcase
from weight_diff_calculate import calculate_weight_diff_for_each_output

max_features = 100
PORT = 12012  # UDP端口
SOCKET_MODE = True  # 是否启用SOCKET模式，不启用就是单机测试模式
hidden_layer_sizes = (3, 3, 3,)  # 隐藏层


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


def start_module(printer=True, test_case_path=None, bb_file_path=None):
    x_data, y_data, is_first_read = read_afl_testcase(
        max_feature_length=max_features,
        # 最大特征长度, 也就是字节序列的长度，不够的话，后面补0，够的话，取前面的
        base_testcase_path=test_case_path,
        # fuzz的out文件夹的地址，会自动搜寻crash/hang/ya等文件夹
        bb_file_path=bb_file_path  # bb_file的地址，用于处理标签，使标签的长度为基本块的个数
    )
    x_data, y_data = numpy.array(x_data), numpy.array(y_data)
    assert x_data.shape[0] == y_data.shape[0]
    print(f"total train data size: {x_data.shape[0]}")
    feature_size = x_data.shape[1]
    label_size = y_data.shape[1]
    model = train_sk_model(
        x_data,  # 特征
        y_data,  # 标签
        is_test=True,  # 是否切割数据集，用于输出f1值
        partial_fit=not is_first_read
    )
    bb_list_wanted = get_wanted_label_with_low_coverage(y_data, size=2)  # 根据覆盖情况，获得最差的size个基本块的序号
    return calculate_weight_diff_for_each_output(
        feature_size,  # 特征的长度
        label_size,  # 标签的长度
        hidden_layer_sizes,  # 隐藏层
        clf=model,  # 模型
        printer=printer,  # 是否打印计算过程
        label_list_wanted=bb_list_wanted,  # 想要优先覆盖的基本块的序号
        summaries_path=os.path.dirname(bb_file_path),  # 输出的文件夹，会自动创建fusion.csv
        top_k=None,  # 只输出前top_k个字节序列,None表示全部输出，也就是输出feature_size个
    )


"""
命令行示例
python main.py _socket_mode _bb_file_path
       0       1            2
"""
if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 3:
        SOCKET_MODE = sys.argv[1] == "True"  # 是否启用SOCKET
        assert os.path.isfile(sys.argv[2])  # BB_File必须存在
        if SOCKET_MODE:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internet udp模式
            address = ("127.0.0.1", PORT)
            server_socket.bind(address)  # 绑定开启socket端口
            while True:
                receive_data, client = server_socket.recvfrom(1024)
                data = receive_data.decode("utf-8")
                print(f"data: {data}")
                if data.startswith("/"):
                    res = start_module(printer=False, test_case_path=data, bb_file_path=sys.argv[2])
                    server_socket.sendto(res.encode("utf-8"), client)
        else:  # 不启用SOCKET，单机测试
            start_module(printer=True, test_case_path="/home/yagol/PycharmProjects/LoopCode/scripts/LOOP/obj-loop/out",
                         bb_file_path="/home/yagol/PycharmProjects/LoopCode/scripts/LOOP/obj-loop/temp/BBFile.txt")
    else:
        print("error: no bb file path")
