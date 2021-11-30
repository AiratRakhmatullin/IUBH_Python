"""
This module contains unittests for the class FunctionMatching from module ideal_func_match
"""
# Step 1 ------------- IMPORT ALL LIBRARIES -------------
import unittest
import pandas as pd
import numpy as np
from ideal_func_match import FunctionMatching
from pandas._testing import assert_frame_equal

# create dataframes examples with a few rows using functions y1 = x, y2 = x^2, y3 = x^3
x = np.array(list(range(-5, 6, 1)))
y1 = x
y2 = np.array([i ** 2 for i in x])
y3 = np.array([i ** 3 for i in x])
y4 = np.array([2*(i ** 3) for i in x])
np.random.seed(1)
# crete test data and add some normal distributed noise
df_test = pd.DataFrame(
    {'x': x,
     'y1(training func)': y1 + np.random.normal(0, .1, y1.shape),
     'y2(training func)': y2 + np.random.normal(0, .1, y2.shape),
     'y3(training func)': y3 + np.random.normal(0, .1, y3.shape)
     })
# crete ideal data without noise
df_ideal = pd.DataFrame(
    {'x': x,
     'y1(ideal func)': y1,
     'y2(ideal func)': y2,
     'y3(ideal func)': y3,
     'y4(ideal func)': y4
     })
# expected result dataframe
df_expected_res = pd.DataFrame(
    {'x': x,
     'y1(ideal func)': y1,
     'y2(ideal func)': y2,
     'y3(ideal func)': y3,
     'max_dev1': 0.325486908234417,
     'max_dev2': 0.29134779283873,
     'max_dev3': 0.132337862526187
     })


# Step 2 ------------- create class with unittests -------------
class TestFunctionMatching(unittest.TestCase):
    """
    This class contains unittests to check how FunctionMatching class works
    """

    def setUp(self):
        self.function_matching = FunctionMatching(df_test=df_test, df_ideal=df_ideal, col_name_key='x')

    # test method starts with the keyword test_
    def test_match(self):
        assert_frame_equal(self.function_matching.match().round(3), df_expected_res.round(3), check_dtype=False)


# Executing the tests in the above test case class
if __name__ == "__main__":
    unittest.main()
