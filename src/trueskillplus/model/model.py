import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split
import numpy as np
"""
Trains a predictive model used to guess scores based on past matches.
"""
def train_csgo_model(df : pd.DataFrame):
    #drop unnecessary columns
    df = df[['winner', 't1_points', 't2_points', 'is_bestof', 'kdr_diff']]

    # Convert column to a one-hot encoded format
    df= pd.get_dummies(df, columns=['winner', 'is_bestof'], dtype=np.float64)

    print(df.sample(10))
    # Split the data into input and output columns
    #winner_t1, winner_t2, t1_points, t2_points, is_bestof_true, is_bestof_false


    X = df.drop(['kdr_diff'], axis=1).values
    y = df[['kdr_diff']].values

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    # Create a multilayer perceptron model with ReLU activation
    model = tf.keras.models.Sequential([
        tf.keras.layers.Dense(32, activation='relu', input_shape=(6,)),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(8, activation='relu'),
        tf.keras.layers.Dense(1)
    ])

    # Compile the model with a mean squared error loss and Adam optimizer
    model.compile(loss='mse', optimizer='adam')

    # Fit the model on the training data
    model.fit(X_train, y_train, epochs=50, batch_size=10, callbacks=tf.keras.callbacks.EarlyStopping(monitor='loss', patience=3))

    # Evaluate the model on the testing data
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


    """
    problems with this:
    -not accurate as much as i want
    -bo3-s maybe should be removed, instead of including it in the model. or smth
    -no validation set
    -

    """

