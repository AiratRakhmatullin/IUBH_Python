"""
This module contains classes to import data
"""
# Step 1 ------------- IMPORT ALL LIBRARIES -------------
import pathlib as pth
import pandas as pd
import csv
import sys
from UserDefinedExceptions import DoNotHaveColumnError, EmptyDataError, NotAppropriateLengthError


# Step 2 ------------- Create the class to read data from csv files into pandas dataframe  -------------
class DataFromFile:
    """
    This class contains functions to read data from csv files into pandas dataframe
    """

    def __init__(self, files, directory=pth.Path.cwd()):
        """
        function to initialize an object and set parameters
        :param directory: directory for the csv files, default value is current dir. Example - r"data\train"
        :param files: list with the names of all files for importing with extension. Example - ['train.csv']
        """
        self.files = files
        self.directory = directory

    def import_files_to_pandas_df(self, add_prefix_for_column_name='', col_name_key='x'):
        """
        import files to pandas dataframe and rename columns
        :param col_name_key: name of the key column, use as column to join files to one dataframe
        :param add_prefix_for_column_name: additional prefix to add in the end of column name
        return pandas dataframe
        """
        df_result = pd.DataFrame()  # пустой датафрейм
        flag = True
        for k in self.files:
            p = pth.Path(self.directory, k)
            if flag:
                try:
                    df_result = pd.read_csv(p, sep=',').copy()
                    flag = False
                except FileNotFoundError:
                    print(
                        "ERROR!!! File {0} not found! Please check the correctness of directory and files name".format(
                            p))
                    sys.exit(1)
                except Exception:
                    exception_type, exception_value, exception_traceback = sys.exc_info()
                    print("Error. Please check that your file {0} has 1) '.csv' format 2) 'utf-8' codec, \
                          ',' as a separator".format(p))
                    print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                                  '[Error Type]: ' + str(exception_type)))
                    sys.exit(1)
            else:
                try:
                    df_result = df_result.merge(pd.read_csv(p, sep=','), how='left', left_on=col_name_key,
                                                right_on=col_name_key)
                except FileNotFoundError:
                    print(
                        "ERROR!!! File {0} not found! Please check the correctness of directory and files name".format(
                            p))
                    sys.exit(1)
                except Exception:
                    exception_type, exception_value, exception_traceback = sys.exc_info()
                    print("Error. Please check that your file {0} has 1) '.csv' format 2) 'utf-8' codec, \
                                  ',' as a separator".format(p))
                    print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                                  '[Error Type]: ' + str(exception_type)))
                    sys.exit(1)
        # rename columns_name and rise error for two cases:
        # 1) if our dataset don't have 'col_name_key' column
        # 2) if df_result is empty
        try:
            columns = [col for col in df_result.columns if col != col_name_key]
            # rise an error if our dataset don't have col_name_key column
            if col_name_key not in df_result.columns:
                raise DoNotHaveColumnError(column_name=col_name_key, file_source=self.directory)
            new_columns = [col + add_prefix_for_column_name for col in df_result.columns if col != col_name_key]
            dict_to_rename_columns = dict(zip(columns, new_columns))
            df_result.rename(columns=dict_to_rename_columns, inplace=True)
            # rise an error if df_result is empty
            if len(df_result) == 0:
                raise EmptyDataError(file_source=self.directory)
            # проверить состоит ли датафрейм только из цифр
            return df_result
        except DoNotHaveColumnError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except EmptyDataError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except Exception:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            print("Error. Please check that your files in directory {0} have 1) '.csv' format 2) 'utf-8' codec, \
                                              ',' as a separator".format(self.directory))
            print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                          '[Error Type]: ' + str(exception_type)))
            sys.exit(1)


# Step 3 ----- Create the class to read data from csv files by row using inheritance from class DataFromFile ----------
class DataFromFileByLine(DataFromFile):
    """
    This class to read data from csv files by row using inheritance from class DataFromFile
    """

    def __init__(self, files, directory=pth.Path.cwd()):
        super().__init__(files, directory)

    # override the import_files_to_pandas_df method to return data line by line
    def import_files_to_pandas_df(self, file_number=0):
        """
        read files by rows
        :param file_number: the number of file (order) in the list of files in the directory
        return one row (yield row)
        """
        # check that the file number does not exceed the total number of files in self.files
        try:
            p = pth.Path(self.directory, self.files[file_number])
        except IndexError:
            print("ERROR!!! Couldn't find one of the files in {0} or try to read not existing file".format(
                self.directory))
            sys.exit(1)
        try:
            with open(p, newline='') as file:
                csv_file_reader = csv.reader(file, delimiter=',')
                next(csv_file_reader, None)  # skip the headers
                for row in csv_file_reader:
                    # check that in row only 2 values
                    if len(row) != 2:
                        raise NotAppropriateLengthError(obj=p, obj_len=len(row), len_appropriate=2)
                    # check that 2 values are numbers
                    try:
                        _, _ = float(row[0]), float(row[1])
                    except ValueError:
                        print("Error!!! Data from {0} doesn't contain only digits. Please check your source files".format(p))
                        sys.exit(1)
                    yield row
        except FileNotFoundError:
            print(
                "ERROR!!! File {0} not found! Please check the correctness of directory and files name".format(
                    p))
            sys.exit(1)
        except NotAppropriateLengthError:
            print(sys.exc_info()[1])
            sys.exit(1)
        except Exception:
            exception_type, exception_value, exception_traceback = sys.exc_info()
            print("Error. Please check that your files in directory {0} have 1) '.csv' format 2) 'utf-8' codec, \
                                                      ',' as a separator 3) file consist only from digits".format(
                self.directory))
            print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                          '[Error Type]: ' + str(exception_type)))
            sys.exit(1)
