import sys
sys.path.append("..")
import trueskillplus
import trueskill


env = trueskillplus.Trueskillplus(stat_coeff=0.5, experience_coeffs={0:0.01, 1:0})

ts1_1 = trueskill.Rating()
ts1_2 = trueskill.Rating()

ts2_1 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_2 = trueskillplus.Rating_plus(25,25/3, 1)

p1 = trueskillplus.Rating_plus(25,25/3, 0)
p2 = trueskillplus.Rating_plus(28,25/3, 1)
p3 = trueskillplus.Rating_plus(23,25/3, 0)
p4 = trueskillplus.Rating_plus(25,25/3, 2)

print('TS1 ratings: ',trueskill.rate(rating_groups=[(ts1_1,),(ts1_2,)]))

print('TS2 ratings: ', env.rate(rating_groups=[(ts2_1,),(ts2_2,)], ranks=[1,2],stats=[(2,),(2,)], expected_stats=[(2,),(2,)], squads=[0,0]))