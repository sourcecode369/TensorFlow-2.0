# -*- coding: utf-8 -*-
"""TensorFlow-2.0-Notebook-4-Regression-Predict-Fuel-Efficiency.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1JK8fYNHDPjqbgOqp9bYmSXmMwwUxwdq1
"""

# Commented out IPython magic to ensure Python compatibility.
# %%time
# from __future__ import absolute_import, division, print_function, unicode_literals
# %load_ext tensorboard
# %load_ext autoreload
# %autoreload 2
# import pathlib
# 
# import numpy as np
# import pandas as pd
# import matplotlib.pyplot as plt
# %matplotlib inline 
# %config InlineBackend.figure_format = "retina"
# import seaborn as sns
# sns.set(rc={"figure.figsize":(12,10)})
# sns.set_style("whitegrid")
# 
# try:
#   %tensorflow_version 2.x
# except:
#   print("TensorFlow 2.0 Not Found.")
# 
# import tensorflow as tf
# from tensorflow import keras
# from tensorflow.keras import layers
# from sklearn.model_selection import *
# 
# print("Version: ", tf.__version__)
# print("Executing eagerly: ", tf.executing_eagerly())
# print("GPU is, ", "available." if tf.test.is_gpu_available() else "unavailable.")
# 
# print("Seeding...")
# 
# import os
# import random
# import sys
# import gc
# import datetime
# gc.enable()
# 
# def seedall(seed):
#   try:
#     np.random.seed(seed)
#     random.seed(seed)
#     tf.radnom.seed(seed)
#     #os.environment["PYTHONHASHSEED"] = seed
#     print("Seeding sucessful.")
#   except:
#     print("Reason: ", Exception)
#     print("Failed to initialize seed.")
# 
# from IPython.display import display, clear_output
# 
# seedall(999)
# print("Supressing warnings..")
# import warnings
# warnings.filterwarnings("ignore")
# print("Done.!")

dataset_path = keras.utils.get_file("auto-mpg.data", "http://archive.ics.uci.edu/ml/machine-learning-databases/auto-mpg/auto-mpg.data")
dataset_path

column_names = ['MPG','Cylinders','Displacement','Horsepower','Weight',
                'Acceleration', 'Model Year', 'Origin']
raw_dataset = pd.read_csv(dataset_path,names=column_names,na_values='?',comment='\t', sep=" ", skipinitialspace=True)

dataset = raw_dataset.copy()

dataset.tail()

dataset.isna().sum().sort_index()/len(dataset)

dataset["Horsepower"] = dataset["Horsepower"].fillna(np.mean(dataset["Horsepower"]))

dataset.head()

origin = dataset.pop('Origin')
dataset["USA"] = (origin==1)*1.0
dataset["Europe"] = (origin==2)*1.0
dataset["Japan"] = (origin==3)*1.0

dataset.tail()

train_dataset = dataset.sample(frac=0.8,random_state=999)
test_dataset = dataset.drop(train_dataset.index)

train_dataset.dtypes

sns.pairplot(train_dataset[["MPG","Cylinders","Displacement","Weight"]],diag_kind="kde")
plt.show()

train_stats = train_dataset.describe(include="all")
train_stats.pop("MPG")
train_stats = train_stats.transpose()
train_stats

train_labels = train_dataset.pop("MPG")
test_labels = test_dataset.pop("MPG")

def normalize(x):
  return (x - train_stats["mean"]) / train_stats["std"]

def denormalize(x):
  return (x * train_stats["std"] + train_stats["mean"])

normed_train_data = normalize(train_dataset)
normed_test_data = normalize(test_dataset)

normed_train_data.head()

