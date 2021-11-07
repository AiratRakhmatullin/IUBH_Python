# use code with some adaptation from https://thinkdiff.net/how-to-use-python-sqlite3-using-sqlalchemy-158f9c54eb32

from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer,  MetaData, Float

# Variables
SQLITE = 'sqlite'

# Table Names
TRAIN = 'training_functions'
IDEAL = 'ideal_functions'
TEST = 'test_functions'


class MyDatabase:
    DB_ENGINE = {
        SQLITE: 'sqlite:///{DB}'
    }

    # Main DB Connection Ref Obj
    db_engine = None

    def __init__(self, dbtype, username='', password='', dbname=''):
        dbtype = dbtype.lower()
        if dbtype in self.DB_ENGINE.keys():
            engine_url = self.DB_ENGINE[dbtype].format(DB=dbname)
            self.db_engine = create_engine(engine_url)
            print(self.db_engine)
        else:
            print("DBType is not found in DB_ENGINE")

    # create tables
    def create_db_tables(self):
        metadata = MetaData()

        train = Table(TRAIN, metadata,
                      Column('X', Float),
                      Column('Y1 (training function)', Float),
                      Column('Y2 (training function)', Float),
                      Column('Y3 (training function)', Float),
                      Column('Y4 (training function)', Float)
                      )

        ideal = Table(IDEAL, metadata,
                      Column('X', Float),
                      Column('Y1 (ideal function)', Float), Column('Y2 (ideal function)', Float),
                      Column('Y3 (ideal function)', Float), Column('Y4 (ideal function)', Float),
                      Column('Y5 (ideal function)', Float), Column('Y6 (ideal function)', Float),
                      Column('Y7 (ideal function)', Float), Column('Y8 (ideal function)', Float),
                      Column('Y9 (ideal function)', Float), Column('Y10 (ideal function)', Float),
                      Column('Y11 (ideal function)', Float), Column('Y12 (ideal function)', Float),
                      Column('Y13 (ideal function)', Float), Column('Y14 (ideal function)', Float),
                      Column('Y15 (ideal function)', Float), Column('Y16 (ideal function)', Float),
                      Column('Y17 (ideal function)', Float), Column('Y18 (ideal function)', Float),
                      Column('Y19 (ideal function)', Float), Column('Y20 (ideal function)', Float),
                      Column('Y21 (ideal function)', Float), Column('Y22 (ideal function)', Float),
                      Column('Y23 (ideal function)', Float), Column('Y24 (ideal function)', Float),
                      Column('Y25 (ideal function)', Float), Column('Y26 (ideal function)', Float),
                      Column('Y27 (ideal function)', Float), Column('Y28 (ideal function)', Float),
                      Column('Y29 (ideal function)', Float), Column('Y30 (ideal function)', Float),
                      Column('Y31 (ideal function)', Float), Column('Y32 (ideal function)', Float),
                      Column('Y33 (ideal function)', Float), Column('Y34 (ideal function)', Float),
                      Column('Y35 (ideal function)', Float), Column('Y36 (ideal function)', Float),
                      Column('Y37 (ideal function)', Float), Column('Y38 (ideal function)', Float),
                      Column('Y39 (ideal function)', Float), Column('Y40 (ideal function)', Float),
                      Column('Y41 (ideal function)', Float), Column('Y42 (ideal function)', Float),
                      Column('Y43 (ideal function)', Float), Column('Y44 (ideal function)', Float),
                      Column('Y45 (ideal function)', Float), Column('Y46 (ideal function)', Float),
                      Column('Y47 (ideal function)', Float), Column('Y48 (ideal function)', Float),
                      Column('Y49 (ideal function)', Float), Column('Y50 (ideal function)', Float)
                      )

        test = Table(TEST, metadata,
                     Column('X (test function)', Float),
                     Column('Y (test function)', Float),
                     Column('Delta Y (test function)', Float),
                     Column('No of ideal function', Integer)
                     )

        try:
            metadata.create_all(self.db_engine)
            print("Tables are created")
        except Exception as e:
            print("Error occurred during table creation!")
            print(e)

    # Insert, Update, Delete with query
    def execute_query(self, query=''):
        if query == '':
            return
        # print(query)
        with self.db_engine.connect() as connection:
            try:
                connection.execute(query)
            except Exception as e:
                print(e)

    # Insert pandas DataFrame
    def insert_dataframe(self, df, table):
        try:
            df.to_sql(table, con=self.db_engine, if_exists='replace', index=False)
        except Exception as e:
            print(e)

    # method will print all the data from a database table we provided as a parameter.
    def print_all_data(self, table='', query=''):
        query = query if query != '' else "SELECT * FROM '{}';".format(table)
        print(query)
        with self.db_engine.connect() as connection:
            try:
                result = connection.execute(query)
            except Exception as e:
                print(e)
            else:
                for row in result:
                    print(row)  # print(row[0], row[1], row[2])
                result.close()
        print("\n")
