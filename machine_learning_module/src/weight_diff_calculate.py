import math
import os
import shutil

import numpy as np


def euclidean(point1, point2):
    """
    计算两点之间的欧式距离

    当维度不超过10维时，用math更快
    若超过了，则尝试用下面的代码r1 = np.linalg.norm(point1 - point2)

    :param point1:
    :param point2:
    :return:
    """
    assert len(point1) == len(point2)  # 计算距离时，节点内的数量必须相同
    return math.dist(point1, point2)


def calculate_weight_diff_for_each_output(feature_sizes, label_sizes, hidden_layer_sizes, clf, top_k=5):
    """
    计算权重差异距离累加和

    :param feature_sizes:
    :param label_sizes:
    :param hidden_layer_sizes:
    :param clf: 模型，必须提供权重向量
    :param top_k:
    :return:
    """
    if os.path.isdir("../out"):
        shutil.rmtree("../out")
    os.mkdir("../out")
    print("hidden_layer_sizes:", hidden_layer_sizes)
    for i in range(label_sizes):
        summary = []  # 该输出层对应的每个输入层的权重差异距离累加和
        for j in range(feature_sizes):
            if len(hidden_layer_sizes) == 2:
                points = gen_point_2(clf, hidden_layer_sizes, i, j)
            elif len(hidden_layer_sizes) == 3:
                points = gen_point_3(clf, hidden_layer_sizes, i, j)
            else:
                raise Exception("不支持的隐藏层数量")
            sum_of_weight_diff = 0
            for m in range(len(points)):
                for n in range(m + 1, len(points)):
                    sum_of_weight_diff += euclidean(points[m], points[n])
            summary.append((sum_of_weight_diff, j))
        summary.sort(key=lambda x: x[0], reverse=True)  # 降序排列，最前面的是最具有影响力的
        with open(f"../out/{str(i)}.txt", "w") as f:
            for k in range(top_k):
                f.write(str(summary[k][1]) + "\n")


def gen_point_3(clf, hidden_layer_sizes, i, j):
    """
    对于存在三个隐藏层的模型
    """
    points = []
    for d0 in range(hidden_layer_sizes[0]):
        for d1 in range(hidden_layer_sizes[1]):
            for d2 in range(hidden_layer_sizes[2]):
                points.append(
                    (
                        clf.coefs_[0][j][d0],
                        clf.coefs_[1][d0][d1],
                        clf.coefs_[2][d1][d2],
                        clf.coefs_[3][d2][i]
                    )
                )
    return points


def gen_point_2(clf, hidden_layer_sizes, i, j):
    """
    对于存在两个隐藏层的模型
    """
    points = []
    for d0 in range(hidden_layer_sizes[0]):
        for d1 in range(hidden_layer_sizes[1]):
            points.append(
                (
                    clf.coefs_[0][j][d0],
                    clf.coefs_[1][d0][d1],
                    clf.coefs_[2][d1][i]
                )
            )
    return points
