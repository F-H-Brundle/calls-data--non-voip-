#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import datetime
import mysql.connector
pd.options.display.max_columns = 32
from datetime import datetime as dt
import traceback


# In[2]:
print("Starting script")

#INPUT PATH
fn = r"C:\Users\administrator.BRUNDLE\Desktop\Call Data.csv"
df = pd.read_csv(fn, sep=",", encoding='latin1', low_memory=False)
print(df)
# UPDATE COLUMN NAMES
col_names = ['callId','startTime', 'answered', 'callerName', 'telephoneNo', 'firstRang', 'lastRang', 'ansOn',  'userAnsOn', 'finishedOn', 'userFinishedOn', 'direction', 'callTime', 'callSegment', 'ringTime', 
'holdTime', 'callType','talkTime', 'ringTimeSeg', 'trunk', 'userFirstRang', 'userLastRang', 'DDI', 'DDIReceived', 'segmentStartTime', 'CLIReceived', 'callerIdentified', 'transferredFrom', 'transferredTo', 'segmentFlags', 'trunkDescription']   
df.columns = col_names

# Function definitions for date and time extraction
def getDate(dateTime):
    return dateTime[0:10]

def getMin(dateTime):
    return dateTime[14:16]

def getH(dateTime):
    return dateTime[11:13]

def getY(dateTime):
    return dateTime[6:10]

def getD(dateTime):
    return dateTime[:2]

def getM(dateTime):
    return dateTime[3:5]

def getDateTime(dateTime):
    try:
        y = int(getY(dateTime))
        m = int(getM(dateTime))
        d = int(getD(dateTime))
        h = int(getH(dateTime))
        minute = int(getMin(dateTime))
        dt = datetime.datetime(y, m, d, h, minute, 0) 
        dt = dt.strftime('%Y-%m-%d %H:%M:%S')
        return dt
    except ValueError:
        return "NA"

# Process the datetime columns
dateTime_dt = df['startTime'].apply(getDateTime)
df.insert((len(df.columns)), 'startDateTime', dateTime_dt)
df.startTime = df.startDateTime
df.drop(['startDateTime'], axis=1, inplace=True)

segDateTime_dt = df['segmentStartTime'].apply(getDateTime)
df.insert((len(df.columns)), 'segmentStartDateTime', segDateTime_dt)
df.segmentStartTime = df.segmentStartDateTime
df.drop(['segmentStartDateTime'], axis=1, inplace=True)

# Functions for extracting year and month
def getStartTimeYear(startTime):
    return startTime[:4]

def getStartTimeMonth(startTime):
    if startTime[5:6] == '0':
        return startTime[6:7]
    if startTime[5:6] == '1':
        return startTime[5:7]

def getfinishedOn2Left(finishedOn):
    if str(finishedOn).isnumeric():
        return str(finishedOn)[0:2]
    else:
        return '0'

# Create new columns based on existing data
startTimeYear = df['startTime'].apply(getStartTimeYear)
startTimeMonth = df['startTime'].apply(getStartTimeMonth)
finishedOn2Left = df['finishedOn'].apply(getfinishedOn2Left)

# Add the new columns to the dataframe
df.insert((len(df.columns)), 'startTimeYear', startTimeYear)
df.insert((len(df.columns)), 'startTimeMonth', startTimeMonth)
df.insert((len(df.columns)), 'finishedOn2Left', finishedOn2Left)

# Replace apostrophes and NaN values
df = df.replace("'", '', regex=True)
df = df.fillna('')

# Convert dataframe columns and values to lists
columns = df.columns.tolist()
values = df.values.tolist()

# Create SQL insert statements
statements = []
for val in values:
    s1 = "INSERT IGNORE INTO `pmrs`.`calls` (`callId`, `startTime`, `answered`, `callerName`, `telephoneNo`, `firstRang`, `lastRang`, `ansOn`, `userAnsOn`, `finishedOn`, `userFinishedOn`, `direction`, `callTime`, `callSegment`, `ringTime`, `holdTime`, `callType`, `talkTime`, `ringTimeSeg`, `trunk`, `userFirstRang`, `userLastRang`, `DDI`, `DDIReceived`, `segmentStartTime`, `CLIReceived`, `callerIdentified`, `transferredFrom`, `transferredTo`, `segmentFlags`, `trunkDescription`, `startTimeYear`, `startTimeMonth`, `finishedOn2Left`) VALUES ("
    s2 = ''
    for i in range(0, len(val)-1):
        s2 = s2 + "'" + str(val[i]) + "', "
    s2 = s2 + "'" + str(val[-1]) + "');"
    st = s1 + s2
    statements.append(st)

# Connect to the MySQL database and execute the insert statements
def insert_into_database(statements, sql_user, sql_password, sql_server, sql_database):
    print("Starting insert into database")
    print(f"Connecting with user: {sql_user} to server: {sql_server}, database: {sql_database}")
    
    try:
        print("Attempting to create MySQL connection object...")
        cnx = mysql.connector.connect(user='csm-reporter', password='LdjoA@D83r@$', host='192.168.1.29', database='pmrs',connection_timeout=60)
        print("Connection to database successful.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")
        import traceback; traceback.print_exc()
        return

    cursor = cnx.cursor()
    for i, statement in enumerate(statements, 1):
            print(f"Executing statement {i}: {statement}")
            cursor.execute(statement)
    cnx.commit()
    print("All statements executed and committed successfully.")
    
    
    print("Closing database connection.")
    cursor.close()
    cnx.close()

# Example of how to call the function:
# Replace these variables with your database credentials
sql_user = "csm-reporter"
sql_password = "LdjoA@D83r@$"
sql_server = "192.168.1.29"
sql_database = "pmrs"

print(f"{len(statements)} to insert")

# Call the function to insert the data
insert_into_database(statements, sql_user, sql_password, sql_server, sql_database)
