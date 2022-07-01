import os

import loguru
import numpy
from scipy.spatial.distance import cdist


def fusion(summaries, summaries_path):
    indexes_and_probabilities = dict()
    for summary in summaries:
        for index, probability in summary:
            temp_probability = indexes_and_probabilities.get(index, 0)
            temp_probability += probability
            indexes_and_probabilities[index] = temp_probability
    indexes_and_probabilities = sorted(indexes_and_probabilities.items(), key=lambda x: x[1])
    file_path = f"{summaries_path}/fusion.csv"
    origin_prob_path = f"{summaries_path}/origin.csv"
    with open(file_path, "w") as f:
        with open(origin_prob_path, "w") as o:
            prob_start = 1
            for index, probability in indexes_and_probabilities:
                f.write(str(index) + "," + str(prob_start) + "\n")
                prob_start += 1
                o.write((str(index) + "," + str(probability) + "\n"))
    return file_path


def calculate_weight_diff_for_each_output(feature_sizes, label_sizes, hidden_layer_sizes, clf, top_k=None,
                                          printer=False,
                                          label_list_wanted=None,
                                          summaries_path=None):
    """
    计算权重差异距离累加和

    :param feature_sizes:
    :param label_sizes:
    :param hidden_layer_sizes:
    :param clf: 模型，必须提供权重向量
    :param top_k: 取前k个字节序列的位置
    :param printer:
    :param label_list_wanted: 想要覆盖的基本快，也就是关注的基本快的序号
    :param summaries_path:
    :return:
    """
    if not os.path.exists(summaries_path):
        os.mkdir(summaries_path)
    loguru.logger.debug(f"hidden_layer_sizes: {hidden_layer_sizes}")
    summaries = []
    if top_k is None:
        top_k = feature_sizes
    for i in range(label_sizes):
        if i not in label_list_wanted:
            continue
        summary = []  # 该输出层对应的每个输入层的权重差异距离累加和
        for j in range(feature_sizes):
            if len(hidden_layer_sizes) == 2:
                points = gen_point_2(clf, hidden_layer_sizes, i, j)
            elif len(hidden_layer_sizes) == 3:
                points = gen_point_3(clf, hidden_layer_sizes, i, j)
            else:
                raise Exception("不支持的隐藏层数量")
            c = cdist(points, points, 'mahalanobis')  # 计算每个点到其他点的距离
            summary.append((j, numpy.triu(c, k=0).sum()))  # 取上三角矩阵
        summary.sort(key=lambda x: x[1], reverse=True)  # 降序排列，最前面的是最具有影响力的
        if printer:
            loguru.logger.debug(summary[:top_k])
        summaries.append(summary[:top_k])
        if printer:
            with open(f"{summaries_path}/{str(i)}.csv", "w") as f:
                for k in range(top_k):
                    f.write(str(summary[k][0]) + "," + str(summary[k][1]) + "\n")
    return fusion(summaries, summaries_path)


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
