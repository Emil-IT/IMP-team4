/*
 * SQLite CREATE TABLE examples.
 * Created by Alvin Alexander, http://alvinalexander.com
 * Released under the Creative Commons License.
 */

--
-- coffees
--
CREATE TABLE coffees (
  id INTEGER PRIMARY KEY,
  coffee_name TEXT NOT NULL,
  price REAL NOT NULL
);

--
-- salespeople
--
CREATE TABLE salespeople (
  id INTEGER PRIMARY KEY,
  first_name TEXT NOT NULL,
  last_name TEXT NOT NULL,
  commission_rate REAL NOT NULL
);

--
-- customers
--
CREATE TABLE customers (
  id INTEGER PRIMARY KEY,
  company_name TEXT NOT NULL,
  street_address TEXT NOT NULL,
  city TEXT NOT NULL,
  state TEXT NOT NULL,
  zip TEXT NOT NULL
);

--
-- orders
--
CREATE TABLE orders (
  id INTEGER PRIMARY KEY,
  customer_id INTEGER,
  salesperson_id INTEGER,
  FOREIGN KEY(customer_id) REFERENCES customers(id),
  FOREIGN KEY(salesperson_id) REFERENCES salespeople(id)
);

/*
 * order_items (multiline comment example)
 */
CREATE TABLE order_items (
  id INTEGER PRIMARY KEY,
  order_id INTEGER,
  product_id INTEGER,
  product_quantity INTEGER,
  FOREIGN KEY(order_id) REFERENCES orders(id),
  FOREIGN KEY(product_id) REFERENCES products(id)
);


-- populate db 

/*
 * SQLite INSERT statement examples.
 * Created by Alvin Alexander, http://alvinalexander.com
 * Released under the Creative Commons License.
 */

--
-- coffees
--

INSERT INTO coffees VALUES (null, 'Colombian', 7.99);
INSERT INTO coffees VALUES (null, 'French_Roast', 8.99);
INSERT INTO coffees VALUES (null, 'Espresso', 9.99);
INSERT INTO coffees VALUES (null, 'Colombian_Decaf', 8.99);
INSERT INTO coffees VALUES (null, 'French_Roast_Decaf', 9.99);

--
-- salespeople
--

INSERT INTO salespeople VALUES (null, 'Fred', 'Flinstone', 10.0);
INSERT INTO salespeople VALUES (null, 'Barney', 'Rubble', 10.0);

--
-- customers
--

INSERT INTO customers VALUES (null, 'ACME, INC.', '101 Main Street', 'Anchorage', 'AK', '99501');
INSERT INTO customers VALUES (null, 'FOOBAR', '200 Foo Way', 'Louisville', 'KY', '40207');

--
-- orders
--

INSERT INTO orders VALUES (null, 1, 1);
INSERT INTO orders VALUES (null, 2, 2);

--
-- order_items
--

-- insert one order
INSERT INTO order_items VALUES (null, 1, 1, 5);
INSERT INTO order_items VALUES (null, 1, 2, 8);

-- insert a second order
INSERT INTO order_items VALUES (null, 2, 3, 6);
INSERT INTO order_items VALUES (null, 2, 1, 10);
