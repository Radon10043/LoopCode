"""
测试用例和插桩生成器
"""
import random
import string

import loguru
import numpy.random
import pandas as pd

test_case_csv_path = 'testcase.csv'


def gen_test_case_param(size: int = 10):
    """
    生成10个测试用例参数
    """
    for i in range(size):
        _p1 = numpy.random.randint(0, 100)
        _p2 = numpy.random.uniform(0, 100)
        _p3 = ''.join(random.sample(string.ascii_letters + string.digits, 8))
        _p4 = random.choice([0, 1])
        _p5 = numpy.random.uniform(0, 100)
        _p6 = numpy.random.randint(0, 100)
        yield _p1, _p2, _p3, _p4, _p5, _p6


@loguru.logger.catch()
def main(_p1: int, _p2: float, _p3: str, _p4: int, _p5: float, _p6: int):
    if isinstance(_p1, int) \
            and isinstance(_p2, float) \
            and isinstance(_p3, str) \
            and isinstance(_p4, int) \
            and isinstance(_p5, float) \
            and isinstance(_p6, int):
        # 插桩变量
        _c1, _c2, _c3, _c4 = False, False, False, False
        if _p1 + _p6 >= 120:
            _c1 = True
        if _p5 > 30:
            _c2 = True
        if _p3.startswith('a') or p4 == 1:
            _c3 = True
        if _p2 > 10:
            _c4 = True
        return _c1, _c2, _c3, _c4
    else:
        raise ValueError('param type error')


if __name__ == '__main__':
    dataframe = pd.DataFrame(columns=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'c1', 'c2', 'c3', 'c4'])
    for p1, p2, p3, p4, p5, p6 in gen_test_case_param(500):
        c1, c2, c3, c4 = main(p1, p2, p3, p4, p5, p6)
        dataframe = pd.concat([dataframe, pd.DataFrame({
            "p1": [int(p1)],
            "p2": [float(p2)],
            "p3": [str(p3)],
            "p4": [int(p4)],
            "p5": [float(p5)],
            "p6": [int(p6)],
            "c1": [bool(c1)],
            "c2": [bool(c2)],
            "c3": [bool(c3)],
            "c4": [bool(c4)]
        })], ignore_index=True)
    dataframe.to_csv(test_case_csv_path, index=False,
                     columns=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'c1', 'c2', 'c3', 'c4'])
