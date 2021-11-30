#                        Step 1 ------------- IMPORT ALL LIBRARIES -------------
# module to import data from files
import import_combine_data as im
# module to find and match functions
import ideal_func_match as mt
# module to work with sqlite database
import mydatabase
# import standard libs
import sys
import pandas as pd
import re
from bokeh.io import output_file
from bokeh.layouts import gridplot
from bokeh.plotting import figure, show
from bokeh.models import Label, Band, ColumnDataSource

#                        Step 2 ------------- SET OPTIONS to work comfortable in PyCharm -------------
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

#                        Step 3 ------------- SET file directories and file names -------------
directory_for_train_data = r"data\train"
files_for_train_data = ['train.csv']
directory_for_ideal_data = r"data\ideal"
files_for_ideal_data = ['ideal.csv']
directory_for_test_data = r"data\test"
files_for_test_data = ['test.csv']

#                        Step 4 ------------- Import data from files -------------
# import 4 train datasets to one DataFrame
d_train = im.DataFromFile(files_for_train_data, directory_for_train_data)
res_train = d_train.import_files_to_pandas_df(add_prefix_for_column_name='(training func)', col_name_key='x')
# import 50 ideal datasets to one DataFrame
d_ideal = im.DataFromFile(files_for_ideal_data, directory_for_ideal_data)
res_ideal = d_ideal.import_files_to_pandas_df(add_prefix_for_column_name='(ideal func)', col_name_key='x')
# import test function. at this step just create generator
d_test = im.DataFromFileByLine(files_for_test_data, directory_for_test_data)
generator_test = d_test.import_files_to_pandas_df(file_number=0)

#                        Step 5 ------------- Find 4 ideal functions for given train data-------------
check = mt.FunctionMatching(res_train, res_ideal, col_name_key='x')
res_check = check.match()

#                        Step 6 ------------- Insert train and ideal data into database-------------
# Create Tables
dbms = mydatabase.MyDatabase(mydatabase.SQLITE, dbname='mysqldb.sqlite')
dbms.create_db_tables()
# insert train data from pandas dataframe
dbms.insert_dataframe(df=res_train, table='training_functions')
# insert ideal data from pandas dataframe
dbms.insert_dataframe(df=res_ideal, table='ideal_functions')

#                        Step 7 ------------- Find appropriate ideal function for given test data, reading data by rows
#                                               and Insert into database if we can find ideal function-------------
# create pandas DF for further visualisation
test_match_all = pd.DataFrame()
for k in generator_test:
    # check is it possible to transform to float
    try:
        k = [float(item) for item in k]
    except ValueError:
        print("Error!!! Data from {0} doesn't contain only digits. Please check your source files".format(k))
        sys.exit(1)
    data = {'x': [k[0]],
            'Y (test func)': [k[1]]}
    # Create DataFrame
    df_test = pd.DataFrame(data)
    test_match = mt.TestMatching(df_test, res_check).match()
    # write all data to the DF for further visualization
    if len(test_match_all):
        test_match_all = pd.concat([test_match_all, test_match], ignore_index=True)
    else:
        test_match_all = test_match.copy()
    # check if no ideal function were found then pass
    if list(test_match[test_match.columns[-1]].isnull())[0]:
        continue
    # else write one raw to the database
    else:
        query = "INSERT INTO {0} ('X (test function)', 'Y (test function)', 'Delta Y (test function)', " \
                "'No of ideal function' ) " \
                "VALUES ({1}, {2}, {3}, {4});".format('test_functions', list(test_match[test_match.columns[0]])[0],
                                                      list(test_match[test_match.columns[1]])[0],
                                                      list(test_match[test_match.columns[2]])[0],
                                                      list(test_match[test_match.columns[3]])[0])
        dbms.execute_query(query)

