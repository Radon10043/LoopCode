"""
模型训练数据生成器

"""
import os
import shutil
from collections import Counter

import loguru
import pandas as pd

import bytes_converter
import numpy as np

dataset_path = '../testcase.csv'
AFL_SHOWMAP_BINARY_PATH = "/home/lowry/Documents/LoopCode/afl-yagol/afl-showmap"


def gen_train_dataset_with_bits_array(max_feature_length=100):
    """
    生成训练数据
    :return:
    """
    x_data = []
    y_data = []
    df = pd.read_csv(dataset_path)
    longest_testcase_length = 0
    for index, row in df.iterrows():
        # 特征向量
        x = []
        p1 = bytes_converter.int_2_bits(int(row['p1']))
        p2 = bytes_converter.int_2_bits(int(row['p2']))
        p3 = bytes_converter.str_2_bits(str(row['p3']))
        p4 = bytes_converter.int_2_bits(int(row['p4']))
        p5 = bytes_converter.int_2_bits(int(row['p5']))
        p6 = bytes_converter.int_2_bits(int(row['p6']))
        p7 = bytes_converter.str_2_bits(str(row['p7']))
        x.extend(p1)
        x.extend(p2)
        x.extend(p3)
        x.extend(p4)
        x.extend(p5)
        x.extend(p6)
        x.extend(p7)
        if len(x) > longest_testcase_length:
            longest_testcase_length = len(x)
        if len(x) > max_feature_length:
            x = x[:max_feature_length]
        else:
            x = x + (max_feature_length - len(x)) * [0]
        x_data.append(x)
        # 标签
        c1 = row['c1']
        c2 = row['c2']
        c3 = row['c3']
        c4 = row['c4']
        c5 = row['c5']
        y_data.append([1 if i else 0 for i in [c1, c2, c3, c4, c5]])
    print("longest_testcase_length:", longest_testcase_length)
    return x_data, y_data


def gen_train_dataset_with_bytes_array(max_feature_length=100):
    df = pd.read_csv(dataset_path)
    x_data = []
    y_data = []
    longest_testcase_length = 0
    for index, row in df.iterrows():
        testcase_one_row = ""
        testcase_one_row += str(row['p1'])
        testcase_one_row += str(row['p2'])
        testcase_one_row += str(row['p3'])
        testcase_one_row += str(row['p4'])
        testcase_one_row += str(row['p5'])
        testcase_one_row += str(row['p6'])
        testcase_one_row += str(row['p7'])
        x = bytearray(testcase_one_row, 'utf-8')
        if len(x) > longest_testcase_length:
            longest_testcase_length = len(x)
        if len(x) > max_feature_length:
            x = x[:max_feature_length]
        else:
            x = x + (max_feature_length - len(x)) * b'\x00'
        x_data.append(x)
        c1 = row['c1']
        c2 = row['c2']
        c3 = row['c3']
        c4 = row['c4']
        c5 = row['c5']
        y = [1 if i else 0 for i in [c1, c2, c3, c4, c5]]
        y_data.append(y)
    print("longest_testcase_length:", longest_testcase_length)
    return x_data, y_data


already_read_testcase = set()


# def read_afl_testcase(max_feature_length=100, base_testcase_path=None, binary_file_path=None, base_cmd=None):
#     testcase_dirs = [f"{base_testcase_path}/ya", f"{base_testcase_path}/crashes", f"{base_testcase_path}/queue",
#                      f"{base_testcase_path}/hangs"]
#     x_data = []
#     y_data = []
#     is_first_read = True if len(already_read_testcase) == 0 else False
#     longest_testcase_length = 0
#     for testcase_dir in testcase_dirs:
#         for root, dirs, files in os.walk(testcase_dir):
#             for file_name in files:
#                 if file_name.endswith("_cov.txt"):
#                     coverage_path = os.path.join(root, file_name)
#                     testcase_bin_path = os.path.join(root, file_name.replace("_cov.txt", ""))
#                     if not root.endswith("ya"):  # ya文件夹不可能存在重复读取, 因为数据读取完都被清空了
#                         if testcase_bin_path in already_read_testcase:  # 过滤已经训练过的测试用例
#                             continue
#                         else:
#                             already_read_testcase.add(testcase_bin_path)
#                     if not os.path.exists(testcase_bin_path):
#                         loguru.logger.error("ERROR: NO TESTCASE BIN FILE, BUT HAVE COVERAGE INFO",
#                                             testcase_bin_path)  # 没有对应的测试用例
#                     else:
#                         with open(testcase_bin_path, "r", encoding="ISO-8859-15") as f:
#                             t = f.read()
#                             x = bytearray(t, "ISO-8859-15")
#                             if len(x) > longest_testcase_length:
#                                 longest_testcase_length = len(x)
#                             if len(x) > max_feature_length:
#                                 x = x[:max_feature_length]
#                             else:
#                                 x = x + (max_feature_length - len(x)) * b'\x00'
#                             x_data.append(x)
#                         with open(coverage_path, "r") as f: 
#                             temp = []
#                             lines = f.readlines()
#                             for i, line in enumerate(lines):  # 只读取前bb_size行
#                                 line = int(line)
#                                 temp.append(line)
#                                 if line == "":  # 读取到文件的结尾了
#                                     break
#                             assert len(temp) == len(lines)
#                             y_data.append(temp)
#                     if root.endswith("ya"):  # 清空ya文件夹的测试用例，因为这些测试用例只提供模型训练数据，没有其他作用
#                         os.remove(testcase_bin_path)
#                         loguru.logger.debug(f"ya的测试用例被删除: {testcase_bin_path}")
#                     os.remove(coverage_path)  # 清空所有的cov 0/1信息，训练过后就没有用了
#                     loguru.logger.debug(f"测试用例覆盖信息被删除: {coverage_path}")
#     check_data(y_data)
#     loguru.logger.debug(f"该批次最长测试用例长度为: {longest_testcase_length}")
#
#     return x_data, y_data, is_first_read


