# -*- codeing = utf-8 -*-
# @Time : 2022/9/2 8:58
# @Author : Lowry
# @File : kMeans.py
# @Software : PyCharm

import os
import random
from time import sleep

from sklearn.cluster import KMeans
import numpy as np
import loguru


def k_means(X, y):
    """
    计算K均值，返回模型对象
    :param X: 特征
    :param y: 标签
    :return: 模型
    """
    # print('X.shape')
    # print(X.shape)
    # print('y.shape')
    # print(y.shape)
    loguru.logger.info('X.shape')
    loguru.logger.info(X.shape)
    loguru.logger.info('y.shape')
    loguru.logger.info(y.shape)

    # 设置n_clusters为聚类中心数量
    n_clusters = int(X.shape[0] / 3)
    # n_clusters = 5
    loguru.logger.info(f'本次训练--->簇的数量：{n_clusters}')
    Kmeans = KMeans(n_clusters=n_clusters)
    # 训练模型
    Kmeans.fit(X)
    return Kmeans


def get_bits(max_feature_length=100, path=None):
    """
    读取.txt尾缀的文件内容为二进制
    :param max_feature_length:
    :param path: 文件路径
    :return: 二进制数据
    """
    x_data = []
    longest_testcase_length = 0
    with open(path, "r", encoding="ISO-8859-15") as f:
        t = f.read()
        x = bytearray(t, "ISO-8859-15")
        if len(x) > longest_testcase_length:
            longest_testcase_length = len(x)
        if len(x) > max_feature_length:
            x = x[:max_feature_length]
        else:
            x += (max_feature_length - len(x)) * b'\x00'
        x_data.append(x)
    return x_data


def write_seed_name(seed_name, path):
    """
    将seed_name写入path中
    :param seed_name: 种子文件名列表
    :param path: 绝对路径
    """
    # path = r'C:\Users\59489\PycharmProjects\聚类算法'
    f = open(path, "a")
    for s in seed_name:
        f.write(s + '\n')
    f.close()


def choose_seed(seed_list, label_list):
    """
    根据label_list从seed_list中随机选择种子
    :param seed_list: 所有的种子文件名列表
    :param label_list: 特征标签列表
    :return: 最终的种子文件名列表
    """
    new_seed_list = []
    label_array = np.array(label_list)  # 转换成数组
    label_set = list(set(label_list))    # 得到标签集合，在转换为列表
    loguru.logger.info(f'标签集合：{label_set}')
    for s in label_set:     # 遍历所有label集合，每次随机得到一个标签的种子文件名，并添加至new_seed_list
        index_list = np.where(label_array == s)[0]     # 该标签在label_list中的位置
        # print(f'标签{s}索引')
        # print(index_list)
        loguru.logger.info(f'标签{s}索引')
        loguru.logger.info(index_list)
        i = random.choice(index_list)       # 随机选择标签中的一个位置
        new_seed = seed_list[int(i)]     # 获取该位置的种子文件名
        # print(f'选择的种子文件名：{new_seed}')
        loguru.logger.info(f'选择的种子文件名：{new_seed}')
        new_seed_list.append(new_seed)      # 将该簇中的该种子添加至new_seed_list
    return new_seed_list


def k_means_main(seed_path=None, out_path=None):
    """
    1. 读取种子文件
    2. 将内容转换为二进制
    3. 将二进制数据作为特征值放入k-means求解
    4. 获得特征标签
    5. 从每个簇种随机选择种子，并将选出的种子文件名存入seed_name中
    6. 将选择的种子文件名写入good_seeds.txt
    :param seed_path: 初始种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    :return: void
    """
    sleep(60)
    X = []  # 用于存储特征值
    X_file_name = []    # 用于存储被选出的种子文件名
    y = []  # 用于存储初始标签，暂时没想好有啥可以用的，默认为空列表
    """1. 读取种子文件 & 2. 将内容转换为二进制"""
    seed_path = seed_path + '/queue'
    files = os.listdir(seed_path)
    for file in files:  # 遍历文件夹
        if (not os.path.isdir(file)) and (not file.endswith('.txt')) and (file != '.state'):  # 判断是否是文件夹，不是文件夹才打开,且不以.txt结尾
            print(file)
            X_file_name.append(file)    # 存储所有种子文件名
            x_data = get_bits(path=seed_path + '/' + file)
            X.append(x_data[0])
    X = np.array(X)
    y = np.array(y)

    """3. 将二进制数据作为特征值放入kk-means求解"""
    km = k_means(X, y)

    """4. 获得特征标签"""
    cc = km.cluster_centers_    # 簇中心点
    lb = km.labels_     # 特征标签

    """5. 从每个簇中随机选择种子，并将选出的种子文件名存入seeds_name中"""
    seed_name = choose_seed(seed_list=X_file_name, label_list=lb)

    """6. 将选择的种子文件名写入good_seeds.txt"""
    if os.path.exists(out_path):
        os.remove(out_path)
    write_seed_name(seed_name=seed_name, path=out_path)


# k_means_main(seed_path=r'/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/out',
#              out_path=r'/home/lowry/Documents/LoopCode/scripts/jasper-3.0.3/obj-loop/temp/good_seeds.txt')
