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
        self.assertEqual(env.stat_coeff, 1)

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
    """@unittest.skip("Skipping this test")
    def test_skip(self):
        # Skip this test
        self.fail("This test should be skipped")

    @unittest.expectedFailure
    def test_expected_failure(self):
        # Expected failure
        self.assertEqual(2 + 2, 5)

    @unittest.skipIf(2 + 2 == 5, "Skipping this test if 2 + 2 equals 5")
    def test_skip_if(self):
        # Skip this test if a condition is met
        self.fail("This test should be skipped if 2 + 2 equals 5")

    @unittest.skipUnless(2 + 2 == 5, "Skipping this test unless 2 + 2 equals 5")
    def test_skip_unless(self):
        # Skip this test unless a condition is met
        self.fail("This test should be skipped unless 2 + 2 equals 5")"""



# Run the tests when the script is executed directly
if __name__ == '__main__':
    test_suite = unittest.TestLoader().loadTestsFromTestCase(Trueskill_plus_test)

    # Create a test runner and run the suite
    runner = unittest.TextTestRunner()
    runner.run(test_suite)



"""env = trueskillplus.Trueskillplus(stat_coeff=0.1, experience_coeffs={0:0.01, 1:0})

ts1_1 = trueskill.trueskill.Rating()
ts1_2 = trueskill.trueskill.Rating()
ts1_3 = trueskill.trueskill.Rating()
ts1_4 = trueskill.trueskill.Rating()





ts2_1 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_2 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_3 = trueskillplus.Rating_plus(25,25/3, 1)
ts2_4 = trueskillplus.Rating_plus(25,25/3, 1)

p1 = trueskillplus.Rating_plus(25,25/3, 0)
p2 = trueskillplus.Rating_plus(28,25/3, 1)
p3 = trueskillplus.Rating_plus(23,25/3, 0)
p4 = trueskillplus.Rating_plus(25,25/3, 2)

print('TS1 ratings: ',trueskill.rate(rating_groups=[(ts1_1,ts1_2),(ts1_3,ts1_4)]))

print('TS2 ratings: ', env.rate(rating_groups=[(ts2_1,ts2_2),(ts2_3,ts2_4)], ranks=[1,2],stats=[(4,2),(3,1)], expected_stats=[(3,3),(2,2)], squads=[0,0]))

#creating the environment
env = trueskillplus.Trueskillplus(stat_coeff=0.1, 
                                  squad_coeffs = {1:0, 2:0.05}, 
                                  experience_coeffs={1:0.01, 2:0})

#creating ratings
r_1 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=1)
r_2 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=1)
r_3 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=0)
r_4 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=0)

#making the players play a match, and updating ratings
new_ratings = env.rate(rating_groups=[(r_1,r_2),(r_3,r_4)], 
                       ranks=[1,2])
#display results
print(new_ratings)
print('###########')
#creating the environment
env = trueskillplus.Trueskillplus(stat_coeff=0.1, 
                                  squad_coeffs = {1:0, 2:0.05}, 
                                  experience_coeffs={1:0.01, 2:0})

#creating ratings
r_1 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=1)
r_2 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=1)
r_3 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=0)
r_4 = trueskillplus.Rating_plus(mu=25,sigma=25/3, experience=0)

#making the players play a match, and updating ratings
new_ratings = env.rate(rating_groups=[(r_1,r_2),(r_3,r_4)], 
                       ranks=[1,2],
                       stats=[(4,2),(3,1)], 
                       expected_stats=[(3,3),(2,2)], 
                       squads=[2,0])
#display results
print(new_ratings)"""