def read_afl_testcase(max_feature_length=100, base_testcase_path=None, binary_file_path=None, base_cmd=None):
    testcase_dirs = [f"{base_testcase_path}/ya", f"{base_testcase_path}/crashes", f"{base_testcase_path}/queue",
                     f"{base_testcase_path}/hangs"]
    x_data = []
    # y_data = []
    edge_list = []
    edge_length = []
    max_edge = 0
    is_first_read = True if len(already_read_testcase) == 0 else False
    longest_testcase_length = 0
    for testcase_dir in testcase_dirs:
        for root, dirs, files in os.walk(testcase_dir):
            for file_name in files:
                if file_name.endswith("_cov.txt"):
                    coverage_path = os.path.join(root, file_name)
                    testcase_bin_path = os.path.join(root, file_name.replace("_cov.txt", ""))
                    if not root.endswith("ya"):  # ya文件夹不可能存在重复读取, 因为数据读取完都被清空了
                        if testcase_bin_path in already_read_testcase:  # 过滤已经训练过的测试用例
                            continue
                        else:
                            already_read_testcase.add(testcase_bin_path)
                    if not os.path.exists(testcase_bin_path):
                        loguru.logger.error("ERROR: NO TESTCASE BIN FILE, BUT HAVE COVERAGE INFO",
                                            testcase_bin_path)  # 没有对应的测试用例
                    else:
                        with open(testcase_bin_path, "r", encoding="ISO-8859-15") as f:
                            t = f.read()
                            x = bytearray(t, "ISO-8859-15")
                            if len(x) > longest_testcase_length:
                                longest_testcase_length = len(x)
                            if len(x) > max_feature_length:
                                x = x[:max_feature_length]
                            else:
                                x = x + (max_feature_length - len(x)) * b'\x00'
                            x_data.append(x)
                        with open(coverage_path, "r") as f:  # TODO: use afl-showmap
                            # TODO: keep_showmap.py
                            edge = []
                            cmd = f"{AFL_SHOWMAP_BINARY_PATH} -q -e -o /dev/stdout -m 512 -t 500 {binary_file_path} {base_cmd} {testcase_bin_path} "
                            loguru.logger.debug(cmd)
                            loguru.logger.debug(f"分析路径CMD:{cmd}")
                            out = os.popen(cmd).readlines()
                            for o in out:
                                edge_item = int(o.split(':')[0])
                                if edge_item > max_edge:
                                    max_edge = edge_item
                                edge.append(edge_item)
                            edge_length.append(len(out))
                            edge_list.append(edge)
                    if root.endswith("ya"):  # 清空ya文件夹的测试用例，因为这些测试用例只提供模型训练数据，没有其他作用
                        os.remove(testcase_bin_path)
                        loguru.logger.debug(f"ya的测试用例被删除: {testcase_bin_path}")
                    os.remove(coverage_path)  # 清空所有的cov 0/1信息，训练过后就没有用了
                    loguru.logger.debug(f"测试用例覆盖信息被删除: {coverage_path}")
    y_data = arrange_list(edge_list, max_edge + 1)
    check_data(len(y_data))
    loguru.logger.debug(f"该批次最长测试用例长度为: {longest_testcase_length}")

    return x_data, y_data, is_first_read


# 整理得到包含0，1的二维列表
def arrange_list(a_list, max_size):
    re_list = np.zeros([len(a_list), max_size], int)
    for i in range(len(a_list)):
        for j in a_list[i]:
            re_list[i, j] = 1
    i = 0
    # 删除纯0列
    loguru.logger.info('整理中...')
    loguru.logger.info('>>>共' + str(re_list.shape[1]) + '列>>>')
    idx = np.argwhere(np.all(re_list[..., :] == 0, axis=0))
    re_list = np.delete(re_list, idx, axis=1)
    loguru.logger.info('!!整理完成!!')
    loguru.logger.info('=============最终为' + str(re_list.shape[1]) + '列=============')
    return re_list.tolist()


def check_data(data):
    save_path = "/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/temp/py.log/edge_content.info"
    with open(save_path, "a") as save_file:
        save_file.write("output showmapt data: >>>\n")
        # save_file.write(f"edge_length: {str(data[0])}\n")
        # save_file.write(f"edge_list_length {str(len(data[1]))}\n")
        save_file.write(str(data) + '\n')
        save_file.write('==========================END\n')