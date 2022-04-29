"""
测试用例和插桩生成器
"""
import random
import string
import tqdm
import loguru
import numpy.random
import pandas as pd

test_case_csv_path = '../testcase.csv'


def gen_test_case_param(size: int = 10):
    """
    生成size个测试用例参数
    """
    for i in range(size):
        _p1 = numpy.random.randint(0, 300)
        _p2 = numpy.random.randint(0, 300)
        _p3 = ''.join(random.sample(string.ascii_letters + string.digits,
                                    # numpy.random.randint(1, len(string.ascii_letters + string.digits))
                                    10
                                    ))
        _p4 = random.choice([0, 1])
        _p5 = numpy.random.randint(0, 300)
        _p6 = numpy.random.randint(0, 300)
        _p7 = ''.join(random.sample(string.ascii_letters + string.digits,
                                    # numpy.random.randint(1, len(string.ascii_letters + string.digits))
                                    10
                                    ))
        yield _p1, _p2, _p3, _p4, _p5, _p6, _p7


@loguru.logger.catch()
def main(_p1: int, _p2: int, _p3: str, _p4: int, _p5: int, _p6: int, _p7: str):
    if isinstance(_p1, int) \
            and isinstance(_p2, int) \
            and isinstance(_p3, str) \
            and isinstance(_p4, int) \
            and isinstance(_p5, int) \
            and isinstance(_p6, int) \
            and isinstance(_p7, str):
        # 插桩变量
        _c1, _c2, _c3, _c4, _c5 = False, False, False, False, False
        if _p1 + _p6 >= 500:
            _c1 = True
        if _p5 > 200:
            _c2 = True
        if _p3.startswith('a') or p4 == 1:
            _c3 = True
        if _p2 > 10:
            _c4 = True
        if len(_p7) > 31:
            _c5 = True
        return _c1, _c2, _c3, _c4, _c5
    else:
        raise ValueError('param type error')


if __name__ == '__main__':
    # 生成测试用例
    test_case_size = 10000
    dataframe = pd.DataFrame(columns=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'c1', 'c2', 'c3', 'c4'])
    with tqdm.tqdm(total=test_case_size) as pbar:
        for p1, p2, p3, p4, p5, p6, p7 in gen_test_case_param(test_case_size):
            c1, c2, c3, c4, c5 = main(p1, p2, p3, p4, p5, p6, p7)
            dataframe = pd.concat([dataframe, pd.DataFrame({
                "p1": [int(p1)],
                "p2": [int(p2)],
                "p3": [str(p3)],
                "p4": [int(p4)],
                "p5": [int(p5)],
                "p6": [int(p6)],
                "p7": [str(p7)],
                "c1": [bool(c1)],
                "c2": [bool(c2)],
                "c3": [bool(c3)],
                "c4": [bool(c4)],
                "c5": [bool(c5)]
            })], ignore_index=True)
            pbar.update(1)
    dataframe.to_csv(test_case_csv_path, index=False,
                     columns=['p1', 'p2', 'p3', 'p4', 'p5', 'p6', 'p7', 'c1', 'c2', 'c3', 'c4', 'c5'])
