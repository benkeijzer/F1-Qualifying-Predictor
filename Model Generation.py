#I created two baseline models:
    #1) Using all available lap time data 
        #Using a recursive NN
    #2) Using the summary data 
        #Using a MLP

import pandas as pd
import numpy as np
import pickle
from tensorflow.keras.preprocessing.sequence import pad_sequences
from sklearn.model_selection import train_test_split
import keras
import tensorflow as tf
from keras import layers

data = pd.read_pickle("Standardised Data.pkl")

###Baseline Model 1:

def pad_lap_times(lap_times):
    if lap_times is None or isinstance(lap_times, float):
        return np.zeros(20)
          #If NA -> fills with 0's
    padded = pad_sequences([lap_times], maxlen=20, padding="post", dtype="float64")[0]
    return padded

for session in ["Practice 1", "Practice 2", "Practice 3"]:
    #Running for ll columns sequentially
    data[session] = data[session].apply(pad_lap_times)
#Padding the lists of lap times to always == 20

Y = data[["Qualifying Results"]]
X = data.drop(["Qualifying Results"], axis=1)

X = np.stack([
    np.stack(X['Practice 1'].to_numpy()),
    np.stack(X['Practice 2'].to_numpy()),
    np.stack(X['Practice 3'].to_numpy())
], axis=-1)
    #Converting the features into a 3D matrix for input into a RNN

x_train, x_test, y_train, y_test = train_test_split(X, Y, test_size=0.2, random_state=42)

y_train = y_train.to_numpy()
y_test = y_test.to_numpy()

y_train = y_train.flatten().astype('int32') - 1  
y_test = y_test.flatten().astype('int32') - 1 
    #Subtracting 1 to set range from 0 - 19 (so it has 20 output categories)

model = keras.Sequential()

model.add(keras.layers.Masking(mask_value=0.0, input_shape=(20, 3)))

model.add(keras.layers.GRU(256, activation = "softmax", return_sequences = True))
model.add(keras.layers.GRU(256, activation = "softmax"))

model.add(keras.layers.Dense(20, activation = "softmax"))

model.summary()

model.compile(loss="sparse_categorical_crossentropy", optimizer=keras.optimizers.Adam(learning_rate = 0.05), metrics=["sparse_categorical_accuracy"])

model.fit(x_train, y_train, epochs=50, batch_size=32, validation_data = (x_test, y_test))




###Summary Model:

summary_data = pd.read_pickle("Summary Data.pkl")

y = summary_data[["Position"]]
x = summary_data.drop(columns = ["Position"])

x = x.to_numpy()
y = y.to_numpy()

y = y.flatten().astype('int32') - 1

x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

summary_model = keras.Sequential()

summary_model.add(keras.layers.Masking(mask_value= -1, input_shape= (12,)))
summary_model.add(keras.layers.Dense(256, activation = "softmax"))
summary_model.add(keras.layers.Dense(20, activation = "softmax"))

summary_model.summary()

summary_model.compile(loss="sparse_categorical_crossentropy", optimizer=keras.optimizers.Adam(learning_rate = 0.05), metrics=["sparse_categorical_accuracy"])

summary_model.fit(x_train, y_train, epochs=100, batch_size=16, validation_data = (x_test, y_test))
