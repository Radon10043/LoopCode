"""
使用sklearn的多层感知机实现模型训练

Q. 多层感知机==全连接神经网络?
A. https://datascience.stackexchange.com/questions/91123/is-a-multi-layer-perceptron-exactly-the-same-as-a-simple-fully-connected-neural

"""
import time

import loguru
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
import joblib

hidden_layer_sizes = (3, 3, 3,)  # 隐藏层
max_iter = 200  # 最大迭代次数
clf = MLPClassifier(
    # solver='adam',
    # alpha=1e-5,
    hidden_layer_sizes=hidden_layer_sizes,  # 默认是(100,)
    max_iter=max_iter,
    verbose=True
)


def load_model(model_saved_path):
    global clf
    clf = joblib.load(model_saved_path)
    clf.verbose = False


def train_sk_model(x_data, y_data, is_test: bool = False, partial_fit=False, pre_train_model_save_path=None):
    """
    使用sklearn的多层感知机实现模型训练

    :param x_data:
    :param y_data:
    :param is_test: 是否是测试?若是，则启动数据集划分
    :param partial_fit:
    :param pre_train_model_save_path:
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
            train_start_time = time.time()
            clf.fit(x_data, y_data)
            train_end_time = time.time()
            if pre_train_model_save_path is not None:
                time1 = time.time()
                joblib.dump(clf, pre_train_model_save_path)
                time2 = time.time()
                loguru.logger.info(
                    f"模型保存到{pre_train_model_save_path}, 训练模型花费的时间为{train_end_time - train_start_time}, 保存模型花费时间为{time2 - time1}")
    return clf
