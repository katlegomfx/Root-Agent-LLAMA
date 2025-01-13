# utils\nextBuilder\database\data.py
import json
import sys
import os
import mysql.connector
import json
import logging

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, app_name, MIGRATIONS_DIR  # nopep8


def update_user(record):
    connection = mysql.connector.connect(
        host="127.0.0.1",
        user="root",
        password="",
        database="flex_development"
    )

    # Create a cursor object to interact with MySQL
    cursor = connection.cursor()

    # Write your query
    query = "SELECT * FROM users WHERE role = 'Admin'"

    # Execute the query
    cursor.execute(query)

    # Fetch results
    results = cursor.fetchone()

    # Don't forget to close the connection when done
    cursor.close()
    connection.close()

    if results != None:

        record['user_id'] = results[0]

        return record
    else:
        return results



def dummy_values(field_details):
    """
    Generate dummy values for the given fields based on their types.
    """
    dummy_data = {}
    for field, field_type in field_details.items():
        if f"{field}".endswith('_id'):
            if field == "user_id":

                # Set up the connection
                connection = mysql.connector.connect(
                    host="127.0.0.1",
                    user="root",
                    password="",
                    database="flex_development"
                )

                # Create a cursor object to interact with MySQL
                cursor = connection.cursor()

                # Write your query
                query = "SELECT * FROM users WHERE role = 'Admin'"

                # Execute the query
                cursor.execute(query)

                # Fetch results
                results = cursor.fetchone()

                # Don't forget to close the connection when done
                cursor.close()
                connection.close()
                # print(results[0])
                dummy_data[field] = results[0]
            else:
                pass

        else:
            if field_type == "STRING":
                dummy_data[field] = "DummyString"
            elif field_type == "INTEGER":
                dummy_data[field] = 123
            elif field_type == "BOOLEAN":
                dummy_data[field] = True
            # Add more conditions for other DataTypes as needed
            else:
                dummy_data[field] = "UnknownType"
    return dummy_data


def clean_and_update_json(table_name, fields):
    """
    If the JSON file for the table exists, clean and update it.
    If it doesn't exist, create it.
    """
    data_path = 'src/data'
    json_filename = os.path.join(app_name, data_path, f"{table_name}.json")

    if os.path.exists(json_filename):
        with open(json_filename, 'r') as file:
            records = json.load(file)

        if not records or len(records) == 0:
            records.append(dummy_values(fields))


        # Retain only fields that exist in the migration
        cleaned_records = []
        for record in records:
            expect = update_user(record)
            if expect != None:
                if 'user_id' in record:
                    record = expect
            
            cleaned_record = {field: record[field]
                            for field in fields if field in record}
            cleaned_records.append(cleaned_record)


        # print(f"Cleaned Records: {cleaned_records}")
        with open(json_filename, 'w') as file:
            json.dump(cleaned_records, file, indent=4)

    else:
        # Create a new JSON file if it doesn't exist
        with open(json_filename, 'w') as file:
            json.dump([], file, indent=4)


def main():

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        migration_filename = os.path.join(
            app_name, MIGRATIONS_DIR, migration_file)

        table_name, fields = extract_table_details_from_migration(
            migration_filename)
        if table_name:
            clean_and_update_json(table_name, fields)
            logging.info(f"Processed JSON file for table '{table_name}'.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
