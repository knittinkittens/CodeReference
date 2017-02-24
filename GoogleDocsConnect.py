# -*- coding: utf-8 -*-
"""
Created on Thu Dec  1 13:57:08 2016


Purpose:
    This script takes a Google Doc spreadsheet and pushes it's contents into a table in the warehouse.
    
Methods:
    Takes two arguements: Google Doc name, and table name.
    Connects to Google using Gspread (awww yeaaaa).
    Attempts to open spreadsheet by the title and gets a list of all the worksheets in the spreadsheet to iterate through.
    Gets the entire contents of each worksheet and appends it to a list.
    Gets rid of blank rows (simply unnecessary).
    Gets rid of the multiple header rows (one taken from each worksheet page).
    Converts the data to either an int, float, or string.
    Checks the datatypes over each column: if all rows are a single data type, then that is how we will push it into the warehouse.
    Builds SQL insert string from the data types and column headers (assumes column headers match the warehouse table column names).
    Splits the data into 1000 row chunks (SQL executemany limit...bleh).
    Truncates table, and then attempts to fill the table with the chunks of data.
    
Issues:
    This script assumes that the data is not ill-formatted in the spreadsheet, and that the table being pushed to is created and 
        has columns names matching the headers of the spreadsheet and data types matching those in the spreadsheet.

"""

#==============================================================================
# Package imports
#==============================================================================
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os
import pymssql
import math
import json
from itertools import chain
import sys
import logging

#==============================================================================
# Format logger
#==============================================================================
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
hdlr = logging.FileHandler(os.path.dirname(os.path.realpath(__file__)) + '/logfile.log')
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')
hdlr.setFormatter(formatter)
logger.addHandler(hdlr) 
logger.setLevel(logging.WARNING)

#==============================================================================
# Variable declarations
#==============================================================================
try:
    config_file = open(os.path.dirname(os.path.realpath(__file__)) + '/config.json')
except:
    logger.error('Config file not found', exc_info = True)
    sys.exit(1)

config          = json.load(config_file)
db_user         = config['db_username']
db_password     = config['db_password']
server_name     = config['server_name']
db              = config['db_name']
scope           = ['https://spreadsheets.google.com/feeds']
g_config_file   = os.path.dirname(os.path.realpath(__file__)) + '/google_config.json'

#==============================================================================
# Function to take spreadsheet, iterate through all tabs, and return list
#==============================================================================
def convert_data(data_point):

   if isinstance(data_point, int):
       return data_point
   else:
       try:
           return float(data_point)
       except:
           return data_point    

#==============================================================================
# Get all vaclues from ach worksheet of a spreadsheet          
#==============================================================================
def get_spreadsheet(title, gc):
    
    try:
        sht = gc.open(title)
    except:
        logger.error('Unable to open spreadsheet', exc_info = True)
        sys.exit(1)
    
    worksheet_list = sht.worksheets()
    
    values = []
    for j in worksheet_list:
        wk = j.get_all_values()
        values.append(wk)
    cols = values[0][0]
    del values[0][0]
    values = list(chain.from_iterable(values))
    
    # Delete blank rows just in case
    values = [i for i in values if any(j != '' for j in i)]
    values = [i for i in values if i != cols]
    values = [[convert_data(y) for y in x] for x in values]
    
    return values, cols
        
#==============================================================================
# Preprocess the data to get the correct column names and value types
#==============================================================================
def preprocess(df, cols):
    
    dtypes = []
    for i in range(len(cols)):
        column = [item[i] for item in df]
        data = [type(x) for x in column]   
        if ((len(set(data)) == 1) and (str(data[0]) == "<class 'str'>")):
            dtypes.append('%s')
        elif ((len(set(data)) == 1) and (str(data[0]) == "<class 'int'>")):
            dtypes.append('%d')
        elif ((len(set(data)) == 1) and (str(data[0]) == "<class 'float'>")):
            dtypes.append('%d')            
        else:
            dtypes.append("%s")

    col = str(cols).replace("'", "")[1:-1]
    stri = '(' + str(dtypes).replace("'", '')[1:-1] + ')'
    
    return col, stri

#==============================================================================
# Add a batch of values to the table in the warehouse            
#==============================================================================
def fill_table(server_name, db_user, db_password, db, df, col, stri, table):

    try:
        conn = pymssql.connect(server_name, db_user, db_password, db)
        cursor = conn.cursor()
        
        insertStr = "INSERT INTO " + table  + ' (' + col + ") VALUES " + stri
        valuesArray = tuple(map(tuple, df))
        cursor.executemany(insertStr,valuesArray)
        conn.commit()
        cursor.close()
        conn.close()
    except:
        logger.error('Unable to update table', exc_info = True)
        cursor.close()
        conn.close()
        sys.exit(1)

#==============================================================================
# Split the spreadshet values into batches for push into table
#==============================================================================
def split_and_fill(values, server_name, db_user, db_password, db, col, stri, table):

    conn = pymssql.connect(server_name, db_user, db_password, db)
    cursor = conn.cursor()
    cursor.execute("TRUNCATE TABLE " + table)
    conn.commit()
    cursor.close()
    conn.close()

    for i in range(int(math.ceil(len(values)/1000))):
        df = values[i*1000:i*1000+1000] 
        fill_table(server_name, db_user, db_password, db, df, col, stri, table)

#==============================================================================
# Authorize and pull
#==============================================================================
def main():
    
    try:
        title = sys.argv[1]
        table = sys.argv[2]
    except:
        logger.error('Incorrect number of arguments', exc_info=True)
        sys.exit(1)
    try:
        credentials     = ServiceAccountCredentials.from_json_keyfile_name(g_config_file, scope)
        gc              = gspread.authorize(credentials)
    except:
        logger.error('Cannot connect to google docs', exc_info=True)
        sys.exit(1)
        
    values, cols    = get_spreadsheet(title, gc)
    col, stri       = preprocess(values, cols)
    split_and_fill(values, server_name, db_user, db_password, db, col, stri, table)
    
if __name__ == '__main__':
    main()
    
