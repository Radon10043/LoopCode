"""
使用sklearn的多层感知机实现模型训练

Q. 多层感知机==全连接神经网络?
A. https://datascience.stackexchange.com/questions/91123/is-a-multi-layer-perceptron-exactly-the-same-as-a-simple-fully-connected-neural

"""
from sklearn.metrics import f1_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


def train_sk_model(hidden_layer_sizes, x_data, y_data, max_iter=200, is_test: bool = False, verbose=False):
    """
    使用sklearn的多层感知机实现模型训练

    :param verbose:
    :param max_iter:
    :param hidden_layer_sizes:
    :param x_data:
    :param y_data:
    :param is_test: 是否是测试?若是，则启动数据集划分
    :return:
    """
    clf = MLPClassifier(
        # solver='adam',
        # alpha=1e-5,
        hidden_layer_sizes=hidden_layer_sizes,  # 默认是(100,)
        max_iter=max_iter,
        verbose=verbose
    )
    if is_test:
        x_train, x_test, y_train, y_test = train_test_split(x_data, y_data)
        print("training...")
        clf.fit(x_train, y_train)
        y_pred = clf.predict(x_test)
        print(f"model f1 score is: {f1_score(y_test, y_pred,average='samples')}")
    else:
        print("training...")
        clf.fit(x_data, y_data)
    return clf
