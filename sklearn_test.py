"""
使用sklearn的多层感知机实现模型训练

Q. 多层感知机==全连接神经网络?
A. https://datascience.stackexchange.com/questions/91123/is-a-multi-layer-perceptron-exactly-the-same-as-a-simple-fully-connected-neural

"""
import numpy
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier

import train_dataset_generator

MAX_FEATURES = 320

x_data, y_data = train_dataset_generator.gen_train_dataset_with_bits_array(max_feature_length=MAX_FEATURES)
# x_data, y_data = train_dataset_generator.gen_train_dataset_with_bytes_array(max_feature_length=MAX_FEATURES)
x_data, y_data = numpy.array(x_data), numpy.array(y_data)

feature_sizes = x_data.shape[1]  # (test_case_size,bytes_sequence_size, bytes_pre_bit=8)
label_sizes = y_data.shape[1]  # (test_case_size, basic_block_size)
hidden_layer_sizes = (3, 3,)

X_train, X_test, y_train, y_test = train_test_split(x_data, y_data)
clf = MLPClassifier(
    # solver='adam',
    # alpha=1e-5,
    hidden_layer_sizes=hidden_layer_sizes,  # 默认是(100,)
    # max_iter=1000,
    verbose=True
)

clf.fit(X_train, y_train)
print(clf.score(X_test, y_test))
