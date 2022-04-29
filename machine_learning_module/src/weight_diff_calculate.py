import numpy as np


def euclidean(point1, point2):
    """
    计算两点之间的欧式距离

    :param point1:
    :param point2:
    :return:
    """
    assert len(point1) == len(point2) == 3  # 仅支持两层隐藏层，也就是三个维度
    diff1 = point1[0] - point2[0]
    diff2 = point1[1] - point2[1]
    diff3 = point1[2] - point2[2]
    return np.sqrt(diff1 ** 2 + diff2 ** 2 + diff3 ** 2)


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
    assert len(hidden_layer_sizes) == 2  # 仅支持两层隐藏层
    for i in range(label_sizes):
        summary = []
        for j in range(feature_sizes):
            points = []
            sum_of_weight_diff = 0
            for d0 in range(hidden_layer_sizes[0]):
                for d1 in range(hidden_layer_sizes[1]):
                    points.append(
                        (
                            clf.coefs_[0][j][d0],
                            clf.coefs_[1][d0][d1],
                            clf.coefs_[2][d1][i]
                        )
                    )
            for m in range(len(points)):
                for n in range(m + 1, len(points)):
                    sum_of_weight_diff += euclidean(points[m], points[n])
            summary.append((sum_of_weight_diff, j))
        summary.sort(key=lambda x: x[0], reverse=True)
        print(f"{i}:{summary[:top_k]}")
