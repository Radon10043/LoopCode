"""
模型训练数据生成器

"""
import os

import pandas as pd

import bytes_converter

dataset_path = '../testcase.csv'


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


def read_afl_testcase(max_feature_length=100):
    x_data = []
    y_data = []
    longest_testcase_length = 0
    for root, dirs, files in os.walk("../c_example/temp/out/ya"):
        for file_name in files:
            test_case_path = os.path.join(root, file_name)
            with open(test_case_path, "r", encoding="ISO-8859-15") as f:
                t = f.read()
                x = bytearray(t, "ISO-8859-15")
                if len(x) > longest_testcase_length:
                    longest_testcase_length = len(x)
                if len(x) > max_feature_length:
                    x = x[:max_feature_length]
                else:
                    x = x + (max_feature_length - len(x)) * b'\x00'
                x_data.append(x)
    print("longest_testcase_length:", longest_testcase_length)


read_afl_testcase()
