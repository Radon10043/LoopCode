import os
import shutil
import time

import loguru


def kill_process_by_socket_port(port):
    output = os.popen("netstat -nlp | grep :" + str(port) + " | awk '{print $6}'").readlines()
    if len(output) == 0:  # 说明端口没有被占用
        return
    assert len(output) == 1, f"检测端口是否被占用时出现错误, 存在{len(output)}个pdi"
    output = output[0].strip()
    assert output.split("/")[1] == "python", f"端口占用的程序不是python"
    pid = output.split("/")[0]
    loguru.logger.info(f"尝试kill的pid为: {pid}")
    kill_output = os.popen(f"kill -9 {pid}").readlines()
    assert len(kill_output) == 0, "kill端口占用程序时出错"
    loguru.logger.info("kill成功, 为了模拟堵塞效果, sleep一段时间")
    time.sleep(2)


def trim_pre_train_testcase(pre_train_testcase):
    seed_path = os.path.join(pre_train_testcase, "seed")
    os.mkdir(seed_path)
    testcase_dirs = [f"{pre_train_testcase}/crashes", f"{pre_train_testcase}/queue", f"{pre_train_testcase}/hangs"]
    for testcase_dir in testcase_dirs:
        for root, dirs, files in os.walk(testcase_dir):
            for file_name in files:
                file_path = os.path.join(root, file_name)
                shutil.copy(file_path, seed_path)


def get_top_k_edge_or_bb():
    pass
