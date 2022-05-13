import os
import sys
import numpy
import socket
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(BASE_DIR)

import train_dataset_generator
from bb_list_getter import get_wanted_label_with_low_coverage
from sklearn_test import train_sk_model
from train_dataset_generator import read_afl_testcase
from weight_diff_calculate import calculate_weight_diff_for_each_output

max_features = 100
PORT = 12012
SOCKET_MODE = False


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


def start_module(printer=True, test_case_path=None, bb_file_path=None):
    x_data, y_data = read_afl_testcase(max_feature_length=max_features,
                                       base_testcase_path=test_case_path,
                                       bb_file_path=bb_file_path)
    x_data, y_data = numpy.array(x_data), numpy.array(y_data)
    assert x_data.shape[0] == y_data.shape[0]
    print(f"total train data size: {x_data.shape[0]}")
    feature_size = x_data.shape[1]
    label_size = y_data.shape[1]
    hidden_layer_sizes = (3, 3, 3,)
    model = train_sk_model(hidden_layer_sizes, x_data, y_data, is_test=True, max_iter=200)
    bb_list_wanted = get_wanted_label_with_low_coverage(y_data, size=2)
    return calculate_weight_diff_for_each_output(feature_size,
                                                 label_size,
                                                 hidden_layer_sizes,
                                                 clf=model,
                                                 printer=printer,
                                                 label_list_wanted=bb_list_wanted,
                                                 summaries_path=os.path.dirname(bb_file_path))


"""
python main.py _socket_mode _bb_file_path
       0       1            2
"""
if __name__ == '__main__':
    print(sys.argv)
    if len(sys.argv) == 3:
        SOCKET_MODE = sys.argv[1] == "True"
        assert os.path.isfile(sys.argv[2])  # BB_File必须存在
        if SOCKET_MODE:
            server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = ("127.0.0.1", PORT)
            server_socket.bind(address)
            while True:
                now = time.time()
                receive_data, client = server_socket.recvfrom(1024)
                data = receive_data.decode("utf-8")
                print(f"data: {data}")
                if data.startswith("/"):
                    res = start_module(printer=False, test_case_path=data, bb_file_path=sys.argv[2])
                    server_socket.sendto(res.encode("utf-8"), client)
        else:
            start_module(printer=False, test_case_path="../c_example/temp/out",
                         bb_file_path="../c_example/temp/BBFile.txt")
    else:
        print("error: no bb file path")
