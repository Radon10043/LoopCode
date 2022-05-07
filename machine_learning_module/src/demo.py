import numpy
import numpy as np

layer_sizes = (5, 5,)
temp = np.cumprod(layer_sizes)[-1]
l = np.zeros(shape=(temp, len(layer_sizes) + 1), dtype=int)
