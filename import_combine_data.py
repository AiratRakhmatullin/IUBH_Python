# 1. library imports
import pathlib as pth
import pandas as pd
import csv


# 2. создаем класс для чтения данных из csv источника
class DataFromFile:
    def __init__(self, files, directory=pth.Path.cwd()):
        """
        :param directory: directory for the csv files, default value is current dir
        :param files: list with the names of all files for importing
        """
        self.files = files
        self.directory = directory
        # check does the file really exist. как лучше проверить? через assert?
        flag_exist = [pth.Path(directory, k).exists() for k in self.files]
        if sum(flag_exist) == len(self.files):
            print('OK, files exist')
        else:
            print('error')
        # добавить проверку, что файлы формата CSV и содержат только 2 колонки 'X' и 'Y'

    def import_files_to_pandas_df(self, add_prefix_for_column_name='', col_name_key='x'):
        """
        :param col_name_key: name of the key column, use as an index column for dataframe
        :param add_prefix_for_column_name: additional test to add in the end of col_name
        """
        # нужно убедиться что все файлы можно склеить в один датафрейм, т.е имеется совпадающее поле для join
        # и размеры файлов сопадают
        # потом можно переопределить этот метод для чтения построчно
        df_result = pd.DataFrame()  # пустой датафрейм
        flag = True
        for k in self.files:
            p = pth.Path(self.directory, k)
            if flag:
                df_result = pd.read_csv(p, sep=',').copy()
                flag = False
            else:
                df_result = df_result.merge(pd.read_csv(p, sep=','), how='left', left_on=col_name_key,
                                            right_on=col_name_key)

        # rename columns_name
        columns = [col for col in df_result.columns if col != col_name_key]
        new_columns = [col + add_prefix_for_column_name for col in df_result.columns if col != col_name_key]
        dict_to_rename_columns = dict(zip(columns, new_columns))
        df_result.rename(columns=dict_to_rename_columns, inplace=True)

        return df_result


# 2. создаем класс для чтения данных из csv источника построчно
class DataFromFileByLine(DataFromFile):
    def __init__(self, files, directory=pth.Path.cwd()):
        super().__init__(files, directory)

    # переопределяем метод import_files_to_pandas_df для возвращения данных построчно
    def import_files_to_pandas_df(self, file_number=0):
        # file_number - это номер файла для вывода построчно в списке файлов files
        # проверить, что номер файла не выходит за рамки общего кол-ва файлов в self.files
        p = pth.Path(self.directory, self.files[file_number])
        with open(p, newline='') as file:
            csv_file_reader = csv.reader(file, delimiter=',')
            next(csv_file_reader, None)  # skip the headers
            for row in csv_file_reader:
                yield row
