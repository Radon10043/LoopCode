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

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # 将项目添加到PATH里
sys.path.append(BASE_DIR)

import train_dataset_generator
from bb_list_getter import get_wanted_label_with_low_coverage
from sklearn_test import train_sk_model, load_model
from train_dataset_generator import read_afl_testcase
from weight_diff_calculate import calculate_weight_diff_for_each_output
import utils
import real_time_data as rta
import keep_showmap
# import record_out as ro

max_features = 100
PORT = 12012  # UDP端口
SOCKET_MODE = True  # 是否启用SOCKET模式，不启用就是单机测试模式
hidden_layer_sizes = (3, 3, 3,)  # 隐藏层
# hidden_layer_sizes = (100, 100, 100,)  # 隐藏层
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


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log-path", help="日志文件保存位置", type=str, required=True)
    parser.add_argument("--skip-log-stdout", help="阻止通过stdout输出日志信息", action="store_true")
    parser.add_argument("--pre-train", help="仅预训练", action="store_true")
    parser.add_argument("--pre-train-testcase", help="预训练时，模型的训练材料的本地地址", type=str)
    parser.add_argument("--model-save-path", help="预训练时，模型的保存地址", type=str)
    parser.add_argument("--model-load-path", help="非预训练模式时，预训练模型的地址，后续更新迭代模型也在该地址中", type=str)
    parser.add_argument("--log-level", help="日志的输出等级", type=str, default="INFO")  # 1:debug 2:info
    parser.add_argument("--gcc-version-bin", help="gcc编译出来的可执行被测文件地址", type=str)
    parser.add_argument("--append-args", help="被测文件的参数", type=str)
    parser.add_argument("--testcase-dir-path", help="测试用例的输出位置，用于监控路径覆盖情况", type=str)
    return parser.parse_args()


def start_module(printer=True, test_case_path=None, pre_train_model_save_path=None):
    if test_case_path is None:
        loguru.logger.error("模型读取的测试用例地址为空，请检查")
        raise Exception("模型读取的测试用例地址为空，请检查")
    args = get_args()
    x_data, y_data, is_first_read = read_afl_testcase(
        max_feature_length=max_features,
        # 最大特征长度, 也就是字节序列的长度，不够的话，后面补0，够的话，取前面的
        base_testcase_path=test_case_path,
        # fuzz的out文件夹的地址，会自动搜寻crash/hang/ya等文件夹
        binary_file_path=args.gcc_version_bin,
        base_cmd=args.append_args
    )
    x_data, y_data = numpy.array(x_data), numpy.array(y_data)
    loguru.logger.info('x_data.shape[0]:' + str(x_data.shape[0]) + '  >>>>>  y_data.shape[0]:' + str(y_data.shape[0]))
    assert x_data.shape[0] == y_data.shape[0]
    loguru.logger.debug(f"total train data size: {x_data.shape[0]}")
    global total_train_testcase_size
    total_train_testcase_size += x_data.shape[0]
    feature_size = x_data.shape[1]
    label_size = y_data.shape[1]
    model = train_sk_model(
        x_data,  # 特征
        y_data,  # 标签
        is_test=False,  # 是否切割数据集，用于输出f1值
        partial_fit=not is_first_read,
        pre_train_model_save_path=pre_train_model_save_path
    )
    if pre_train_model_save_path is not None:
        return
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


@loguru.logger.catch()
def main():
    loguru.logger.info("start py module...ok")
    time_used = []
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
        if args.pre_train:  # 预训练模式
            loguru.logger.info("此次为预训练模式")
            if args.model_save_path is None:
                loguru.logger.error("缺少预训练模型的保存位置地址")
                raise Exception("缺少预训练模型的保存位置地址")
            if args.pre_train_testcase is None:
                loguru.logger.error("缺少预训练时的测试用例地址")
                raise Exception("缺少预训练时的测试用例地址")
            start_module(printer=True,
                         test_case_path=args.pre_train_testcase,
                         pre_train_model_save_path=args.model_save_path)
            loguru.logger.info(f"预训练完成，预训练的模型位置为{args.model_save_path}")
            loguru.logger.info("正在处理预训练数据文件夹里的数据，删掉无用测试用例...")
            utils.trim_pre_train_testcase(args.pre_train_testcase)
            loguru.logger.info("预训练的训练材料，成功移动到seed文件夹中")
            loguru.logger.info("预训练模式结束")
        else:  # afl联动模式
            if args.model_load_path is not None:
                load_model(args.model_load_path)
                loguru.logger.info(f"成功加载预训练模型{args.model_load_path}")
            train_times = 0
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # internet UDP模式
            address = ("127.0.0.1", PORT)
            server_socket.bind(address)  # 绑定开启socket端口
            loguru.logger.info(f"绑定SOCKET端口成功, 开始监听{PORT}...")
            # t1 = Thread(target=rta.recordData, args=())
            # t1.start()
            showmap_thread = Thread(target=keep_showmap.runner, args=(args.testcase_dir_path, args.gcc_version_bin, args.append_args, os.path.join(args.log_path, "edge_cov.info")))
            showmap_thread.start()
            print('>>>Begin>>>')
            while True:
                print('>>>while True')
                receive_data, client = server_socket.recvfrom(1024)
                data = receive_data.decode("utf-8")
                loguru.logger.info(f"receive data: {data}")
                if data.startswith("/"):
                    print('>>>data.startswith')
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


"""
命令行示例
python main.py --log-path where_is_log --skip-log-stdout
       0           
"""
if __name__ == '__main__':
    main()
