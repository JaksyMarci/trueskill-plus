import pandas as pd
import trueskill
from matplotlib import pyplot as plt
import os
import sys
import numpy as np
#https://www.kaggle.com/datasets/chuckephron/leagueoflegends?select=LeagueofLegends.csv

ts2_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..\\..'))
sys.path.insert(0, ts2_dir)
import trueskillplus

#prepare data
df = pd.read_csv('LeagueofLegends.csv')[['League', 'blueTeamTag', 'bResult', 'rResult',
       'redTeamTag', 'golddiff', 'bKills', 'bTowers',
       'bInhibs', 'bDragons', 'bBarons', 'bHeralds', 'rKills',
       'rTowers', 'rInhibs', 'rDragons', 'rBarons', 'rHeralds']]

columns_to_convert = ['bKills', 'bTowers', 'bInhibs', 'bDragons', 'bBarons', 'bHeralds',
                      'rKills', 'rTowers', 'rInhibs', 'rDragons', 'rBarons', 'rHeralds']

for col in columns_to_convert:
    df[col] = df[col].apply(eval).apply(len)

df['golddiff'] = df['golddiff'].apply(eval).apply(lambda x : x.pop())


df = df[df['League'] == 'NALCS'].reset_index(drop=True) #supposedly this is the most efficient filtering method, but im not convinced

value_counts_1 = df['blueTeamTag'].value_counts()
value_counts_2 = df['redTeamTag'].value_counts()
keep_values_1 = value_counts_1[value_counts_1 >= 30].index.tolist()
keep_values_2 = value_counts_2[value_counts_2 >= 30].index.tolist()

df = df[df['blueTeamTag'].isin(keep_values_1)]
df = df[df['redTeamTag'].isin(keep_values_2)]

#prepare ratings
ts_ratings = {}
ts_plus_ratings = {}

for tag in df['blueTeamTag'].unique():
    ts_ratings[tag] = trueskill.Rating()
    ts_plus_ratings[tag] = trueskill.Rating()

ts_env = trueskill.TrueSkill(draw_probability=0)
ts_plus_env = trueskillplus.Trueskillplus(draw_probability=0)

df['predicted_bResult'] = '?'

#prepare graph
x = np.arange(len(df))
y = []
label_list = []
for key, value in ts_ratings.items():
    label_list.append(key)

for index, row in df.iterrows():
    b_win_prob = ts_plus_env.win_probability([ts_ratings[row['blueTeamTag']]], [ts_ratings[row['redTeamTag']]])
    df.at[index, 'predicted_bResult'] = 1 if b_win_prob > 0.5 else 0
    if row['bResult'] == 1:
        #blue win
        b_new_rating, r_new_rating = trueskill.rate_1vs1(ts_ratings[row['blueTeamTag']], ts_ratings[row['redTeamTag']])
        ts_ratings[row['blueTeamTag']] = b_new_rating
        ts_ratings[row['redTeamTag']] = r_new_rating
    else:
        #red win
        r_new_rating, b_new_rating = trueskill.rate_1vs1(ts_ratings[row['redTeamTag']], ts_ratings[row['blueTeamTag']])
        ts_ratings[row['redTeamTag']] = r_new_rating
        ts_ratings[row['blueTeamTag']] = b_new_rating

    mu_list = []
    for key, value in ts_ratings.items():
        mu_list.append(value.mu)
    y.append(mu_list)

plt.figure()
plt.plot(x, y, label=label_list)
plt.savefig('NALCS_trueskill')


num_matches = sum(df['bResult'] == df['predicted_bResult'])
total_rows = len(df)
percent_matches = num_matches / total_rows * 100

print(
    f'Trueskill correctly predicts the outcome {percent_matches}% of the time.')



