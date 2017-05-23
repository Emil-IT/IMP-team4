
--DROP TABLE warehouse, robot, zone, arduino, package, sensor, shelf;


CREATE TABLE warehouse (
	id INTEGER PRIMARY KEY,
	site TEXT NOT NULL
);

CREATE TABLE robot (
	id INTEGER PRIMARY KEY,
	aisle INTEGER NOT NULL,
	warehouse_id INTEGER NOT NULL,
	
	FOREIGN KEY(warehouse_id) REFERENCES warehouse(id)
);

CREATE TABLE zone (
	no_aisles INTEGER NOT NULL,
	rows_per_aisle INTEGER NOT NULL,
	position INTEGER,
	warehouse_id INTEGER,
	robot_id INTEGER,
	
	FOREIGN KEY(warehouse_id) REFERENCES warehouse(id),
	FOREIGN KEY(robot_id) REFERENCES robot(id),
	PRIMARY KEY(position, warehouse_id)
);

CREATE TABLE arduino (
	id INTEGER PRIMARY KEY,
	warehouse_id INTEGER NOT NULL,
	
	FOREIGN KEY(warehouse_id) REFERENCES warehouse(id)
);

CREATE TABLE sensor (
	type TEXT,
	reading REAL,
	arduino_id INT,
	
	FOREIGN KEY(arduino_id) REFERENCES arduino(id),
	PRIMARY KEY(type, arduino_id)
);

CREATE TABLE shelf (
	name TEXT,
	warehouse_id INTEGER,
	package_id INTEGER,
	arduino_id INTEGER,
	
	FOREIGN KEY(arduino_id) REFERENCES arduino(id),
	FOREIGN KEY(warehouse_id) REFERENCES warehouse(id),
	FOREIGN KEY(package_id) REFERENCES package(id),
	PRIMARY KEY(name, warehouse_id)
);

CREATE TABLE package (
	id INTEGER PRIMARY KEY,
	status TEXT NOT NULL
);
