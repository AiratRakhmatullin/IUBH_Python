"""
This module contains classes to match functions
"""
# Step 1 ------------- IMPORT ALL LIBRARIES -------------
import numpy as np
import pandas as pd
import re
import sys
from UserDefinedExceptions import NotAppropriateColumnError, NotAppropriateDataFormatError, \
    NotAppropriateVariableFormatError, EmptyDataError


# Step 2 ------------- Create the class to choose optimal ideal functions which feet train functions  -------------
class FunctionMatching:
    """
    This class for choosing optimal ideal functions which feet train functions
    """

    def __init__(self, df_test, df_ideal, col_name_key='x'):
        """
        function to initialize an object and check and set parameters
        :param df_test: dataframe contain all test values
        :param df_ideal: dataframe contain all ideal functions
        :param col_name_key: name of the key column for matching two dataframes, by default is 'X'
        """
        # check that the input data are dataframes
        if not isinstance(df_test, pd.DataFrame):
            raise NotAppropriateVariableFormatError(var=df_test)
        if not isinstance(df_ideal, pd.DataFrame):
            raise NotAppropriateVariableFormatError(var=df_ideal)
        # check that both dataframes have a "col_name_key" column
        if (col_name_key not in df_test.columns) or (col_name_key not in df_ideal.columns):
            raise NotAppropriateColumnError(col_name=col_name_key, dataframes=[df_test, df_ideal])
        # check that all values in dataframes are numbers
        if sum(df_test.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())) != df_test.shape[1]:
            raise NotAppropriateDataFormatError(dataframe=df_test)
        if sum(df_ideal.apply(lambda s: pd.to_numeric(s, errors='coerce').notnull().all())) != df_ideal.shape[1]:
            raise NotAppropriateDataFormatError(dataframe=df_ideal)
        # if no exceptions were raised then set parameters
        try:
            self.df_test = df_test
            self.df_ideal = df_ideal
            self.col_name_key = col_name_key
        except NotAppropriateVariableFormatError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except NotAppropriateColumnError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except NotAppropriateDataFormatError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except Exception:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            print("Error. Please check that your variables for matching are 1) both pandas dataframes, \
                                                      2) data consists only from digits")
            print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                          '[Error Type]: ' + str(exception_type)))
            sys.exit(1)

    def match(self):
        """
        find best ideal functions for each test function
        return dataframe with best ideal functions and maximum allowed deviation
        """
        try:
            # create list of Y columns in test dataframe
            col_test = [col for col in self.df_test.columns if col != self.col_name_key]
            # create list of Y columns in ideal dataframe
            col_ideal = [col for col in self.df_ideal.columns if col != self.col_name_key]
            # create the resulting dataframe. initially it contains only column "X"
            df_res = pd.DataFrame(self.df_test[self.col_name_key].copy())
            for col_t in col_test:
                res = self.df_test[[self.col_name_key, col_t]].merge(self.df_ideal[[self.col_name_key, col_ideal[0]]],
                                                                     how='left',
                                                                     left_on=self.col_name_key,
                                                                     right_on=self.col_name_key)
                # fix the initial value of the min deviation
                min_deviation = sum((res[col_t] - res[col_ideal[0]]) * (res[col_t] - res[col_ideal[0]]))
                # fix the initial value of the column for a suitable ideal function
                min_ideal_func = col_ideal[0]
                for col_i in col_ideal:
                    res = self.df_test[[self.col_name_key, col_t]].merge(self.df_ideal[[self.col_name_key, col_i]],
                                                                         how='left',
                                                                         left_on=self.col_name_key,
                                                                         right_on=self.col_name_key)
                    if sum((res[col_t] - res[col_i]) * (res[col_t] - res[col_i])) < min_deviation:
                        min_deviation = sum((res[col_t] - res[col_i]) * (res[col_t] - res[col_i]))
                        min_ideal_func = col_i
                # Create a dataframe where the current column Y_test and the found Y_ideal will be
                df_prelim = self.df_test[[self.col_name_key, col_t]].merge(
                    self.df_ideal[[self.col_name_key, min_ideal_func]],
                    how='left',
                    left_on=self.col_name_key,
                    right_on=self.col_name_key)
                # for each column Y_test, add data to the final dataframe
                df_res = df_res.merge(df_prelim, how='left', left_on=self.col_name_key, right_on=self.col_name_key)
            # add columns with the maximum allowed deviation to check later with test functions
            col_ideal = [col for col in df_res.columns if col != self.col_name_key]
            count = 1
            for i in range(0, len(col_ideal), 2):
                max_dev = pow((2 * (df_res[col_ideal[i]] - df_res[col_ideal[i + 1]]) * (
                            df_res[col_ideal[i]] - df_res[col_ideal[i + 1]])), 0.5)
                col_name = 'max_dev' + str(count)
                count += 1
                df_res[col_name] = max_dev.max()
            col_for_res = [col for col in df_res.columns if col not in col_test]
            # check that DF is not empty
            if len(df_res[col_for_res]) == 0:
                raise EmptyDataError(file_source='the result of matching')
            return df_res[col_for_res]
        except EmptyDataError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except Exception:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            print("Error. Please check that your variables for matching are 1) both pandas dataframes, \
                                                          2) data consists only from digits")
            print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                          '[Error Type]: ' + str(exception_type)))
            sys.exit(1)

# Step 2 ------------- Create a class for selecting the optimal function from the list of found ideal for test data


class TestMatching(FunctionMatching):
    """
    This class for choosing optimal ideal functions which feet test functions.
    Class inherits from FunctionMatching, where two dataframes are input. one consists of one line (test data),
    the second contains information about possible ideal functions and the maximum allowed deviation
    """

    def __init__(self, df_test, df_ideal, col_name_key='x'):
        """
        function to initialize an object and check and set parameters
        :param df_test: dataframe contain all test values
        :param df_ideal: dataframe contain all ideal functions
        :param col_name_key: name of the key column for matching two dataframes, by default is 'X'
        """
        super().__init__(df_test, df_ideal, col_name_key)

    def match(self):
        """
        find best ideal functions for each test function
        return dataframe with best ideal functions and maximum allowed deviation
        """
        try:
            # looking for a suitable x for test data from the list of ideal data
            res = self.df_test.merge(self.df_ideal, how='left', left_on=self.col_name_key, right_on=self.col_name_key)
            col_res = res.columns
            number_ideal_functions = int((len(res.columns) - 2) / 2)
            delta = np.inf
            ideal_func = None
            for i in range(2, number_ideal_functions + 2, 1):
                if list(pow(((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]])), 0.5))[
                    0] < delta and \
                        list(pow(((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]])), 0.5))[0] <= \
                        list(res[col_res[i + number_ideal_functions]])[0]:
                    delta = list(pow(((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]])), 0.5))[0]
                    ideal_func = int(re.search(r'\d+', col_res[i]).group(0))
            res = res[col_res[0:2]]
            res['Delta Y (test func)'] = delta
            res['No of ideal func'] = ideal_func
            res.rename({self.col_name_key: 'X (test func)'}, axis=1, inplace=True)
            return res
        except Exception:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            print("Error. Please check that your variables for matching are 1) both pandas dataframes, \
                                                          2) data consists only from digits")
            print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                          '[Error Type]: ' + str(exception_type)))
            sys.exit(1)
