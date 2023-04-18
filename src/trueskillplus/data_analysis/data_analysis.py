import itertools
import pandas as pd
import math
import sys
import os
from matplotlib import pyplot as plt
import numpy as np



ts2_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..'))
sys.path.insert(0, ts2_dir)

print(sys.path)

import trueskillplus
import trueskill



# pro csgo games from 2016-2020
# source: https://www.kaggle.com/datasets/gabrieltardochi/counter-strike-global-offensive-matches?resource=download


#TODO: convert from t1-t2 to winner-loser format so placement of teams isnt relevant
"""
prepare dataset
"""
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

# prepare TS env
ts_env = trueskill.TrueSkill(draw_probability=0)
ts_plus_env = trueskillplus.Trueskillplus(draw_probability=0)

ts_ratings = {}
ts_plus_ratings = {}

is_bestof = []
kdr_diff = []
# assign initial ratings 
#very inefficient but i dont want to fix it
for index, row in df.iterrows():
    x.append(index)
    if row['team_1'] not in ts_ratings:
        ts_ratings[row['team_1']] = trueskill.Rating()
        ts_plus_ratings[row['team_1']] = trueskill.Rating()

    if row['team_2'] not in ts_ratings:
        ts_ratings[row['team_2']] = trueskill.Rating()
        ts_plus_ratings[row['team_2']] = trueskill.Rating()

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

"""
Calculate original trueskil ratings
"""

for index, row in df.iterrows():

    p = ts_plus_env.win_probability(team1=[ts_ratings[row['team_1']]], team2=[ts_ratings[row['team_2']]]) #TODO danger, environments could be different. 
    predictions.append('t1') if p > 0.5 else predictions.append('t2')
    probabilities.append(p)

    if (row['winner'] == 't1'):

        t1_new_rating, t2_new_rating = ts_env.rate_1vs1(
            ts_ratings[row['team_1']], ts_ratings[row['team_2']])

        ts_ratings[row['team_1']] = t1_new_rating
        ts_ratings[row['team_2']] = t2_new_rating

    elif (row['winner'] == 't2'):

        t2_new_rating, t1_new_rating = ts_env.rate_1vs1(
            ts_ratings[row['team_2']], ts_ratings[row['team_1']])

        ts_ratings[row['team_1']] = t1_new_rating
        ts_ratings[row['team_2']] = t2_new_rating

    #needed for plot
    mu_list = []

    for key, value in ts_ratings.items():
        mu_list.append(value.mu)

    y.append(mu_list)

df['predicted_winner'] = predictions
df['t1_win_probability'] = probabilities
#needed for plot
label_list = []
for key, value in ts_ratings.items():
    label_list.append(key)

plt.plot(x, y, label=label_list)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.savefig('image_ts')

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

plt.close()
"""
Caluclate Trueskill plus ratings:
"""
from trueskillplus.model import model

ts_plus_model = model.train_csgo_model(df)

plt.figure(figsize=[20, 5], dpi=400)
x = []
y = []


#TODO reusing the dataset is questionable

for index, row in df.iterrows():

    p = ts_plus_env.win_probability(team1=[ts_plus_ratings[row['team_1']]], team2=[ts_plus_ratings[row['team_2']]]) #put it into team format as well
    predictions.append('t1') if p > 0.5 else predictions.append('t2')
    probabilities.append(p)

    
    if (row['winner'] == 't1'):
        x = np.array([ row['t1_points'], row['t2_points'], 1.0, 0.0, 1.0 if row['is_bestof'] == False else 0.0, 1.0 if row['is_bestof'] == True else 0.0])
        t1_new_rating, t2_new_rating = ts_plus_env.rate_1vs1(
            rating1=ts_plus_ratings[row['team_1']], rating2=ts_plus_ratings[row['team_2']],
            stats=row['kdr_diff'],
            predicted_stats=ts_plus_model(np.reshape(x, (1,6)))
            )

        ts_plus_ratings[row['team_1']] = t1_new_rating
        ts_plus_ratings[row['team_2']] = t2_new_rating

    elif (row['winner'] == 't2'):
        x= np.array([ row['t1_points'], row['t2_points'], 0.0, 1.0, 1.0 if row['is_bestof'] == False else 0.0, 1.0 if row['is_bestof'] == True else 0.0])
        
        t2_new_rating, t1_new_rating = ts_plus_env.rate_1vs1(
            rating1=ts_plus_ratings[row['team_2']], 
            rating2=ts_plus_ratings[row['team_1']],
            stats=row['kdr_diff'],
            predicted_stats=ts_plus_model(np.reshape(x, (1,6)))
            )

        ts_plus_ratings[row['team_1']] = t1_new_rating
        ts_plus_ratings[row['team_2']] = t2_new_rating

    mu_list = []

    for key, value in ts_ratings.items():
        mu_list.append(value.mu)

    y.append(mu_list)

df['predicted_winner'] = predictions
df['t1_win_probability'] = probabilities

label_list = []
for key, value in ts_plus_ratings.items():
    label_list.append(key)

plt.plot(x, y, label=label_list)
plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))

plt.savefig('image_ts_plus')

num_matches = sum(df['winner'] == df['predicted_winner'])
total_rows = len(df)
percent_matches = num_matches / total_rows * 100

print(
    f'Trueskill plus correctly predicts the outcome {percent_matches}% of the time.')


df = df.tail(-1000)

num_matches = sum(df['winner'] == df['predicted_winner'])
total_rows = len(df)
percent_matches = num_matches / total_rows * 100
# initial value: 58,546%
print(
    f'After removing the first 1000 rows and ratings converge, Trueskill plus correctly predicts the outcome {percent_matches}% of the time.')


"""
Trueskill correctly predicts the outcome 56.91788526434196% of the time.
After removing the first 1000 rows and ratings converge, Trueskill correctly predicts the outcome 58.74035989717223% of the time.
"""
