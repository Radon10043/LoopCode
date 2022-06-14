"""
使用sklearn的多层感知机实现模型训练

Q. 多层感知机==全连接神经网络?
A. https://datascience.stackexchange.com/questions/91123/is-a-multi-layer-perceptron-exactly-the-same-as-a-simple-fully-connected-neural

"""
import loguru
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

hidden_layer_sizes = (3, 3, 3,)  # 隐藏层
max_iter = 200  # 最大迭代次数
clf = MLPClassifier(
    # solver='adam',
    # alpha=1e-5,
    hidden_layer_sizes=hidden_layer_sizes,  # 默认是(100,)
    max_iter=max_iter,
    verbose=False
)


def train_sk_model(x_data, y_data, is_test: bool = False, partial_fit=False):
    """
    使用sklearn的多层感知机实现模型训练

    :param x_data:
    :param y_data:
    :param is_test: 是否是测试?若是，则启动数据集划分
    :param partial_fit:
    :return:
    """
    if partial_fit:
        loguru.logger.info(f"partial_fit...x_data size is {x_data.shape}")
        clf.partial_fit(x_data, y_data)
    else:
        if is_test:
            x_train, x_test, y_train, y_test = train_test_split(x_data, y_data)
            loguru.logger.info("training...")
            clf.fit(x_train, y_train)
            y_pred = clf.predict(x_test)
            loguru.logger.debug(f"model f1 score is: {f1_score(y_test, y_pred, average='samples')}")
        else:
            loguru.logger.info("training...")
            clf.fit(x_data, y_data)
    return clf
