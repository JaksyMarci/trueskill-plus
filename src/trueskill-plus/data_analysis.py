import itertools
import pandas as pd
import math
import sys
from matplotlib import pyplot as plt
import numpy as np
sys.path.append("..")

from trueskill import Rating, rate_1vs1, TrueSkill, rate_csgo

ratings = {}
mu_values = {}
# pro csgo games from 2016-2020
# source: https://www.kaggle.com/datasets/gabrieltardochi/counter-strike-global-offensive-matches?resource=download

df = pd.read_csv('csgo_games.csv')[['team_1', 'team_2', 'winner', 't1_points', 't2_points',
                                   't1_player1_kdr', 't1_player2_kdr', 't1_player3_kdr', 't1_player4_kdr', 't1_player5_kdr',
                                    't2_player1_kdr', 't2_player2_kdr', 't2_player3_kdr', 't2_player4_kdr', 't2_player5_kdr',
                                    't1_player1_dmr', 't1_player2_dmr', 't1_player3_dmr', 't1_player4_dmr', 't1_player5_dmr',
                                    't2_player1_dmr', 't2_player2_dmr', 't2_player3_dmr', 't2_player4_dmr', 't2_player5_dmr']]


#DANGER! the dataset includes scores in a bo3 and bo5 format as well, not just singular matches. this could fuck up things, drop scores if it does.
#if you dont want to use scores, you can use mfkin uhh 'dmr'

df['t1_avg_kdr'] = (df['t1_player1_kdr'] + df['t1_player2_kdr'] +
                    df['t1_player3_kdr'] + df['t1_player4_kdr'] + df['t1_player5_kdr']) / 5
df['t2_avg_kdr'] = (df['t2_player1_kdr'] + df['t2_player2_kdr'] +
                    df['t2_player3_kdr'] + df['t2_player4_kdr'] + df['t2_player5_kdr']) / 5

"""
df['t1_avg_dmr'] = (df['t1_player1_dmr'] + df['t1_player2_dmr'] +
                    df['t1_player3_dmr'] + df['t1_player4_dmr'] + df['t1_player5_dmr']) / 5
df['t2_avg_dmr'] = (df['t2_player1_dmr'] + df['t2_player2_dmr'] +
                    df['t2_player3_dmr'] + df['t2_player4_dmr'] + df['t2_player5_dmr']) / 5
"""


# remove teams from the dataset that have less than 200 matches

value_counts_1 = df['team_1'].value_counts()
value_counts_2 = df['team_2'].value_counts()

# get a list of values that meet the occurrence count threshold
keep_values_1 = value_counts_1[value_counts_1 >= 100].index.tolist()
keep_values_2 = value_counts_2[value_counts_2 >= 100].index.tolist()
# filter the dataframe to only include rows where the fruit value is in the keep_values list
df = df[df['team_1'].isin(keep_values_1)]
df = df[df['team_2'].isin(keep_values_2)]

#filter out draws (not idal but draws are so rare it doesnt really matter)
df = df[df['winner'] != 'draw']




# prepare plot
plt.figure(figsize=[20, 5], dpi=400)
x = []
y = []

# prepare TS1 env
env = TrueSkill(draw_probability=0)
env.make_as_global()


def win_probability(team1, team2):
    
    delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
    sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
    size = len(team1) + len(team2)
    denom = math.sqrt(size * (env.beta * env.beta) + sum_sigma)

    return env.cdf(delta_mu / denom)

is_bestof = []
kdr_diff = []
# assign initial ratings 
#very inefficient but i dont want to fix it
for index, row in df.iterrows():
    x.append(index)
    if row['team_1'] not in ratings:
        r = ratings[row['team_1']] = Rating()

    if row['team_2'] not in ratings:
        r = ratings[row['team_2']] = Rating()

    if row['t1_points'] + row['t2_points'] < 16 :
        is_bestof.append(True)
    else:
        is_bestof.append(False)
    
    kdr_diff.append(row['t1_avg_kdr'] - row['t2_avg_kdr'])
df['is_bestof'] = is_bestof
df['kdr_diff'] = kdr_diff

df['predicted_winner'] = 0
df['t1_win_probability'] = 0
predictions = []
probabilities = []
for index, row in df.iterrows():

    p = win_probability([ratings[row['team_1']]], [ratings[row['team_2']]]) #put it into team format as well
    predictions.append('t1') if p > 0.5 else predictions.append('t2')
    probabilities.append(p)

    if (row['winner'] == 't1'):

        t1_new_rating, t2_new_rating = rate_1vs1(
            ratings[row['team_1']], ratings[row['team_2']])

        ratings[row['team_1']] = t1_new_rating
        ratings[row['team_2']] = t2_new_rating

    elif (row['winner'] == 't2'):

        t2_new_rating, t1_new_rating = rate_1vs1(
            ratings[row['team_2']], ratings[row['team_1']])

        ratings[row['team_1']] = t1_new_rating
        ratings[row['team_2']] = t2_new_rating

    mu_list = []

    for key, value in ratings.items():
        mu_list.append(value.mu)

    y.append(mu_list)

df['predicted_winner'] = predictions
df['t1_win_probability'] = probabilities
label_list = []
for key, value in ratings.items():
    label_list.append(key)

plt.plot(x, y, label=label_list)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.savefig('image')

num_matches = sum(df['winner'] == df['predicted_winner'])
total_rows = len(df)
percent_matches = num_matches / total_rows * 100

print(
    f'Trueskill correctly predicts the outcome {percent_matches}% of the time.')


df = df.tail(-1000)

num_matches = sum(df['winner'] == df['predicted_winner'])
total_rows = len(df)
percent_matches = num_matches / total_rows * 100
# initial value: 58,546%
print(
    f'After removing the first 1000 rows and ratings converge, Trueskill correctly predicts the outcome {percent_matches}% of the time.')

"""
Trueskill correctly predicts the outcome 56.91788526434196% of the time.
After removing the first 1000 rows and ratings converge, Trueskill correctly predicts the outcome 58.74035989717223% of the time.
"""
import tensorflow as tf
import pandas as pd
from sklearn.model_selection import train_test_split


#drop unnecessary columns
df = df[['winner', 't1_points', 't2_points', 't1_win_probability', 'is_bestof', 'kdr_diff']]

# Convert column to a one-hot encoded format
df= pd.get_dummies(df, columns=['winner', 'is_bestof'], dtype=np.float64)

print(df.sample(10))
# Split the data into input and output columns


X = df.drop(['kdr_diff'], axis=1).values
y = df[['kdr_diff']].values

# Split the data into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Create a multilayer perceptron model with ReLU activation
model = tf.keras.models.Sequential([
    tf.keras.layers.Dense(32, activation='relu', input_shape=(7,)),
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

df_test = pd.concat([pd.DataFrame(model.predict(X_test), columns=['Predicted']),
                     pd.DataFrame(y_test, columns=['Real']),
                     pd.DataFrame(X_test, columns=['t1_points', 't2_points', 't1_pred_win','a','b','c','d'])],
                     axis=1)

print(df_test.sample(20))


"""
problems with this:
-not accurate as much as i want
-bo3-s maybe should be removed, instead of including it in the model. or smth
-no validation set
-

"""

