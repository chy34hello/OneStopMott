import mysql.connector
import configparser




class MySQLConnector:
    def __init__(self, config_path):
        config = configparser.ConfigParser()
        config.read(config_path)
        self.host = config.get('database', 'host')
        self.user = config.get('database', 'user')
        self.password = config.get('database', 'password')
        self.database = config.get('database', 'database')

    def connect(self):
        self.cnx = mysql.connector.connect(
            host=self.host,
            user=self.user,
            password=self.password,
            database=self.database
        )
        self.cursor = self.cnx.cursor()

    def disconnect(self):
        self.cursor.close()
        self.cnx.close()

    def fetch_column_as_string(self, table_name, column_name):
        query = "SELECT " + column_name + " FROM " + table_name
        self.cursor.execute(query)

    def fetch_max_pk_value(self, table_name, pk_column_name):
        query = "SELECT MAX({}) FROM {}".format(pk_column_name, table_name)
        self.cursor.execute(query)
        result = self.cursor.fetchone()
        return result[0]

    def insert_rows(self, table_name, rows):
        sql_query = "INSERT INTO {}  values (%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s, %s, %s, %s);".format(table_name)
        self.cursor.executemany(sql_query, rows)
        self.cnx.commit()

    def insert_rows_tested_title(self, table_name, rows):
        sql_query = "INSERT INTO {}  values (%s, %s, %s, %s);".format(table_name)
        self.cursor.executemany(sql_query, rows)
        self.cnx.commit()