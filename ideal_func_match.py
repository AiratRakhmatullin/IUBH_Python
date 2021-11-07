# 1. library imports
import pathlib as pth

import numpy as np
import pandas as pd
import re


# 2. создаем класс для поиска оптимальных функций
class FunctionMatching:
    def __init__(self, df_test, df_ideal, col_name_key='x'):
        """
        :param df_test: dataframe contain all test values
        :param df_ideal: dataframe contain all ideal functions
        :param col_name_key: name of the key column for matching two dataframes, by default is 'X'
        """
        # првоерка на то, что входные данные это датафреймы
        # проверка на то, что кол-во строк совпадает в 2ух датафреймах
        # првоерка на то, что в обоих датафреймах есть столбец col_name_key и что они полностью совпадают
        # проверка на то, что все значения в датафреймах заполнены и являются числами.
        self.df_test = df_test
        self.df_ideal = df_ideal
        self.col_name_key = col_name_key

    def match(self):
        # create list of Y columns in test dataframe
        col_test = [col for col in self.df_test.columns if col != self.col_name_key]
        # create list of Y columns in ideal dataframe
        col_ideal = [col for col in self.df_ideal.columns if col != self.col_name_key]
        # добавить поверку, что col_test и col_ideal названия соответсвуют шаблону
        # создаем резултирующий датафрейм. изначально в нем только колонка "X"
        df_res = pd.DataFrame(self.df_test[self.col_name_key].copy())
        for col_t in col_test:

            res = self.df_test[[self.col_name_key, col_t]].merge(self.df_ideal[[self.col_name_key, col_ideal[0]]],
                                                                 how='left',
                                                                 left_on=self.col_name_key,
                                                                 right_on=self.col_name_key)
            # фиксируем исходное значение мин отклонения
            min_deviation = sum((res[col_t] - res[col_ideal[0]]) * (res[col_t] - res[col_ideal[0]]))
            # фиксируем исходное значение колонки для подходящей идеальной функции
            min_ideal_func = col_ideal[0]
            for col_i in col_ideal:

                res = self.df_test[[self.col_name_key, col_t]].merge(self.df_ideal[[self.col_name_key, col_i]],
                                                                     how='left',
                                                                     left_on=self.col_name_key,
                                                                     right_on=self.col_name_key)
                if sum((res[col_t] - res[col_i]) * (res[col_t] - res[col_i])) < min_deviation:
                    min_deviation = sum((res[col_t] - res[col_i]) * (res[col_t] - res[col_i]))
                    min_ideal_func = col_i
            # Создаем датафрейм где будет текущая колонка Y_test и найденная Y_ideal
            df_prelim = self.df_test[[self.col_name_key, col_t]].merge(
                self.df_ideal[[self.col_name_key, min_ideal_func]],
                how='left',
                left_on=self.col_name_key,
                right_on=self.col_name_key)
            # переименовать колонки в df_prelim чтобы легко было понять где для какого Y найдена идеальная функция
            # для каждой колонки Y_test добавляем данные в финальный датафрейм
            df_res = df_res.merge(df_prelim, how='left', left_on=self.col_name_key, right_on=self.col_name_key)
            # print(min_deviation)
        # сразу добавляем колонки с максимально допустимой девиацией для проверки потом test функций
        col_ideal = [col for col in df_res.columns if col != self.col_name_key]
        count = 1
        for i in range(0, len(col_ideal), 2):
            max_dev = 2 ** 0.5 * (df_res[col_ideal[i]] - df_res[col_ideal[i + 1]]) * \
                      (df_res[col_ideal[i]] - df_res[col_ideal[i + 1]])
            col_name = 'max_dev' + str(count)
            count += 1
            df_res[col_name] = max_dev.max()
        col_for_res = [col for col in df_res.columns if col not in col_test]
        return df_res[col_for_res]


# 3. создаем класс для подбора оптимальной функции из списка найденных идеальных для тестовых данных
# класс наследуется от FunctionMatching, где на входе два датафрейма. один состоит из одной строки (тестовые данные),
# второй содержит в себе информация об идельных функциях и обучающих данных для поиска максимального отклонения


class TestMatching(FunctionMatching):
    def __init__(self, df_test, df_ideal, col_name_key='x'):
        super().__init__(df_test, df_ideal, col_name_key)

    def match(self):
        # добавить проверку, что колонки идут вначале train потом ideal по очереди и они идут в парах
        #col_ideal = [col for col in self.df_ideal.columns if col != self.col_name_key]
        #count = 1
        #for i in range(0, len(col_ideal), 2):
            #print(i)
            #print(self.df_ideal[col_ideal[i]])
            #max_dev = 2 ** 0.5 * (self.df_ideal[col_ideal[i]] - self.df_ideal[col_ideal[i + 1]]) * \
            #          (self.df_ideal[col_ideal[i]] - self.df_ideal[col_ideal[i + 1]])

            #col_name = 'max_dev' + str(count)
            #count += 1
            #self.df_ideal[col_name] = max_dev.max()
        # оставить только столбцы с ideal func и self.col_name_key для последующего merge

        # добавить проверку, что df_test состоит из одной строки и двух колонок

        # ищем подходящий x для test данных из перечня идеальных
        res = self.df_test.merge(self.df_ideal, how='left', left_on=self.col_name_key, right_on=self.col_name_key)
        # делаем проверку, что res не пустой и состоит из одной строки. Если не пустой, то делаем поиск подходящей идеальной функции
        col_res = res.columns
        # print(col_res)
        # print(col_res[1])
        # print(res[col_res[1]])
        number_ideal_functions = int((len(res.columns) - 2)/2)
        delta = np.inf
        ideal_func = None
        for i in range(2, number_ideal_functions+2, 1):
            if list((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]]))[0] < delta and \
                    list((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]]))[0] <= list(res[col_res[i + number_ideal_functions]])[0]:
                delta = list((res[col_res[1]] - res[col_res[i]]) * (res[col_res[1]] - res[col_res[i]]))[0]
                ideal_func = int(re.search(r'\d+', col_res[i]).group(0))
        res = res[col_res[0:2]]
        res['Delta Y (test func)'] = delta
        res['No of ideal func'] = ideal_func
        res.rename({self.col_name_key: 'X (test func)'}, axis=1, inplace=True)
        return res
