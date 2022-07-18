"""
获得想要获取的指定label，也就是循环或者基本快的位置，用List保存

"""
from typing import List


def get_wanted_label_with_low_coverage(coverage_datas, size) -> List[int]:
    """
    基于覆盖情况获得label的list,排在前面的是覆盖率降低的

    """
    bb_coverage_infos = []
    for bb_index in range(coverage_datas.shape[1]):
        bb_coverage_infos.append((bb_index, sum(coverage_datas[:, bb_index])))
    bb_coverage_infos.sort(key=lambda x: x[1])
    return [x[0] for x in bb_coverage_infos[:size]]
