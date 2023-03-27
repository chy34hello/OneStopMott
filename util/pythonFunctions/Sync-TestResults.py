import configparser
import mysql
import csv
import mysql.connector
from datetime import date
from datetime import datetime
from mysqlConnector import MySQLConnector

table_name = "testHistory"
pk_column_name = "ID"
table_name = "testHistory"
pk_column_name = "ID"
#file_to_sync_with_DB = "work-sheet-Feb2023-Netflix-run3-result.csv"
file_to_sync_with_DB = "work-sheet-Jan-PrimeVideo-result.csv"
config_path = 'config.ini'


# use this file for updating latest Matrix run results
def create_updated_rows(rows, max_pk_value):
    updated_rows = []
    index = 1
    for row in rows:
        new_row = (max_pk_value + index,) + row[1:] + (date.today(),)
        updated_rows.append(new_row)
        index += 1
    return updated_rows

def read_csv_file(file_path):
    with open(file_path, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        rows = [tuple(row) for row in reader]
        return rows


config = configparser.ConfigParser()
config.read(config_path)

connector = MySQLConnector(config_path)
connector.connect()

max_pk_value = connector.fetch_max_pk_value(table_name, pk_column_name)
rows = read_csv_file(file_to_sync_with_DB)
updated_rows = create_updated_rows(rows, max_pk_value)

connector.insert_rows(table_name, updated_rows)
connector.disconnect()

