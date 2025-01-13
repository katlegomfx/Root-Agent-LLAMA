# utils\nextBuilder\database\sequelize_model_creator.py
import re
import logging
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    MIGRATIONS_DIR,
    app_name,
    write_to_file

)

def extract_model_details(migration_filename):
    """
    Extract model details from the migration file.
    """
    with open(migration_filename, 'r') as file:
        migration_content = file.read()

    # Extract model and table names
    model_name = os.path.basename(migration_filename).split('-')[1].split('_')[0]
    table_name = re.findall(r"await queryInterface\.createTable\('(\w+)'", migration_content)[0]
    
    # Extract fields and their attributes
    field_blocks = re.findall(r"(\w+): {([^}]+)}", migration_content)
    fields = {}
    for field, attributes in field_blocks:
        if field.endswith('_id'):
            fields[field] = attributes.strip().split(',')
        else:
            # For fields not ending with _id, only keep the type attribute
            type_match = re.search(r"type: (Sequelize\.\w+)", attributes)
            if type_match:
                fields[field] = [type_match.group(0)]
    
    return model_name, table_name, fields

def generate_model_file_fixed(model_name, table_name, fields):
    """
    Generate Sequelize model file content based on the extracted details.
    """
    model_content = f"const Sequelize = require('sequelize');\n\nexport default function {model_name}Model(sequelize, DataTypes) {{\n  return sequelize.define('{table_name}', {{\n"

    for field_name, attributes in fields.items():
        field_content = f"    {field_name}: {{\n"
        
        for attribute in attributes:
            if "references:" in attribute:
                field_content += f"      references: {{\n"
            else:
                field_content += f"      {attribute.strip()},\n"
        
        # Close the references attribute if it was opened and remove the trailing comma
        if "references:" in field_content:
            field_content = field_content.rstrip(",\n") + "\n      },\n"
        
        # Remove any trailing commas for the last attribute
        field_content = field_content.rstrip(",\n") + "\n    },\n"
        model_content += field_content

    model_content += f"  }}, {{\n    timestamps: true\n  }});\n}};"
    return model_content

def main():
    # logging.info("Starting Sequelize model generation process...")

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        migration_filename = os.path.join(
            app_name, MIGRATIONS_DIR, migration_file)
        
        model_name, table_name, fields = extract_model_details(migration_filename)
        model_content = generate_model_file_fixed(model_name, table_name, fields)

        filename_after = migration_file.split('-')[1].split('_')[0]
        filename_after += '.js'
        model_filename = os.path.join(
            app_name, "src/models", filename_after)
        
        write_to_file(model_filename, model_content)

        logging.info(f"Model file '{model_filename}' generated successfully!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    main()
