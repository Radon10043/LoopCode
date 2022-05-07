import numpy

from machine_learning_module.src import train_dataset_generator
from machine_learning_module.src.sklearn_test import train_sk_model
from machine_learning_module.src.train_dataset_generator import read_afl_testcase
from machine_learning_module.src.weight_diff_calculate import calculate_weight_diff_for_each_output

max_features = 400


def test_case_type_1():
    """
    比特序列，即每一个元素是[0,0,1,1,1,1,...]
    :return:
    """
    return train_dataset_generator.gen_train_dataset_with_bits_array(max_feature_length=max_features)


def test_case_type_2():
    """
    字节序列，即每一个元素是[\x00,\x00,\x01,\x01,\x01,\x01,...]
    :return:
    """
    return train_dataset_generator.gen_train_dataset_with_bytes_array(max_feature_length=max_features)


if __name__ == '__main__':
    # x_data, y_data = test_case_type_1()
    # x_data, y_data = test_case_type_2()
    x_data, y_data = read_afl_testcase(max_feature_length=35)
    x_data, y_data = numpy.array(x_data), numpy.array(y_data)
    hidden_layer_sizes = (3, 3,)
    model = train_sk_model(hidden_layer_sizes, x_data, y_data, is_test=True, max_iter=500)
    feature_size = x_data.shape[1]
    label_size = y_data.shape[1]
    calculate_weight_diff_for_each_output(feature_size, label_size, hidden_layer_sizes, clf=model)
