import sys
sys.path.append("..")
import trueskillplus
import trueskill
import random

env = trueskillplus.Trueskillplus(stat_coeff=0.1, experience_coeffs={0:0.01, 1:0})

ts1_1 = trueskill.Rating()
ts1_2 = trueskill.Rating()
ts1_3 = trueskill.Rating()
ts1_4 = trueskill.Rating()





ts2_1 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_2 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_3 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_4 = trueskillplus.Rating_plus(25,25/3, 1)

p1 = trueskillplus.Rating_plus(25,25/3, 0)
p2 = trueskillplus.Rating_plus(28,25/3, 1)
p3 = trueskillplus.Rating_plus(23,25/3, 0)
p4 = trueskillplus.Rating_plus(25,25/3, 2)

print('TS1 ratings: ',trueskill.rate(rating_groups=[(ts1_1,ts1_2),(ts1_3,ts1_4)]))

print('TS2 ratings: ', env.rate(rating_groups=[(ts2_1,ts2_2),(ts2_3,ts2_4)], ranks=[1,2],stats=[(4,3),(2,2)], expected_stats=[(3,3),(2,2)], squads=[0,0]))


new_ratings=[(ts2_1,ts2_2),(ts2_3,ts2_4)]
for i in range(100):
    new_ratings = env.rate(rating_groups=new_ratings, ranks=[random.randint(1,2),random.randint(1,2)],stats=[(4,3),(2,2)], expected_stats=[(3,3),(2,2)], squads=[0,0])
    

print(new_ratings)