import keras.optimizers
import numpy
from keras.models import Sequential
from keras.layers import Dense, Activation
from sklearn.model_selection import train_test_split

import train_dataset_generator

MAX_FEATURES = 10000
MAX_BASIC_BLOCKS = 5

model = Sequential()
model.add(Dense(4096, input_dim=MAX_FEATURES))
model.add(Activation('relu'))
model.add(Dense(MAX_BASIC_BLOCKS))
model.add(Activation('sigmoid'))
opt = keras.optimizers.adam_v2.Adam(learning_rate=0.01)
model.compile(loss='binary_crossentropy', optimizer=opt, metrics=['accuracy'])
model.summary()

x_data, y_data = train_dataset_generator.gen_train_dataset_with_bits_array(max_feature_length=MAX_FEATURES)
# x_data, y_data = train_dataset_generator.gen_train_dataset_with_bytes_array()
x_data, y_data = numpy.array(x_data), numpy.array(y_data)

feature_sizes = x_data.shape[1]  # (test_case_size,bytes_sequence_size, bytes_pre_bit=8)
label_sizes = y_data.shape[1]  # (test_case_size, basic_block_size)
hidden_layer_sizes = (4096, 10,)

X_train, X_test, y_train, y_test = train_test_split(x_data, y_data)
model.fit(X_train, y_train, epochs=100, batch_size=32)
