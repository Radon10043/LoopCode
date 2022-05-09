import math
import os
import shutil


def fusion(summaries):
    indexes_and_probabilities = dict()
    for summary in summaries:
        for index, probability in summary:
            if index not in indexes_and_probabilities:
                indexes_and_probabilities[index] = probability
            else:
                indexes_and_probabilities[index] += probability
    with open("../out/fusion.csv", "w") as f:
        for index, probability in indexes_and_probabilities.items():
            f.write(str(index) + "," + str(probability) + "\n")


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


def calculate_weight_diff_for_each_output(feature_sizes, label_sizes, hidden_layer_sizes, clf, top_k=None,
                                          printer=False,
                                          label_list_wanted=None):
    """
    计算权重差异距离累加和

    :param feature_sizes:
    :param label_sizes:
    :param hidden_layer_sizes:
    :param clf: 模型，必须提供权重向量
    :param top_k:
    :param printer:
    :param label_list_wanted:
    :return:
    """
    if os.path.isdir("../out"):
        shutil.rmtree("../out")
    os.mkdir("../out")
    print("hidden_layer_sizes:", hidden_layer_sizes)
    summaries = []
    if top_k is None:
        top_k = label_sizes
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
            sum_of_weight_diff = 0
            for m in range(len(points) - 1):
                # sum_of_weight_diff += euclidean(points[m], points[m + 1])
                for n in range(m + 1, len(points)):
                    sum_of_weight_diff += euclidean(points[m], points[n])
            summary.append((j, sum_of_weight_diff))
        summary.sort(key=lambda x: x[1], reverse=True)  # 降序排列，最前面的是最具有影响力的
        if printer:
            print(summary[:top_k])
        summaries.append(summary[:top_k])
        with open(f"../out/{str(i)}.csv", "w") as f:
            for k in range(top_k):
                f.write(str(summary[k][0]) + "," + str(summary[k][1]) + "\n")
    fusion(summaries)


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
