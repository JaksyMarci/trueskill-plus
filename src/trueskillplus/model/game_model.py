import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
from matplotlib import pyplot as plt
"""
Trains a predictive model used to guess scores based on past matches.
"""


def train_csgo_model(df: pd.DataFrame):
    # drop unnecessary columns
    df = df[['winner', 't1_points', 't2_points', 'is_bestof', 'kdr_diff']]

    # Convert column to a one-hot encoded format
    df = pd.get_dummies(df, columns=['winner', 'is_bestof'], dtype=np.float64)

    print(df.sample(10))
    # Split the data into input and output columns
    # winner_t1, winner_t2, t1_points, t2_points, is_bestof_true, is_bestof_false

    X = df.drop(['kdr_diff'], axis=1).values
    y = df[['kdr_diff']].values

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Create MLP
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(6,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1)
    ])

    model.compile(loss='mse', optimizer='adam')

    model.fit(X_train, y_train, epochs=50, batch_size=10,
              callbacks=tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3))

    test_loss = model.evaluate(X_test, y_test)
    print('Test loss:', test_loss)
    """
    df_test = pd.concat([pd.DataFrame(model.predict(X_test), columns=['Predicted']),
                        pd.DataFrame(y_test, columns=['Real']),
                        pd.DataFrame(X_test, columns=['t1_points', 't2_points', 't1_pred_win','a','b','c','d'])],
                        axis=1)

    print(df_test.sample(20))
    """

    return model


def train_league_model(df: pd.DataFrame):
    df = df[['golddiff', 'bResult', 'rResult', 'bKills', 'bTowers', 'bInhibs', 'bDragons', 'bBarons',
             'bHeralds', 'rKills', 'rTowers', 'rInhibs', 'rDragons', 'rBarons', 'rHeralds']].astype(float)

    X = df.drop(['golddiff'], axis=1).values
    y = df[['golddiff']].values

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(14,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1)
    ])

    model.compile(loss='mse', optimizer='adam')

    model.fit(X_train, y_train, epochs=200, batch_size=10,
              callbacks=tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3))

    test_loss = model.evaluate(X_test, y_test)
    print('Test loss:', test_loss)
    return model
