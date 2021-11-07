import import_combine_data as im
import ideal_func_match as mt
import pandas as pd
import mydatabase

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

# загружаем тренировочные данные в один DataFrame
directory = r"E:\IUBH_MS_AI\2_nd_semester\Programming in Python\assignment\data\train"
files = ['train.csv']
d_train = im.DataFromFile(files, directory)
res_train = d_train.import_files_to_pandas_df(add_prefix_for_column_name='(training func)', col_name_key='x')

# загружаем экспериментальные идельные функции в один DataFrame, получаем список всех файлов в папке, так как файлов
# должно быть 50 штук добавить потом првоерку, что файлов должно быть 50 штук для идеальных функций
directory = r"E:\IUBH_MS_AI\2_nd_semester\Programming in Python\assignment\data\ideal"
# paths = sorted(Path(directory).glob('*.csv'))
# paths = [os.path.basename(p) for p in paths]
# files = list(map(str, paths))
files = ['ideal.csv']
d_ideal = im.DataFromFile(files, directory)
res_ideal = d_ideal.import_files_to_pandas_df(add_prefix_for_column_name='(ideal func)', col_name_key='x')

# проводим матчинг идеальных функций
check = mt.FunctionMatching(res_train, res_ideal, col_name_key='x')
res_check = check.match()

res_check.to_excel(r"E:\IUBH_MS_AI\2_nd_semester\Programming in Python\assignment\data\check_res\res.xlsx",
                   sheet_name='res')

# выводим построчно данные из файла csv
directory = r"E:\IUBH_MS_AI\2_nd_semester\Programming in Python\assignment\data\test"
files = ['test.csv']
d_test = im.DataFromFileByLine(files, directory)

# выводим на печать
if __name__ == '__main__':
    # создаю генератор списка строк из csv файла, игнорирую первую строку где название колонок
    obj_my = d_test.import_files_to_pandas_df()
    df_test = pd.DataFrame()
    # Create Tables
    dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mydb.sqlite')
    dbms.create_db_tables()

    # insert train data from pandas dataframe
    dbms.insert_dataframe(df=res_train, table='training_functions')
    # insert ideal data from pandas dataframe
    dbms.insert_dataframe(df=res_ideal, table='ideal_functions')

    # check and insert into database test data
    for k in obj_my:
        # блок с попыткой перевода во float. если не получается, то обрабатываем ошибку и завершаем программу
        k = [float(item) for item in k]
        data = {'x': [k[0]],
                'Y (test func)': [k[1]]}
        # Create DataFrame
        df_test = pd.DataFrame(data)
        test_match = mt.TestMatching(df_test, res_check).match()
        # check if no ideal function were found then pass
        if list(test_match[test_match.columns[-1]].isnull())[0]:
            continue
        else:
            query = "INSERT INTO {0} ('X (test function)', 'Y (test function)', 'Delta Y (test function)', " \
                    "'No of ideal function' ) " \
                    "VALUES ({1}, {2}, {3}, {4});".format('test_functions', list(test_match[test_match.columns[0]])[0],
                                                          list(test_match[test_match.columns[1]])[0],
                                                          list(test_match[test_match.columns[2]])[0],
                                                          list(test_match[test_match.columns[3]])[0])
            dbms.execute_query(query)

    dbms.print_all_data(table='training_functions', query="SELECT * FROM '{}' limit 5;".format('training_functions'))
    dbms.print_all_data(table='ideal_functions', query="SELECT * FROM '{}' limit 5;".format('ideal_functions'))
    dbms.print_all_data(table='test_functions', query="SELECT * FROM '{}' limit 5;".format('test_functions'))

