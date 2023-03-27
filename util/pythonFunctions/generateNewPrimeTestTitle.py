import mysql.connector
import configparser
import pandas as pd
from datetime import date, datetime
from mysqlConnector import MySQLConnector
from title_sanitizer import TitleSanitizer

table_name = "testedTitles"
pk_column_name = "titleID"
file_to_read = "FebPrimeVideo Source.xlsx"


config_path = 'config.ini'
config = configparser.ConfigParser()
config.read(config_path)


connector = MySQLConnector(config_path)
connector.connect()

connector.fetch_column_as_string(table_name, "titleName")
rows = connector.cursor.fetchall()
titles = set([str(row[0]) for row in rows])

sanitizer = TitleSanitizer(file_to_read)
sanitized_titles = sanitizer.get_sanitized_titles()

count=0
video_titles =[]
for title in sanitized_titles:
    if title not in titles:
        count+=1
        video_titles.append(title)
        print(title)


data = {"ID": list(range(1, len(video_titles)+1)),
        "Video Title": video_titles,
        "Utterance": ["play {} from Prime Video".format(title) for title in video_titles]}
df = pd.DataFrame(data)
df.to_excel("test_titles_PrimeVideo.xlsx", index=False)
        

connector.disconnect()