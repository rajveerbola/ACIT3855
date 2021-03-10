import mysql.connector

db_conn = mysql.connector.connect(host="acit38555.eastus.cloudapp.azure.com", user="root", password="password", database="carpart")

c = db_conn.cursor()

c.execute('''
          CREATE TABLE car_part_order
          (id INT NOT NULL AUTO_INCREMENT,
          price_id INT NOT NULL,
           part_id VARCHAR(250) NOT NULL,
           name_of_part VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT car_part_order_pk PRIMARY KEY (id))
          ''')

c.execute('''
          CREATE TABLE cleaning_product_order
          (id INT NOT NULL AUTO_INCREMENT,
          price_id VARCHAR(250) NOT NULL,
           brand_id VARCHAR(250) NOT NULL,
           type_id VARCHAR(250) NOT NULL,
           date_created VARCHAR(100) NOT NULL,
           CONSTRAINT cleaning_product_order_pk PRIMARY KEY (id))
          ''')

db_conn.commit()
db_conn.close()