# -*- codeing = utf-8 -*-
# @Time : 2022/9/2 8:58
# @Author : Lowry
# @File : clustering.py
# @Software : PyCharm

import os
import random
from time import sleep
from sklearn.cluster import DBSCAN
from sklearn.cluster import AgglomerativeClustering

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
    if os.path.exists(path):
        os.remove(path)
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
    label_set = list(set(label_list))  # 得到标签集合，在转换为列表
    # loguru.logger.info(f'标签集合：{label_set}')
    for s in label_set:  # 遍历所有label集合，每次随机得到一个标签的种子文件名，并添加至new_seed_list
        index_list = np.where(label_array == s)[0]  # 该标签在label_list中的位置
        # print(f'标签{s}索引')
        # print(index_list)
        # loguru.logger.info(f'标签{s}索引')
        # loguru.logger.info(index_list)
        i = random.choice(index_list)  # 随机选择标签中的一个位置
        new_seed = seed_list[int(i)]  # 获取该位置的种子文件名
        # print(f'选择的种子文件名：{new_seed}')
        loguru.logger.info(f'选择的种子文件名：{new_seed}')
        new_seed_list.append(new_seed)  # 将该簇中的该种子添加至new_seed_list
    return new_seed_list


#
def get_byte(seed_path=None):
    X = []  # 用于存储特征值
    X_file_name = []  # 用于存储被选出的种子文件名
    y = []  # 用于存储初始标签，暂时没想好有啥可以用的，默认为空列表
    seed_path = seed_path + '/queue'
    files = os.listdir(seed_path)
    for file in files:  # 遍历文件夹
        if (not os.path.isdir(file)) and (not file.endswith('.txt')) and (
                file != '.state'):  # 判断是否是文件夹，不是文件夹才打开,且不以.txt结尾
            # print(file)
            X_file_name.append(file)  # 存储所有种子文件名
            x_data = get_bits(path=seed_path + '/' + file)
            X.append(x_data[0])
    X = np.array(X).astype(np.float64)
    y = np.array(y)
    return X, y, X_file_name


def k_means_main(seed_path=None, out_path=None):
    """
    1. 读取种子文件
    2. 将内容转换为二进制
    3. 将二进制数据作为特征值放入k-means求解
    4. 获得特征标签
    5. 从每个簇种随机选择种子，并将选出的种子文件名存入seed_name中
    6. 将选择的种子文件名写入good_seeds.txt
    :param seed_path: 种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    :return: void
    """
    loguru.logger.info(">>>开始-Kmeans-聚类>>>")

    """1. 读取种子文件 & 2. 将内容转换为二进制"""
    X, y, X_file_name = get_byte(seed_path)

    """3 将二进制数据作为特征值放入k-means求解"""
    km = k_means(X, y)

    """4. 获得特征标签"""
    # cc = km.cluster_centers_  # 簇中心点
    lb = km.labels_  # 特征标签

    """5. 从每个簇中随机选择种子，并将选出的种子文件名存入seeds_name中"""
    seed_name = choose_seed(seed_list=X_file_name, label_list=lb)

    """6. 将选择的种子文件名写入good_seeds.txt"""
    write_seed_name(seed_name=seed_name, path=out_path)


def get_seeds_fixed(seed_path=None, out_path=None):
    """
    【固定】  ===>    获取前1/3的种子
    :param seed_path: 初始种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    """
    seed_path = seed_path + '/queue'
    files = os.listdir(seed_path)
    X_file_name = []
    loguru.logger.info(f'开始固定选取种子，总目录: {seed_path}')
    for file in files:  # 遍历文件夹
        # 判断是否是文件夹，不是文件夹才打开。并且不以.txt结尾
        if (not os.path.isdir(file)) and (not file.endswith('.txt')) and (file != '.state'):
            X_file_name.append(file)  # 存储所有种子文件名
    X_file_name.sort()
    loguru.logger.info(f'共选择总数量的1/3种子: {int(len(X_file_name) / 3)}个 ')
    for i in range(int(len(X_file_name) / 3)):
        loguru.logger.info(f'种子文件名: {X_file_name[i]}')
    write_seed_name(X_file_name[0: int(len(X_file_name) / 3)], out_path)


