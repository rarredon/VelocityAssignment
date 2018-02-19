CREATE TABLE IF NOT EXISTS request (
  id integer PRIMARY KEY AUTOINCREMENT,
  title text NOT NULL,
  description text NOT NULL,
  client integer NOT NULL,
  priority integer NOT NULL,
  target_date text NOT NULL,
  product_area text NOT NULL,
  FOREIGN KEY(client) REFERENCES client(id),
  CONSTRAINT client_priority UNIQUE (client, priority)
);
CREATE TABLE IF NOT EXISTS client (
  id integer PRIMARY KEY AUTOINCREMENT,
  'name' text NOT NULL,
  city text NOT NULL,
  'state' text NOT NULL,
  CONSTRAINT uniq_name UNIQUE ('name')
 );
  
