"""
This module contains unittests for the class TestMatching from module ideal_func_match
"""
# Step 1 ------------- IMPORT ALL LIBRARIES -------------
import unittest
import pandas as pd
import numpy as np
from ideal_func_match import TestMatching
from pandas._testing import assert_frame_equal

# create dataframes examples with a few rows using functions y1 = x, y2 = x^2, y3 = x^3
x = np.array(list(range(-5, 6, 1)))
y1 = x
y2 = np.array([i ** 2 for i in x])
y3 = np.array([i ** 3 for i in x])
np.random.seed(1)
# crete test data and add some normal distributed noise
df_test = pd.DataFrame(
    {'x': [-3],
     'Y (test func)': [-2.69]
     })
# crete ideal data without noise
df_ideal = pd.DataFrame(
    {'x': x,
     'y1(ideal func)': y1,
     'y2(ideal func)': y2,
     'y3(ideal func)': y3,
     'max_dev1': 0.325486908234417,
     'max_dev2': 0.29134779283873,
     'max_dev3': 0.132337862526187
     })
# expected result dataframe
df_expected_res = pd.DataFrame(
    {'X (test func)': [-3],
     'Y (test func)': [-2.69],
     'Delta Y (test func)': [0.31],
     'No of ideal func': [1]
     })


# Step 2 ------------- create class with unittests -------------
class TestTestMatching(unittest.TestCase):
    """
    This class contains unittests to check how TestMatching class works
    """

    def setUp(self):
        self.test_matching = TestMatching(df_test=df_test, df_ideal=df_ideal, col_name_key='x')

    # test method starts with the keyword test_
    def test_match(self):
        assert_frame_equal(self.test_matching.match().round(3), df_expected_res.round(3), check_dtype=False)


# Executing the tests in the above test case class
if __name__ == "__main__":
    unittest.main()