def get_seeds_random(seed_path=None, out_path=None):
    """
    【随机】  ===>    获取前1/3的种子
    :param seed_path: 初始种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    """
    seed_path = seed_path + '/queue'
    files = os.listdir(seed_path)
    X_file_name = []
    for file in files:  # 遍历文件夹
        # 判断是否是文件夹，不是文件夹才打开。并且不以.txt结尾
        if (not os.path.isdir(file)) and (not file.endswith('.txt')) and (file != '.state'):
            X_file_name.append(file)  # 存储所有种子文件名
    X_file_name = random.sample(X_file_name, int(len(X_file_name) / 3))
    loguru.logger.info(f'共选择总数量的1/3种子: {int(len(X_file_name))}个 ')
    write_seed_name(X_file_name, out_path)


# get_seeds_random(seed_path=r'/home/lowry/Documents/LoopCode/scripts/jasper-2.0.21/obj-loop/out',
#                  out_path=r'/home/lowry/Documents/LoopCode/scripts/jasper-2.0.21/obj-loop/temp/good_seeds.txt')


def db_scan_main(seed_path=None, out_path=None):
    """
    1. 读取种子文件
    2. 将内容转换为二进制
    3. 将二进制数据作为特征值放入k-means求解
    4. 获得特征标签
    5. 从每个簇种随机选择种子，并将选出的种子文件名存入seed_name中
    6. 将选择的种子文件名写入good_seeds.txt
    :param seed_path: 种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    :return: void
    """
    loguru.logger.info(">>>开始-DBSCAN-聚类>>>")

    """1. 读取种子文件 & 2. 将内容转换为二进制"""
    X, y, X_file_name = get_byte(seed_path)

    """3 将二进制数据作为特征值放入DBSCAN求解"""
    # eps为距离阈值ϵ，min_samples为邻域样本数阈值MinPts,X为数据
    y_pred = DBSCAN(eps=100, min_samples=1).fit(X).__dict__

    """4. 获得特征标签"""
    lb = y_pred['labels_']

    """5. 从每个簇中随机选择种子，并将选出的种子文件名存入seeds_name中"""
    seed_name = choose_seed(seed_list=X_file_name, label_list=lb)

    """6. 将选择的种子文件名写入good_seeds.txt"""
    write_seed_name(seed_name=seed_name, path=out_path)
    # y_pred = DBSCAN(eps=100, min_samples=1).fit(X).__dict__
    # print(y_pred)
    # print(set(lb))
    # print(np.where(y_pred['labels_'] == 5)[0])


def agglomerative_main(seed_path=None, out_path=None):
    """
    1. 读取种子文件
    2. 将内容转换为二进制
    3. 将二进制数据作为特征值放入agglomerative求解
    4. 获得特征标签
    5. 从每个簇种随机选择种子，并将选出的种子文件名存入seed_name中
    6. 将选择的种子文件名写入good_seeds.txt
    :param seed_path: 种子目录绝对路径
    :param out_path: 选中种子文件名存储路径
    :return: void
    """
    loguru.logger.info(">>>开始-层次-聚类>>>")

    """1. 读取种子文件 & 2. 将内容转换为二进制"""
    X, y, X_file_name = get_byte(seed_path)

    """3 将二进制数据作为特征值放入agglomerative求解"""
    n_clusters = int(len(X)/4)
    loguru.logger.info(f'本次训练--->簇的数量：{n_clusters}')
    cluster = AgglomerativeClustering(n_clusters=n_clusters, affinity='euclidean', linkage='ward')
    cluster.fit_predict(X)
    y_pred = cluster.__dict__

    """4. 获得特征标签"""
    lb = y_pred['labels_']

    """5. 从每个簇中随机选择种子，并将选出的种子文件名存入seeds_name中"""
    seed_name = choose_seed(seed_list=X_file_name, label_list=lb)

    """6. 将选择的种子文件名写入good_seeds.txt"""
    write_seed_name(seed_name=seed_name, path=out_path)


# agglomerative(r'/home/lowry/Documents/LoopCode/scripts/jasper_in4', r"/home/lowry/Documents/LoopCode/scripts/good_seeds.txt")
