import os
import time

import loguru

AFL_SHOWMAP_BINARY_PATH = "/home/yagol/LoopCode/afl-yagol/afl-showmap"

visited_path = set()


def runner(testcase_dir, binary_file_path, base_cmd, save_path):
    loguru.logger.info(f"keep_showmap.runner(Thread), {testcase_dir},{binary_file_path},{base_cmd},{save_path}")
    timer = 0
    edge = set()
    open(save_path, "w")
    while True:
        time.sleep(60)
        timer += 1
        loguru.logger.info(f"开始第{timer}次路径信息统计...")
        for root, dirs, files in os.walk(testcase_dir):
            for file in files:
                testcase_path = os.path.join(root, file)
                if testcase_path.endswith(".txt"):
                    continue
                if testcase_path in visited_path:
                    loguru.logger.debug(f"{testcase_path}的路径已经分析过了")
                    continue
                visited_path.add(testcase_path)
                cmd = f"{AFL_SHOWMAP_BINARY_PATH} -q -e -o /dev/stdout -m 512 -t 500 {binary_file_path} {base_cmd} {testcase_path}"
                loguru.logger.debug(f"分析路径CMD:{cmd}")
                out = os.popen(cmd).readlines()
                for o in out:
                    edge.add(o.strip())
        with open(save_path, "a") as save_file:
            save_file.write(f"time: {timer}, edge: {len(edge)}\n")
            loguru.logger.info(f"完成第{timer}次路径信息统计")


def runner_test(testcase_dir, binary_file_path, base_cmd):
    loguru.logger.info(f"keep_showmap.runner(Thread), {testcase_dir},{binary_file_path},{base_cmd}")
    timer = 0
    edge = set()
    timer += 1
    loguru.logger.info(f"开始第{timer}次路径信息统计")
    for root, dirs, files in os.walk(testcase_dir):
        for file in files:
            testcase_path = os.path.join(root, file)
            if testcase_path.endswith(".txt"):
                continue
            if testcase_path in visited_path:
                loguru.logger.info(f"{testcase_path}的路径已经分析过了")
                continue
            visited_path.add(testcase_path)
            cmd = f"{AFL_SHOWMAP_BINARY_PATH} -q -e -o /dev/stdout -m 512 -t 500 {binary_file_path} {base_cmd} {testcase_path}"
            # loguru.logger.info(f"分析路径CMD:{cmd}")
            out = os.popen(cmd).readlines()
            for o in out:
                edge.add(o.strip())
            print(testcase_path, len(edge))


runner_test("/home/yagol/LoopCode/scripts/jasper-3.0.3/obj-loop/out", "/home/yagol/LoopCode/scripts/jasper-3.0.3-gcc/obj-loop/src/app/jasper", "--output /tmp/out_afl_origin.jpg --input")