def build_model():
  model = tf.keras.Sequential([
                               layers.Dense(256, activation=tf.nn.relu, input_shape=[len(normed_train_data.keys())], kernel_initializer="glorot_uniform"),
                               layers.Dropout(0.2),
                               layers.BatchNormalization(),
                               layers.Dense(128,activation=tf.nn.relu, use_bias=True, kernel_initializer="glorot_uniform"),
                               layers.Dropout(0.2),
                               layers.BatchNormalization(),
                               layers.Dense(64,activation=tf.nn.relu,kernel_initializer="glorot_uniform"),
                               layers.Dropout(0.2),
                               layers.Dense(1)
  ])

  optimizer = tf.keras.optimizers.RMSprop(0.001)

  model.compile(optimizer=optimizer, loss=["mean_squared_error"], metrics=["mean_squared_error", "mean_absolute_error"])

  model.summary()

  return model

regressor = build_model()

checkpoint = tf.keras.callbacks.ModelCheckpoint("model_regressor.h5",monitor="val_loss",verbose=1,save_best_only=True,mode="auto")
reduce_lr = tf.keras.callbacks.ReduceLROnPlateau(monitor="val_loss",factor=0.5,patience=5,verbose=1,mode="auto",min_lr=0.000001)
logdir = os.path.join("logs", datetime.datetime.now().strftime("%Y%m%d-%H%M%S"))
tensorboard = tf.keras.callbacks.TensorBoard(log_dir=logdir,histogram_freq=1)
early_stopping = tf.keras.callbacks.EarlyStopping(monitor="val_loss",verbose=1,mode="auto", patience=30)

class PlotLearning(tf.keras.callbacks.Callback):
  def on_train_begin(self, logs={}):
    self.i = 0
    self.x = []
    self.loss = []
    self.val_loss = []
    self.mae = []
    self.val_mae = []
    self.fig = plt.figure()
    self.logs = []

  def on_epoch_end(self, epoch, logs={}):
      
    self.logs.append(logs)
    self.x.append(self.i)
    self.loss.append(logs.get('loss'))
    self.mae.append(logs.get('mean_absolute_error'))
    
    self.val_loss.append(logs.get('val_loss'))        
    self.val_mae.append(logs.get('val_mean_absolute_error'))
    
    self.i += 1
    f, ax = plt.subplots(1, 2, figsize=(12,4), sharex=True)
    ax = ax.flatten()
    clear_output(wait=True)
    
    ax[0].plot(self.x, self.loss, label="loss", lw=2)
    ax[0].plot(self.x, self.val_loss, label="val loss")
    #ax[0].set_ylim(bottom=0.)
    ax[0].legend()
    ax[0].grid(True)
      
    ax[1].plot(self.x, self.mae, label="Mean Absolute Error", lw=2)
    ax[1].plot(self.x, self.val_mae, label="val Mean Absolute Error")
    #ax[1].set_ylim(bottom=0.)
    ax[1].legend()
    ax[1].grid(True)
      
    plt.show();
        
plotLoss = PlotLearning()

# Commented out IPython magic to ensure Python compatibility.
EPOCHS = 5000
# %tensorboard --logdir logs
history = regressor.fit(normed_train_data, 
                    train_labels, 
                    epochs=EPOCHS, 
                    validation_split=0.2,
                    verbose=1,
                    callbacks=[reduce_lr,plotLoss,tensorboard,checkpoint,early_stopping])

from tensorboard import notebook
notebook.list()
notebook.display(port=6006, height=1000)

results = regressor.evaluate(normed_test_data,test_labels)
for name, value in zip(regressor.metrics_names,results):
  print("%s:%.3f"%(name,value))

test_predictions = regressor.predict(normed_test_data).flatten()

plt.scatter(test_labels, test_predictions)
plt.xlabel(" True Values [MPG]")
plt.ylabel(" Predictions [MPG]")
plt.axis("equal")
plt.axis("square")
plt.xlim([0,plt.xlim()[1]])
plt.ylim([0,plt.ylim()[1]])
_ = plt.plot([-100, 100], [-100, 100])

error = test_predictions - test_labels
plt.hist(error, bins = 25)
plt.xlabel("Prediction Error [MPG]")
_ = plt.ylabel("Count")