import trueskill
import math
import itertools
import sys
import logging
from trueskill import *
from typing import List, Tuple

sys.path.append('..')

#: Default initial mean of ratings.
MU = 25.
#: Default initial standard deviation of ratings.
SIGMA = MU / 3
#: Default distance that guarantees about 76% chance of winning.
BETA = SIGMA / 2
#: Default dynamic factor.
TAU = SIGMA / 100
#: Default draw probability of the game.
DRAW_PROBABILITY = .10
#: A basis to check reliability of the result.
DELTA = 0.0001


class Rating_plus(trueskill.Rating):
    def __init__(self, mu=None, sigma=None, experience = 0):
        super().__init__(mu, sigma)
        self.experience = experience
    



class Trueskillplus(trueskill.TrueSkill):
    def __init__(self, mu=MU, sigma=SIGMA, beta=BETA, tau=TAU, draw_probability=DRAW_PROBABILITY, experience_coeffs : dict = None, squad_coeffs : dict = None, stat_coeff = 1):
        super().__init__(mu, sigma, beta, tau, draw_probability)
        
        #todo: give env the following
        #stat coeff: difference from the expected * how much should be the new sigma?
        #default 1 -> new sigma is sigma + abs(stat_diff - expected_stat_diff) 
        #todo this also shouldnt be a flat value
        #
        #squad coeff
        #experience coeff (both add to mu)
        self.stat_coeff = stat_coeff
        if experience_coeffs is None:
            self.experience_coeffs = {0:0.005, 1:0.004, 2:0.002,3:0.001, 4:0.0, 5:0.0}
        else:
            self.experience_coeffs = experience_coeffs
        if squad_coeffs is None:
            self.squad_coeffs = {1:0, 2:0.01, 3:0.02, 4:0.03, 5:0.05}  
        else:
            self.squad_coeffs = squad_coeffs
            #TODO validate this.

    


    def win_probability(self, team1, team2): #Szervezd ezt ki egy külön modulba, kapja az env-et paraméterkén
    
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (self.env.beta * self.env.beta) + sum_sigma)

        return self.env.cdf(delta_mu / denom)

    def rate(self, rating_groups : List[Tuple], ranks=None, weights=None, min_delta=0.001, stats : List[Tuple] = None, expected_stats : List[Tuple] = None, squads : List = None):
      
        super().validate_rating_groups(rating_groups)
        #TODO none lekezelés
        if (squads is None):
            squads = [1 for x in rating_groups]

        

        if stats is not None and expected_stats is not None:

            if len(rating_groups) != len(stats) and len(rating_groups) != len(expected_stats):
                
                raise Exception("Unable to validate - rating groups, stats and expected stats have different structures, or invalid data.")
                
            
            if not (all(len(item1) == len(item2) and len(item1) == len(item3) for item1, item2, item3 in zip(rating_groups, stats, expected_stats))):
                raise Exception("Unable to validate - rating groups, stats and expected stats have different structures, or invalid data.")
          
        else:
            stats = []
            expected_stats = []
            

        for i, team in enumerate(rating_groups[:-1]):
            next_team = rating_groups[i+1]
            if (len(team) != len(next_team)):
                raise Exception("N:M type of matches are not supported")
             


        average_ratings = [] #average rating of i-th team
        for team_tuple in rating_groups:
            
            team_avg = 0
            default_stat = []
            default_expected_stat = []
            for r in team_tuple:
                team_avg+=r.mu
                default_stat.append(0)
                default_expected_stat.append(0)
            
            stats.append(tuple(default_stat))
            expected_stats.append(tuple(default_expected_stat))
            average_ratings.append(team_avg / len(team_tuple))

        i = 0
        new_ratings = []
        experiences = []

        
        for team_tuple, stat_tuple, expected_stat_tuple in zip(rating_groups, stats, expected_stats):
            new_team = []
            team_experiences = []
            
            for r, s, es in zip(team_tuple, stat_tuple, expected_stat_tuple):
                
                #caluclate individual statistics
                stat_diff = s-es
                rating_diff = abs(
                    r.mu - 
                    (sum(average_ratings[:i] + average_ratings[i+1:]) / len(average_ratings[:i] + average_ratings[i+1:]))
                )
               
                stat_offset = (stat_diff / (rating_diff + 1)) *  self.stat_coeff
                
                #calculate squad offset
                if squads[i] in self.squad_coeffs:
                    squad_offset = float(self.squad_coeffs[squads[i]])
                
                else:
                    squad_offset = 0

                #calculate experience offset
                if r.experience in self.experience_coeffs:
                    experience_offset = float(self.experience_coeffs[r.experience])

                    
                
                else:
                    experience_offset = 0

     
                
                new_team.append(Rating_plus(r.mu +
                                            r.mu * squad_offset +
                                            r.mu * experience_offset,
                                            r.sigma + stat_offset,
                                            r.experience))
                team_experiences.append(r.experience) 

                
                #r : trueskillplus rating
                #s : stat number
                #es: expected stat

            new_ratings.append(tuple(new_team))
            experiences.append(tuple(team_experiences))
            i+=1

     

        

        return self.to_trueskill_plus(super().rate(new_ratings, ranks, weights, DELTA), experiences)

        
        #N:N team match – [(r1, r2, r3), (r4, r5, r6)] - optimal
        #N:N:N multiple team match – [(r1, r2), (r3, r4), (r5, r6)] - calculates with the average of the opposing teams, not ideal

        #N:M unbalanced match – [(r1,), (r2, r3, r4)] - unsupported.
        #Free-for-all – [(r1,), (r2,), (r3,), (r4,)] # ffa is same as N:N:N

    #TODO: 
    def rate_1vs1(self, rating1 : Rating_plus, rating2 : Rating_plus, stats = None, expected_stats = None):
       
        rating1 = Rating_plus(rating1.mu + rating1.mu * ((1 / rating1.experience + 1) * self.experience_coeff))
        rating2 = Rating_plus(rating2.mu + rating2.mu * ((1 / rating2.experience + 1) * self.experience_coeff))


        if stats is not None and expected_stats is not None:
            
            rating_diff = abs(rating1.mu - rating2.mu)
            stat_diff = abs(stats-expected_stats)
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
    
    def to_trueskill_plus(self, rating_groups : List[Tuple], experiences : List[Tuple] = None):
        ts_plus_ratings = []

        for team, team_exp in zip(rating_groups, experiences):
            ts_plus_team = []
            for r, e in zip(team, team_exp):
                if experiences:
                    ts_plus_team.append(Rating_plus(r.mu,r.sigma, e))
                else:
                    ts_plus_team.append(Rating_plus(r.mu,r.sigma))
            
            ts_plus_ratings.append(tuple(ts_plus_team))
        
        return ts_plus_ratings
    
    def quality(self, rating_groups, weights=None):
        return super().quality(rating_groups, weights)
