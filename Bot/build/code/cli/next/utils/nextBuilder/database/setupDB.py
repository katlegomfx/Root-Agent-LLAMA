# Bot\build\code\cli\next\utils\nextBuilder\database\setupDB.py
import json
import sys
import os
import mysql.connector
from mysql.connector import Error
import json
import logging

sys.path.append(os.getcwd())

from utils.shared import db_name, app_name  # nopep8

def create_database(db_name):
    try:
        # Connect to the MySQL server
        connection = mysql.connector.connect(
            host="127.0.0.1",
            user='root',
            password='')

        # Create a cursor object
        cursor = connection.cursor()

        # Check if the database exists
        cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")
        database_exists = cursor.fetchone()

        if database_exists:
            print(f"Database '{db_name}' already exists.")
        else:
            # Create a new database
            cursor.execute(f"CREATE DATABASE {db_name}")
            print(f"Database '{db_name}' created successfully.")

    except Error as e:
        print(f"Error: '{e}'")

    finally:
        # Close the connection
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("MySQL connection is closed")

create_database(db_name)

def update_database_values(json_file_path, new_dev_db, new_test_db, new_prod_db):
    # Open and read the JSON file
    with open(json_file_path, 'r') as file:
        data = json.load(file)

    # Update the database values
    data['development']['database'] = new_dev_db
    data['test']['database'] = new_test_db
    data['production']['database'] = new_prod_db

    # Write the updated JSON back to the file
    with open(json_file_path, 'w') as file:
        json.dump(data, file, indent=2)

json_file_path = os.path.join(app_name, 'src', 'config', 'config.json')
using = db_name.split('_')[0]
new_dev_db = f'{using}_development'
new_test_db = f'{using}_test'
new_prod_db = f'{using}_production'
update_database_values(json_file_path, new_dev_db, new_test_db, new_prod_db)
