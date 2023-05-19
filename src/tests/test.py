import sys
sys.path.append("..")
import trueskillplus
import trueskill
from trueskillplus import Trueskillplus, Rating_plus
import unittest


class Trueskill_plus_test(unittest.TestCase):
 

    def setUp(self):
        self.default_env = trueskillplus.Trueskillplus()
        
    def tearDown(self):
        pass

    def test_rating_with_default_values(self):

        rating_plus = trueskillplus.Rating_plus()
        self.assertIsInstance(rating_plus, trueskillplus.Rating_plus)
        self.assertIsInstance(rating_plus, trueskill.Rating)
        self.assertEqual(rating_plus.mu, self.default_env.mu)
        self.assertEqual(rating_plus.sigma, self.default_env.sigma)
        self.assertEqual(rating_plus.experience, 0)

    def test_rating_with_custom_values(self):
        
        rating_plus = trueskillplus.Rating_plus(mu=100, sigma=33, experience=1)
        self.assertIsInstance(rating_plus, trueskillplus.Rating_plus)
        self.assertIsInstance(rating_plus, trueskill.Rating)
        self.assertEqual(rating_plus.mu, 100)
        self.assertEqual(rating_plus.sigma, 33)
        self.assertEqual(rating_plus.experience, 1)

        env=trueskill.TrueSkill(mu=100, sigma=33)
        self.assertEqual(rating_plus.mu, env.mu)
        self.assertEqual(rating_plus.sigma, env.sigma)

    def test_init_with_default_values(self):
        env = Trueskillplus()
        MU = 25
        SIGMA = 25/3
        BETA = 25/6
        TAU=25/300
        DRAW_PROBABILITY = 0.1
        self.assertIsInstance(env, Trueskillplus)
        self.assertIsInstance(env, trueskill.TrueSkill)
        self.assertEqual(env.mu, MU)
        self.assertAlmostEqual(env.sigma, SIGMA)
        self.assertAlmostEqual(env.beta, BETA)
        self.assertAlmostEqual(env.tau, TAU)
        self.assertAlmostEqual(env.draw_probability, DRAW_PROBABILITY)
        self.assertEqual(env.experience_coeffs, {
            0: 0.005, 1: 0.004, 2: 0.003, 3: 0.002, 4: 0.001, 5: 0.0
        })
        self.assertEqual(env.squad_coeffs, {
            1: 0, 2: 0.01, 3: 0.02, 4: 0.03, 5: 0.05
        })
        self.assertEqual(env.stat_coeff, 0)

    def test_init_with_custom_values(self):
        experience_coeffs = {0: 0.01, 1: 0.008, 2: 0.006, 3: 0.004, 4: 0.002, 5: 0.0}
        squad_coeffs = {1: 0, 2: 0.02, 3: 0.04, 4: 0.06, 5: 0.08}
        trueskill_plus = Trueskillplus(
            mu=30, sigma=10, beta=5, tau=3, draw_probability=0.20,
            experience_coeffs=experience_coeffs, squad_coeffs=squad_coeffs, stat_coeff=0.5
        )
        self.assertIsInstance(trueskill_plus, Trueskillplus)
        self.assertIsInstance(trueskill_plus, trueskill.TrueSkill)
        self.assertEqual(trueskill_plus.mu, 30)
        self.assertEqual(trueskill_plus.sigma, 10)
        self.assertEqual(trueskill_plus.beta, 5)
        self.assertEqual(trueskill_plus.tau, 3)
        self.assertEqual(trueskill_plus.draw_probability, 0.20)
        self.assertEqual(trueskill_plus.experience_coeffs, experience_coeffs)
        self.assertEqual(trueskill_plus.squad_coeffs, squad_coeffs)
        self.assertEqual(trueskill_plus.stat_coeff, 0.5)

    def test_win_probability(self):
        team1 = (Rating_plus(mu=25, sigma=8), Rating_plus(mu=30, sigma=10))
        team2 = (Rating_plus(mu=20, sigma=6), Rating_plus(mu=25, sigma=9))
        
        
        self.assertGreater(self.default_env.win_probability(team1, team2), 0.5)
        self.assertLess(self.default_env.win_probability(team2, team1), 0.5)

    def test_to_trueskill_plus_without_experiences(self):
        rating_groups = [
            (trueskill.Rating(mu=25, sigma=8), trueskill.Rating(mu=30, sigma=10)),
            (trueskill.Rating(mu=20, sigma=6), trueskill.Rating(mu=28, sigma=9))
        ]
        expected_ts_plus_ratings = [
            (Rating_plus(mu=25, sigma=8), Rating_plus(mu=30, sigma=10)),
            (Rating_plus(mu=20, sigma=6), Rating_plus(mu=28, sigma=9))
        ]
        actual_ts_plus_ratings = self.default_env.to_trueskill_plus(rating_groups)
        self.assertEqual(actual_ts_plus_ratings, expected_ts_plus_ratings)

    def test_to_trueskill_plus_with_experiences(self):
        rating_groups = [
            [trueskill.Rating(mu=25, sigma=8), trueskill.Rating(mu=30, sigma=10)],
            [trueskill.Rating(mu=20, sigma=6), trueskill.Rating(mu=28, sigma=9)]
        ]
        experiences = [
            (0, 100),
            (50, 75)
        ]
        expected_ts_plus_ratings = [
            (Rating_plus(mu=25, sigma=8, experience=0), Rating_plus(mu=30, sigma=10, experience=100)),
            (Rating_plus(mu=20, sigma=6, experience=50), Rating_plus(mu=28, sigma=9, experience=75))
        ]
        actual_ts_plus_ratings = self.default_env.to_trueskill_plus(rating_groups, experiences)
        self.assertEqual(actual_ts_plus_ratings, expected_ts_plus_ratings)

    def test_rate(self):
        r1 = Rating_plus()
        r2 = Rating_plus()
        r3 = Rating_plus()
        r4 = Rating_plus()

        (new_r1, new_r2), (new_r3, new_r4) = self.default_env.rate([(r1,r2),(r3,r4)])

        self.assertEqual(new_r1, new_r2)
        self.assertGreater(new_r1, new_r3)

    def test_ranks(self): 
        r1 = Rating_plus()
        r2 = Rating_plus()
        r3 = Rating_plus()
        r4 = Rating_plus()

        (new_r1, new_r2), (new_r3, new_r4) = self.default_env.rate([(r1,r2),(r3,r4)], ranks=[2,1])

        self.assertEqual(new_r1, new_r2)
        self.assertGreater(new_r3, new_r1) 

    def test_stats(self):
        env = Trueskillplus(stat_coeff=0.5)
        r1 = Rating_plus()
        r2 = Rating_plus()
        r3 = Rating_plus()
        r4 = Rating_plus()

        (new_r1, new_r2), (new_r3, new_r4) = env.rate(rating_groups=[(r1,r2),(r3,r4)], stats=[(4,2),(3,1)], expected_stats=[(3,3),(3,3)])

       
        self.assertGreater(new_r1, new_r2)
        self.assertGreater(new_r2, new_r3)
        self.assertGreater(new_r3, new_r4)
    
    def test_squads(self):
        env = Trueskillplus(squad_coeffs={1:0, 2:0.1})
        
        r1 = Rating_plus()
        r2 = Rating_plus()
        r3 = Rating_plus()
        r4 = Rating_plus()

        (new_r1, new_r2), (new_r3, new_r4) = env.rate(rating_groups=[(r1,r2),(r3,r4)], squads=[2,1])
        (def_r1, def_r2), (def_r3, def_r4) = self.default_env.rate(rating_groups=[(r1,r2),(r3,r4)])
       
        self.assertGreater(new_r1, def_r1)
        self.assertGreater(new_r3, def_r3)

    def test_experience(self):
        env = Trueskillplus(experience_coeffs={0:0.01, 1:0})
        
        r1 = Rating_plus(experience=0)
        r2 = Rating_plus(experience=1)
        r3 = Rating_plus(experience=0)
        r4 = Rating_plus(experience=0)

        (new_r1, new_r2), (new_r3, new_r4) = env.rate(rating_groups=[(r1,r2),(r3,r4)])
        (def_r1, def_r2), (def_r3, def_r4) = self.default_env.rate(rating_groups=[(r1,r2),(r3,r4)])
       
        self.assertGreater(new_r1, new_r2)
        self.assertEqual(new_r3, new_r4)
        self.assertGreater(new_r1, def_r1)

   
    def test_exception(self):
        r1 = Rating_plus()
        r2 = Rating_plus()
        r3 = Rating_plus()
        r4 = Rating_plus()
        self.assertRaises(Exception, self.default_env.rate, [(r1,r2,r3),(r4,)])
        self.assertRaises(Exception, self.default_env.rate, [(),()])
        self.assertRaises(Exception, self.default_env.rate, [(r1,),()])
        self.assertRaises(Exception, self.default_env.rate, rating_groups=[(r1,r2),(r3,r4)], ranks=[1,2,3])
        self.assertRaises(Exception, self.default_env.rate, rating_groups=[(r1,r2),(r3,r4)], ranks=[1])
        self.assertRaises(Exception, self.default_env.rate, rating_groups=[(r1,r2),(r3,r4)], stats=[1], expected_stats=[1])
        self.assertRaises(Exception, self.default_env.rate, rating_groups=[(r1,r2),(r3,r4)], stats=[1,2], expected_stats=[1])
        self.assertRaises(Exception, self.default_env.rate, rating_groups=[(r1,r2),(r3,r4)], stats=[(1,2),(2,1)], expected_stats=[1])




# Run the tests when the script is executed directly
if __name__ == '__main__':
    tests = unittest.TestLoader().loadTestsFromTestCase(Trueskill_plus_test)

    # Create a test runner and run the suite
    runner = unittest.TextTestRunner()
    runner.run(tests)