#                        Step 8 ------------- Print some data from tables to make sure that we've done correct inserts
#                                               and make figures using Bokeh-------------
# print some data from tables to make sure that we've done correct insets and make figures using Bokeh
if __name__ == '__main__':
    # check that we have correct data in sqlite database - print some data
    dbms.print_all_data(table='training_functions', query="SELECT * FROM '{}' limit 5;".format('training_functions'))
    dbms.print_all_data(table='ideal_functions', query="SELECT * FROM '{}' limit 5;".format('ideal_functions'))
    dbms.print_all_data(table='test_functions', query="SELECT * FROM '{}' limit 5;".format('test_functions'))

    # create figure to show that we have chosen correct ideal functions
    output_file('Train_and_Ideal_functions.html', title='Train and Ideal functions')
    # create 4 plots
    colors = ['red', 'skyblue', 'rosybrown', 'black']
    col_res_check = res_check.columns
    svalues = []
    # create 4 figures on one html page
    try:
        for i in range(1, 5):
            s = figure()
            svalues.append(s)
            for k in range(1, 5):
                # plot ideal functions
                s.line(x=res_check[col_res_check[0]], y=res_check[col_res_check[k]],
                       color=colors[k - 1], line_width=2,
                       legend_label=str(col_res_check[k]))
            # plot train data
            s.circle(x=res_train['x'], y=res_train['y' + str(i) + '(training func)'],
                     color='green', size=4, alpha=0.5,
                     legend_label=str('y' + str(i) + '(training func)'))
            # add decor
            s.legend.location = "bottom"
            s.legend.border_line_width = 2
            s.legend.border_line_color = "navy"
            s.legend.border_line_alpha = 1
            s.legend.label_text_font_size = '8pt'
            s.legend.click_policy = "hide"
            s.title.text = 'Figure to show how good train data fits ideal functions'
            s.add_layout(Label(x=0, y=20000, text='click on the legend to turn on/off'))
        # make a grid
        grid_train_ideal = gridplot(svalues, ncols=2, width=750, height=350)
        show(grid_train_ideal)
    except Exception:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        print("Error. Train and Ideal functions Visualisations are failed")
        print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                      '[Error Type]: ' + str(exception_type)))
        sys.exit(1)

    # create figure to show that we have different ideal functions for test data
    output_file('Test_and_Ideal_functions.html', title='Test and Ideal functions')
    # create 4 plots
    colors = ['red', 'skyblue', 'rosybrown', 'black']
    col_res_check = res_check.columns
    pvalues = []
    try:
        for i in range(1, 5):
            df = res_check[[col_res_check[0], col_res_check[i], col_res_check[i + 4]]].copy()
            # calculate lower and upper bound of possible deviation
            df['lower'] = df[col_res_check[i]] - df[col_res_check[i + 4]]
            df['upper'] = df[col_res_check[i]] + df[col_res_check[i + 4]]
            source = ColumnDataSource(df.reset_index())

            p = figure()
            pvalues.append(p)
            # plot ideal functions
            p.line(x=df[col_res_check[0]], y=df[col_res_check[i]],
                   color=colors[i-1], line_width=1,
                   legend_label=str(col_res_check[i]))
            # plot points from test that are not fit ideal function
            x_notfit = test_match_all[test_match_all['No of ideal func'] != int(re.search(r'\d+', col_res_check[i]).group(0))]['X (test func)']
            y_notfit = test_match_all[test_match_all['No of ideal func'] != int(re.search(r'\d+', col_res_check[i]).group(0))]['Y (test func)']
            p.scatter(x=x_notfit, y=y_notfit, line_color='red', fill_alpha=1,
                      size=7, legend_label='test_NOT_match')
            band = Band(base='x', lower='lower', upper='upper', source=source, level='underlay',
                        fill_alpha=1.0, line_width=1, line_color='black')
            p.add_layout(band)
            # plot points from test that are fit ideal function
            x_fit = test_match_all[test_match_all['No of ideal func'] == int(re.search(r'\d+', col_res_check[i]).group(0))]['X (test func)']
            y_fit = test_match_all[test_match_all['No of ideal func'] == int(re.search(r'\d+', col_res_check[i]).group(0))]['Y (test func)']
            p.scatter(x=x_fit, y=y_fit, line_color='green', fill_alpha=5,
                      size=12, legend_label='test_match')
            # add decor
            p.legend.location = "bottom"
            p.legend.border_line_width = 2
            p.legend.border_line_color = "navy"
            p.legend.border_line_alpha = 1
            p.legend.label_text_font_size = '10pt'
            p.legend.click_policy = "hide"
            p.title.text = 'Figure to show how good test data fits ideal functions'
            p.add_layout(Label(x=0, y=20000, text='click on the legend to turn on/off'))
        # make a grid and show
        grid_test_ideal = gridplot(pvalues, ncols=2, width=1000, height=500)
        show(grid_test_ideal)
    except Exception:
        exception_type, exception_value, exception_traceback = sys.exc_info()
        print("Error. Test and Ideal functions Visualisations are failed")
        print(''.join('[Error Message]: ' + str(exception_value) + ' ' +
                      '[Error Type]: ' + str(exception_type)))
        sys.exit(1)
