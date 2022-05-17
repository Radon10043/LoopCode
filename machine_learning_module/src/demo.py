import numpy
from sklearn.neural_network import MLPClassifier

clf = MLPClassifier(
    # solver='adam',
    # alpha=1e-5,
    hidden_layer_sizes=(3, 3),  # 默认是(100,)
    max_iter=200,
    verbose=True
)
x = numpy.random.rand(100, 2)
y=numpy.random.randint(2, size=100)
clf.fit(x, y)
print("==========================")
x_update = [[2, 2], [3, 3]]
y_update = [1, 0]
clf.partial_fit(x_update, y_update)
print(clf.predict([[2, 2]]))
