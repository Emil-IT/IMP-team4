def buildZones(connection):
	
	query = 'select no_aisles, rows_per_aisle, position, site from zone, warehouse where zone.warehouse_id=warehouse.id'
	cursor = connection.cursor()
	cursor.execute(query)
	result = cursor.fetchall()
	zonesJSON = '"zones": ['
	for res in result:
		query = 'select * from arduino, warehouse where warehouse.id=arduino.warehouse_id and warehouse.site="%s"'%(res[3])
		zonesJSON += '{"aisles":%d, "rows":%d, "zonename":"%s%d","sensors":['%(res[0], res[1], res[3], res[2])
		sensorRes = (cursor.execute(query)).fetchall()
		for each in sensorRes:
			zonesJSON += '{"shelves":['
			query = 'select shelf.name from shelf, arduino, warehouse where shelf.arduino_id=arduino.id and arduino.warehouse_id=warehouse.id'
			cursor.execute(query)
			result2 = cursor.fetchall()
			for shelf in result2:
				zonesJSON += '"%s",'%(shelf[0])
			zonesJSON = zonesJSON[:-1] # remove last char (,)
			query = 'select reading from shelf, zone, warehouse, arduino, sensor where zone.warehouse_id=warehouse.id and shelf.arduino_id=sensor.arduino_id and shelf.warehouse_id=arduino.warehouse_id and arduino.warehouse_id=zone.warehouse_id group by sensor.type'
			cursor.execute(query)
			result2 = cursor.fetchall()
			zonesJSON += '],"readings":{"temperature":%d,"light":%d,"humidity":%.2f}},'%(result2[0][0], result2[1][0], result2[2][0])
			zonesJSON = zonesJSON[:-1]
		zonesJSON += ']},'
	zonesJSON = zonesJSON[:-1] # remove last char (,)
	zonesJSON += ']'
	return zonesJSON
	
def buildRobots(connection):
	return '"robots":[{"zone": "Uppsala1","id": "12345","position": {"x": 150,"y": 100}}]'

def buildPackages(connection):
	return '"packages":[{"id":"44421","position":{"x":550,"y":20}},{"id":"44532","position":{"x":250,"y":20}},{"id":"44514","position":{"x":250,"y":450}}]'

def buildTasks(connection):
	return '"tasks":[{"task_id":"1234","package_id":"44532","robot_id":"12345","priority":1,"drop_off":"dropoff_2","current_position":{"x":130,"y":200}},{"task_id":"1235","package_id":"44421","robot_id":"12345","priority":2,"drop_off":"dropoff_4","current_position":{"x":130,"y":200}},{"task_id":"1236","package_id":"44514","robot_id":"12345","priority":4,"drop_off":"dropoff_2","current_position":{"x":130,"y":200}}]'
