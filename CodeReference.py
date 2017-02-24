# -*- coding: utf-8 -*-
"""
Code Reference File

"""

import os
import json
import requests
import xmltodict
from suds.client import Client
from bs4 import BeautifulSoup
import pymssql
import pandas as pd
import psycopg2
import logging

#==============================================================================
# Config file
#==============================================================================
config_file = open(os.path.dirname(os.path.realpath(__file__)) + '/config.json')
config = json.load(config_file)

#==============================================================================
# Logger Write to File
#==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/logfile.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

#==============================================================================
# Rest API
#==============================================================================
url = 'https://www.myurl.com/'
param = {
            'a': 'aa',
            'b': 'bb'
            }
header = {
            'a':'aa'
            , 'b':'bb'
            }
response = requests.get(url, headers = header, params = param)

# JSON Response
json_response = json.loads(response.text)

# XML Response
xml_response = xmltodict.parse(response.content)


#==============================================================================
# Soap API
#==============================================================================
url = 'https://www.myurl.com/thisisawsdlfile.wsdl'
client = Client(url)
header = client.factory.create('auth')
header.user = 'username'
header.password = 'password'
client.set_options(soapheaders = header)
response = client.service['ServiceName'].methodName({'Param1': 'param'})

#==============================================================================
# XML Body PUT Request
#==============================================================================
xml = """XMl Nonsense here"""
header = {'Content-Type': 'application/xml'}
response = requests.post(url, data = xml, headers = header)
soup = BeautifulSoup(response.content, "lxml")

#==============================================================================
# HTML Scraping Rest Request
#==============================================================================
url = 'https://www.myurl.com/'
param = {
            'a': 'aa',
            'b': 'bb'
            }
response = requests.get(url, params = param)
soup = BeautifulSoup(response.text, 'html.parser')

#==============================================================================
# Connect to MS-SQL Database
#==============================================================================
conn = pymssql.connect('server-name', 'db-name', 'username', 'password')
cursor = conn.cursor()
cursor.execute('INSERT SQL STATEMENT HERE')
results = cursor.fetchall()
cols = [i[0] for i in cursor.description]
cursor.close()
conn.close()

# OR 
conn = pymssql.connect('server-name', 'db-name', 'username', 'password')
results = pd.read_sql('INSERT SQL STATEMENT HERE', conn)
conn.close()

#==============================================================================
# Connect to PostgreSQL Database
#==============================================================================
os.environ['DYLD_LIBRARY_PATH'] = '/Library/PostgreSQL/9.4/lib'
conn = psycopg2.connect("dbname='dbname' user='username' host='hostname' password='password'")
cursor = conn.cursor()
cursor.execute('INSERT SQL STATEMENT HERE')
results = pd.DataFrame(cursor.fetchall())
results.columns =  [i[0] for i in cursor.description] 
cursor.close()
conn.close()

#==============================================================================
# Push to MS-SQL table
#==============================================================================
results = pd.DataFrame()
conn = pymssql.connect('server-name', 'db-name', 'username', 'password')
cursor = conn.cursor()     
cursor.execute("TRUNCATE TABLE tablename")
insertStr = "INSERT INTO table (columns) VALUES (%datatype, %datatype, ...)"
valuesArray = results.as_matrix()
valuesArray = tuple(map(tuple, valuesArray))
cursor.executemany(insertStr,valuesArray)
conn.commit()
cursor.close()
conn.close()

