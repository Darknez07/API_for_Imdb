import pandas as pd
from flask import Flask, g, jsonify
import sqlite3
import subprocess
import random
import string
import numpy as np
letters_count = 20
digits_count = 12

try:

    stdo = subprocess.check_output(['scrapy','crawl','Movies','-o','ImdbRated1000.csv'],
                               stderr=subprocess.STDOUT,
                               timeout=120) # 2 mins
except:

    print("Done Gathering data")

finally:

    sql = sqlite3.connect('db/Imdb.db')
    db = pd.read_csv('../ImdbRated1000.csv')
    db["Id"] = np.array([i[0].split('/')[4][2:] for i in db[['Movie_Url']].values])
    db.to_sql('Movies', con=sql,if_exists='append', index=False)