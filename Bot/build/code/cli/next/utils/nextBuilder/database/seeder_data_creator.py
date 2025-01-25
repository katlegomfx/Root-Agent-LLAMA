# Bot\build\code\cli\next\utils\nextBuilder\database\seeder_data_creator.py
import os
import re
import json
import logging
import sys

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, app_name, MIGRATIONS_DIR  # nopep8

def dummy_values(fields):
    """
    Generate dummy values for the given fields.
    """
    dummy_data = {}
    for field in fields:
        dummy_data[field] = "Dummy"  # You can customize this logic
    return dummy_data

def clean_and_update_json(table_name, fields):
    """
    If the JSON file for the table exists, clean and update it.
    If it doesn't exist, create it.
    """
    data_path = f'{app_name}/src/data'
    json_filename = os.path.join(data_path, f"{table_name}.json")

    if os.path.exists(json_filename):
        with open(json_filename, 'r') as file:
            records = json.load(file)

        if not records:  # If the file doesn't exist or is empty
            records.append(dummy_values(fields))

        # Retain only fields that exist in the migration
        cleaned_records = []
        for record in records:
            cleaned_record = {field: record[field]
                              for field in fields if field in record}
            cleaned_records.append(cleaned_record)

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

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    main()
