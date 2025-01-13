# utils\nextBuilder\database\sequelize_seeder.py
import os
import re
import json
import logging
import sys

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, write_to_file, app_name, MIGRATIONS_DIR  # nopep8


def generate_seeder_content(table_name):
    """
    Generate Sequelize seeder file content based on table name.
    """
    return f"""'use strict';

const fs = require('fs');
const path = require('path');

module.exports = {{
  up: async (queryInterface, Sequelize) => {{

    // Read the JSON file's content
    const data = fs.readFileSync(path.join(__dirname, '../data/{table_name}.json'), 'utf8');

    // Parse the JSON content
    const records = JSON.parse(data);

    // Use the parsed data to bulk insert into the {table_name.capitalize()} table
    return queryInterface.bulkInsert('{table_name}', records, {{}});

  }},

  down: async (queryInterface, Sequelize) => {{
    return queryInterface.bulkDelete('{table_name}', null, {{}});
  }}
}};
"""

def main():

    seeders_path = 'src/seeders'
    seeders_path = os.path.join(app_name, seeders_path)
    
    # Delete existing seeders
    existing_seeders = [f for f in os.listdir(seeders_path) if os.path.isfile(os.path.join(seeders_path, f))]
    for seeder in existing_seeders:
        os.remove(os.path.join(seeders_path, seeder))

    # Define a starting prefix and a method to increment it
    prefix = 1
    def get_next_prefix():
        nonlocal prefix
        result = str(prefix).zfill(3)
        prefix += 1
        return result

    user_seeder_content = generate_seeder_content('users')
    write_to_file(os.path.join(seeders_path, f'000-users_seeder.js'), user_seeder_content)

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        migration_filename = os.path.join(
            app_name, MIGRATIONS_DIR, migration_file)
        
        table_name, fields = extract_table_details_from_migration(
            migration_filename)
        if table_name and table_name != 'users':  # Exclude users as it's already created
            seeder_content = generate_seeder_content(table_name)
            seeder_filename = f"{get_next_prefix()}-{table_name}_seeder.js"
            write_to_file(os.path.join(
                seeders_path, seeder_filename), seeder_content)


            logging.info(f"Seeder file '{seeder_filename}' generated successfully!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
