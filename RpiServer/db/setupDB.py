import sqlite3
import os
import os.path
#import ctypes
def setup(path):
	databaseFile = (path + 'warehouses.db')
	sqlFile = (path + 'init_warehouse.sql')
	
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
	# warehouses
	cursor.execute('insert into warehouse (id, site) values (123, "uppsala")')
	cursor.execute('insert into warehouse (id, site) values (456, "hanoi")')
	
	# zones
	cursor.execute('insert into zone (no_aisles, rows_per_aisle, position, warehouse_id, robot_id) values (2, 3, 0, 123, NULL)')
	cursor.execute('insert into zone (no_aisles, rows_per_aisle, position, warehouse_id, robot_id) values (1, 3, 0, 456, NULL)')
	
	# shelves
	chars = ['A', 'B', 'C', 'D']
	for c in chars:
		for i in range(0,6):
			query = 'insert into shelf (name, warehouse_id, package_id, arduino_id) values ("%c%d", 123, NULL, NULL)' %(c, i)
			cursor.execute(query)
	
	chars = ['A', 'B']
	for c in chars:
		for i in range(0,6):
			query = 'insert into shelf (name, warehouse_id, package_id, arduino_id) values ("%c%d", 456, NULL, NULL)' %(c, i)
			cursor.execute(query)
	
	# arduinos
	cursor.execute('insert into arduino (id, warehouse_id) values (1337, 123)')
	
	# sensors
	cursor.execute('insert into sensor (type, reading, arduino_id) values ("temperature", NULL, 1337)')
	cursor.execute('insert into sensor (type, reading, arduino_id) values ("humidity", NULL, 1337)')
	cursor.execute('insert into sensor (type, reading, arduino_id) values ("light", NULL, 1337)')
	
	#save changes
	conn.commit()

	return conn
