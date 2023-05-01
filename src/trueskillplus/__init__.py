import trueskill
import tensorflow as tf
import math
import itertools
import sys

from trueskill import BETA, DELTA, DRAW_PROBABILITY, MU, SIGMA, TAU

sys.path.append('..')

class Rating(trueskill.Rating):
    def __init__(self, mu=None, sigma=None, experience = 0):
        super().__init__(mu, sigma)
        self.experience = experience
    



#no ranks, no draws
class Trueskillplus(trueskill.TrueSkill):
    def __init__(self, mu=..., sigma=..., beta=..., tau=..., draw_probability=..., experience_coeff = 0, squad_coeffs : dict = None, stat_coeff = 1):
        super().__init__(mu, sigma, beta, tau, draw_probability)
        
        #todo: give env the following
        #stat coeff: difference from the expected * how much should be the new sigma?
        #default 1 -> new sigma is sigma + abs(stat_diff - expected_stat_diff) 
        #todo this also shouldnt be a flat value
        #
        #squad coeff
        #experience coeff (both add to mu)
        self.stat_coeff = stat_coeff
        self.experience_coeff = experience_coeff
        self.squad_coeffs = squad_coeffs

    


    def win_probability(self, team1, team2): #Szervezd ezt ki egy külön modulba, kapja az env-et paraméterkén
    
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (self.env.beta * self.env.beta) + sum_sigma)

        return self.env.cdf(delta_mu / denom)

    def rate(self, rating_groups, ranks=None, weights=None, min_delta=...):
        
        super().validate_rating_groups(rating_groups)
        
        super().rate(rating_groups, ranks, weights, min_delta)
        #N:N team match – [(r1, r2, r3), (r4, r5, r6)]
        #N:N:N multiple team match – [(r1, r2), (r3, r4), (r5, r6)]
        #N:M unbalanced match – [(r1,), (r2, r3, r4)]
        #Free-for-all – [(r1,), (r2,), (r3,), (r4,)]

        return 
       
        """
        


        Trueskill 2 variables

        points: score of each team.
        stats: number representing some statistic of a team. cumulated from some statistic. "performance" of team.
        model: a keras model that should predict a score difference between the teams
        is_bestof: if the game is a best of series, it should be true

        #TODO: arguments checks
        winner_points = points[0]
        loser_points = points[1]
        winner_kdr = kdr_stats[0]
        loser_kdr = kdr_stats[1]

        kdr_diff = winner_kdr - loser_kdr#positive means winner had higher kdr 

        
        winner_win_probability = self.win_probability(rating_groups[0], rating_groups[1])
        #df = df[['winner', 't1_points', 't2_points', 't1_win_probability', 'is_bestof', 'kdr_diff']]

        predicted_kdr_diff = model.predict([winner_points, loser_points, winner_win_probability, 1.0, 0.0, 1.0 if is_bestof == False else 0.0, 1.0 if is_bestof == True else 0.0])
        
        #TODO this is gonna be a bad solution, but i dont wanna carry over tau all the time
        # set dynamics factor according to how unlikely this result is.
        diff = abs(kdr_diff - predicted_kdr_diff)


        default_tau = self.tau


        self.tau = self.tau + self.tau * diff #need to modify by some amount.
        
        """
        
    

    
    def rate_1vs1(self, rating1 : Rating, rating2 : Rating, stats = None, predicted_stats = None):
       
        rating1 = Rating(rating1.mu + rating1.mu * ((1 / rating1.experience + 1) * self.experience_coeff))
        rating2 = Rating(rating2.mu + rating2.mu * ((1 / rating2.experience + 1) * self.experience_coeff))


        if stats is not None and predicted_stats is not None:
            
            rating_diff = abs(rating1.mu - rating2.mu)
            stat_diff = abs(stats-predicted_stats)
            #we would need to know the relation between +1 rating <-> +how much stats. should be a 'hyperparamener'
            #TODO ditch this if it doesnt perform well
            #add coeffs for both values maybe?
            stat_offset = (stat_diff / (rating_diff + 1)) *  self.stat_coeff
            
        else:
            stat_offset = 0

            
            
        
        rating1 = trueskill.Rating(rating1.mu, rating1.sigma + stat_offset)
        rating2 = trueskill.Rating(rating2.mu, rating2.sigma + stat_offset) #large diff means an upset happened, so sigma gets modified
        #add experience_offset to ratings here
        return trueskill.rate_1vs1(rating1, rating2)
    

    
