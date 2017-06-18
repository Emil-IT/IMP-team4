import json

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
	
def buildRobots(connection, positions):
	
	robotsJSON = '"robots":['
	position = 0
	cursor = connection.cursor()
	query = 'select warehouse.site, robot.id, zone.position from warehouse, zone, robot where robot.id=zone.robot_id and zone.warehouse_id=warehouse.id'
	cursor.execute(query)
	result = cursor.fetchall()
	for each in result:
		zone = "%s%d"%(each[0], each[2])
		id = (each[1])
		for pos in positions:
			if (pos[0] == each[1]):
				position = (pos[1])
		robotsJSON += (json.dumps({"zone":zone, "id":id, "position":position}) + ',')
	robotsJSON = robotsJSON[:-1] + ']'
	print(robotsJSON)
	return robotsJSON #'"robots":[{"zone": "uppsala0","id": "12345","position": '+position.+'}]'

def buildPackages(connection):
	return '"packages":[{"id":"44421","position":"Conv","carrying":1, "zone":"hanoi0"},{"id":"44532","position":"A3","carrying":0, "zone":"uppsala0"},{"id":"44514","position":"A2","carrying":0, "zone":"uppsala0"}]'

def buildTasks(connection):
	return '"tasks":[{"task_id":"1234","package_id":"44532","robot_id":"12345","priority":1,"drop_off":"A2","status":1},{"task_id":"1235","package_id":"44421","robot_id":"12345","priority":2,"drop_off":"Conv","status":0}]'
