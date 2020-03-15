# TODO: change to use any sql db, use sqlite3 for now.
import sqlite3
import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String
import urllib
from config_reader import ConfigReader
from pandas.io import sql
from datetime import datetime

class DbManager:
    def __init__(self):
        # self.connString = "data.db" # 'data.db'
        # self.type = "sqlite"
        reader = ConfigReader()
        db_connection = reader.get_value("db_connection")        
        self.conn_string = '{db_engine}+{connector}://{user}:{password}@{server}/{database}'.format(
            db_engine=db_connection['db_engine'],
            connector=db_connection['connector'],
            user=db_connection['user'],
            password=db_connection['password'],
            server=db_connection['server'],
            database=db_connection['database'])
    
    # def get_odbc_conn(self):
    #     connstr="Driver={MySQL ODBC 8.0 ANSI Driver};Server=localhost;Port=3306;Database=db;User=root;Password=dingoabc123;charset=UTF8"
    #     conn = pyodbc.connect(connstr)
    #     return conn

    def create_db_structure_with_data(self, movies, ratings, links):
    #     if self.type == "sqlite":
    #         conn = sqlite3.connect(self.connString)
    #         #c = conn.cursor()
    #         movies.to_sql("movies", conn, if_exists="replace")
    #         ratings.to_sql("ratings", conn, if_exists="replace")
    #         links.to_sql("links", conn, if_exists="replace")
    #     else:

            engine = create_engine(self.conn_string)

            # Drop tables
            sql.execute("DROP TABLE IF EXISTS movies", engine)
            sql.execute("DROP TABLE IF EXISTS ratings", engine)

            # # Create tables
            sql.execute('''CREATE TABLE movies
                    (movieId INTEGER, title VARCHAR(200), genres VARCHAR(100))''', engine)
            sql.execute('''CREATE TABLE ratings
                    (userId INTEGER, itemId INTEGER, rating FLOAT, timestamp TIMESTAMP)''', engine)
           
            count = 0
            for index, row in movies.iterrows():
                sql.execute("INSERT INTO movies VALUES ({movieId}, '{title}', '{genres}')".format(
                    movieId=row['movieId'],
                    title=row['title'].replace("'", r"\'"),
                    genres=row['genres']), 
                    engine)
                count += 1
                if count >= 100:
                    break

            count = 0
            for index, row in ratings.iterrows():
                sql.execute("INSERT INTO ratings VALUES ({userId}, {itemId}, {rating}, '{timestamp}')".format(
                    userId=row['userId'],
                    itemId=row['movieId'],
                    rating=row['rating'],
                    timestamp=datetime.utcfromtimestamp(int(row['timestamp'])).strftime('%Y-%m-%d %H:%M:%S')),
                    engine)
                count += 1
                if count >= 100:
                    break
 
    def get_ratings(self):
        conn = sqlite3.connect(self.connString)
        return pd.read_sql_query("SELECT userId, itemId, rating, timestamp FROM ratings;", conn)

    def get_movies(self):
        conn = sqlite3.connect(self.connString)
        return pd.read_sql_query("SELECT movieId, title, genres FROM movies;", conn)

    def get_links(self):
        conn = sqlite3.connect(self.connString)
        return pd.read_sql_query("SELECT movieId, imdbId, tmdbId FROM links;", conn)