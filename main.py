"""
基于权重距离累加和量化全连接神经网络输出与输入之间的关系

@author: yagol
2022.4.11 TODO:标签与输出层之间的关系？
2022.4.12 TODO:能不能转换为多标签？
"""
from collections import Counter

import tensorflow as tf
import numpy as np

x_size = 10
y_size = 3

x_data, y_data = [], []
for i in range(100):
    max_random = 100
    value0 = np.random.uniform(0, max_random)
    value1 = np.random.uniform(0, max_random)
    value2 = np.random.uniform(0, max_random)
    value3 = np.random.uniform(0, max_random)
    value4 = np.random.uniform(0, max_random)
    value5 = np.random.uniform(0, max_random)
    value6 = np.random.uniform(0, max_random)
    value7 = np.random.uniform(0, max_random)
    value8 = np.random.uniform(0, max_random)
    value9 = np.random.uniform(0, max_random)
    x_data.append([value0, value1, value2, value3, value4, value5, value6, value7, value8, value9])
    check_label1 = value1
    check_label2 = value2
    check_label3 = value3
    label = 0
    if check_label1 > 25:
        if check_label2 > 25:
            if check_label3 > 25:
                label = 1
            else:
                label = 2
        else:
            if check_label3 > 25:
                label = 3
            else:
                label = 4
    else:
        if check_label2 > 25:
            if check_label3 > 25:
                label = 5
            else:
                label = 6
        else:
            if check_label3 > 25:
                label = 7
            else:
                label = 8
    y_data.append(label)

x_data = np.array(x_data)
y_data = np.array(y_data)

x_train = x_data[:-30]
y_train = y_data[:-30]

x_test = x_data[-30:]
y_test = y_data[-30:]

# 转换x的数据类型，否则后面矩阵相乘时会因数据类型不一致报错
x_train = tf.cast(x_train, tf.float32)
x_test = tf.cast(x_test, tf.float32)

train_db = tf.data.Dataset.from_tensor_slices((x_train, y_train)).batch(32)
test_db = tf.data.Dataset.from_tensor_slices((x_test, y_test)).batch(32)

"""
隐藏层第1个。输入为特征的数量，输出为3层权重和偏置
"""
w1 = tf.Variable(tf.random.truncated_normal([x_size, 3], stddev=0.1, seed=1))
b1 = tf.Variable(tf.random.truncated_normal([3], stddev=0.1, seed=1))
"""
隐藏层第2个。
"""
w2 = tf.Variable(tf.random.truncated_normal([3, 3], stddev=0.1, seed=1))
b2 = tf.Variable(tf.random.truncated_normal([3], stddev=0.1, seed=1))

"""
隐藏层第3个。输出为3个坐标（不确定）
"""
w3 = tf.Variable(tf.random.truncated_normal([3, 3], stddev=0.1, seed=1))
b3 = tf.Variable(tf.random.truncated_normal([3], stddev=0.1, seed=1))

loss_all = 0  # 损失值
lr = 0.1  # 学习率
epoch = 100  # 训练网络时的迭代次数
total_correct = 0  # 预测正确的样本数量

# 模型训练
for epoch in range(epoch):
    for step, (x_train, y_train) in enumerate(train_db):
        with tf.GradientTape() as tape:
            y_1 = tf.matmul(x_train, w1) + b1
            y_1 = tf.nn.relu(y_1)

            y_2 = tf.matmul(y_1, w2) + b2
            y_2 = tf.nn.relu(y_2)

            y = tf.matmul(y_2, w3) + b3
            y = tf.nn.softmax(y)

            y_ = tf.one_hot(y_train, depth=3)

            # 损失函数使用均方误差
            loss = tf.reduce_mean(tf.square(y - y_))

            loss_all += loss.numpy()

        # 这里是对loss求导
        grads = tape.gradient(loss, [w1, b1, w2, b2, w3, b3])

        # 更新各个参数
        w1.assign_sub(lr * grads[0])
        b1.assign_sub(lr * grads[1])
        w2.assign_sub(lr * grads[2])
        b2.assign_sub(lr * grads[3])
        w3.assign_sub(lr * grads[4])
        b3.assign_sub(lr * grads[5])

    print("Epoch {}".format(epoch))

# 模型预测
for x_test, y_test in test_db:
    y_1 = tf.matmul(x_test, w1) + b1
    y_2 = tf.matmul(y_1, w2) + b2
    y = tf.matmul(y_2, w3) + b3
    y = tf.nn.softmax(y)

    pred = tf.argmax(y, axis=1)
    pred = tf.cast(pred, dtype=y_test.dtype)
    correct = tf.cast(tf.equal(pred, y_test), dtype=tf.int32)
    correct = tf.reduce_sum(correct)
    total_correct += correct

acc = total_correct / y_test.shape[0]
print('test_acc', acc.numpy())
print("======")


def euclidean(point1, point2):
    diff1 = point1[0] - point2[0]
    diff2 = point1[1] - point2[1]
    diff3 = point1[2] - point2[2]
    return np.sqrt(diff1 ** 2 + diff2 ** 2 + diff3 ** 2)


def calculate(start, end):
    path0 = [w1[start][0], w2[0][0], w3[0][end]]
    path1 = [w1[start][1], w2[1][0], w3[0][end]]
    path2 = [w1[start][2], w2[2][0], w3[0][end]]
    path3 = [w1[start][0], w2[0][1], w3[1][end]]
    path4 = [w1[start][1], w2[1][1], w3[1][end]]
    path5 = [w1[start][2], w2[2][1], w3[1][end]]
    path6 = [w1[start][0], w2[0][2], w3[2][end]]
    path7 = [w1[start][1], w2[1][2], w3[2][end]]
    path8 = [w1[start][2], w2[2][2], w3[2][end]]
    paths = [path0, path1, path2, path3, path4, path5, path6, path7, path8]
    dis_sum = 0
    for point1_index in [0, 1, 2, 3, 4, 5, 6, 7, 8]:
        for point2_index in range(point1_index + 1, 9):
            dis_sum += euclidean(paths[point1_index], paths[point2_index])
    return dis_sum


for y_i in range(y_size):
    result = []
    for x_i in range(x_size):
        dis = calculate(x_i, y_i)
        print(f"对于第 {y_i} 号输出神经元，第 {x_i} 号输入神经元的权重距离和为: {dis}")
        result.append((dis, x_i))
    result.sort(reverse=True)
    sorted_x_i = []
    for index, (_, one_sorted_x_i) in enumerate(result):
        """
        输出排序后的结果，按照权重距离和由大到小输出
        """
        sorted_x_i.append(one_sorted_x_i)
    print(sorted_x_i)
    print("======")
