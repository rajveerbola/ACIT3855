import mysql.connector

db_conn = mysql.connector.connect(host="acit38555.eastus.cloudapp.azure.com", user="root", password="password", database="carpart")

c = db_conn.cursor()
c.execute('''
          DROP TABLE car_part_order, cleaning_product_order
          ''')

db_conn.commit()
db_conn.close()
