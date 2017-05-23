import sqlite3
import os
import os.path
#import ctypes

databaseFile = './test.db'
sqlFile = './init_warehouse.sql'

# Delete the old table
#if os.path.isfile(databaseFile):
#	os.remove(databaseFile)

# Create the tables
qry = open(sqlFile, 'r').read()
sqlite3.complete_statement(qry)
conn = sqlite3.connect(databaseFile)
cursor = conn.cursor()
try:
	cursor.executescript(qry)
except Exception as e:
	print(e)
	cursor.close()
	raise