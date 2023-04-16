import trueskill
import tensorflow as tf
import math
import itertools

#no ranks, no draws
class Trueskill_plus():
    def __init__():
        env = trueskill.TrueSkill()
        env.make_as_global()

    def win_probability(self, team1, team2):
    
        delta_mu = sum(r.mu for r in team1) - sum(r.mu for r in team2)
        sum_sigma = sum(r.sigma ** 2 for r in itertools.chain(team1, team2))
        size = len(team1) + len(team2)
        denom = math.sqrt(size * (self.env.beta * self.env.beta) + sum_sigma)

        return self.env.cdf(delta_mu / denom)

    def rate(rating_groups, points = None, stats = None, model: tf.keras.Model = None):
        #put code here

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
        trueskill.rate(rating_groups, ranks=None, weights=None, min_delta=0.0001)
    
    def rate_1vs1(rating1, rating2, points = None, stats = None, model: tf.keras.Model = None):
        #ratings would get switched around if one team had more points.
        #model should have columns!
        #t1 is the winner always here.
        
        if points:
            t1_points = points[0]
            t2_points = points[1]
        if stats:
            t1_stats = stats[0]
            t2_stats = stats[1]
        
        if t1_points > t2_points:
            winner = 't1'
        else:
            winner = 't2'

        

        stat_diff = t1_stats - t2_stats
        pred_stat_diff = model.predict([winner, t1_points, t2_points, ])
        



        trueskill.rate_1vs1(rating1, rating2)