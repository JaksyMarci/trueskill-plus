import sys
sys.path.append("..")
import trueskillplus

env = trueskillplus.Trueskillplus(stat_coeff=0.001)

p1 = trueskillplus.Rating_plus(25,25/3, 0)
p2 = trueskillplus.Rating_plus(28,25/3, 1)
p3 = trueskillplus.Rating_plus(23,25/3, 0)
p4 = trueskillplus.Rating_plus(25,25/3, 2)
print(p1,p2,p3,p4)
print(env.rate(rating_groups=[(p1,p2),(p3,p4)], stats=[(0,0),(0,0)], expected_stats=[(0,0),(0,0)], squads=[1,3]))

env.rate(rating_groups=[(p1,p2),(p3,p4)], stats=[(0,0),(0,0)], expected_stats=[(0,0),(0,)])