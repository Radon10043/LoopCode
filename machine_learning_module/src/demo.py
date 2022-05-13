import math

from numpy import *
import numpy
from scipy.spatial.distance import cdist

if __name__ == '__main__':
    # 初始化数据点集，或者从其它地方加载
    x = numpy.random.random((5000, 3))
    c = cdist(x, x, 'euclidean')
    for i in range(x.shape[0]):
        for j in range(i + 1, x.shape[0]):
            print(math.dist(x[i], x[j]), c[i][j])
