# Bot\build\code\cli\next\utils\nextBuilder\backend\utils_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, write_to_file, MIGRATIONS_DIR, UTILS_DIR, app_name  # nopep8

# Template for the utility functions
UTILS_TEMPLATE = """
/**
 * Fetch all {model_name} records.
 */
export const fetch{model_name_cap} = async () => {{
    try {{
        const response = await fetch('http://localhost:3000/api/{model_name}');
        return response.json();
    }} catch (error) {{
        console.error("Failed to fetch {model_name}.", error);
        return null;
    }}
}}

/**
 * Create a new {model_name} record.
 * @param {{object}} data - Data for the new {model_name}
 */
export const create{model_name_cap} = async (data) => {{
    try {{
        const response = await fetch('http://localhost:3000/api/{model_name}', {{
            method: 'POST',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify(data)
        }});
        return response.json();
    }} catch (error) {{
        console.error("Failed to create {model_name}.", error);
        return null;
    }}
}}

/**
 * Update an existing {model_name} record.
 * @param {{object}} data - Updated data for the {model_name}
 */
export const update{model_name_cap} = async (id, data) => {{
    try {{
        const response = await fetch(`/api/{model_name}/${{id}}`, {{
            method: 'PUT',
            headers: {{
                'Content-Type': 'application/json'
            }},
            body: JSON.stringify(data)
        }});
        return response.json();
    }} catch (error) {{
        console.error("Failed to update {model_name}.", error);
        return null;
    }}
}}

/**
 * Delete a {model_name} record.
 * @param {{number}} id - ID of the {model_name} to delete
 */
export const delete{model_name_cap} = async (id) => {{
    try {{
        const response = await fetch(`/api/{model_name}/${{id}}`, {{
            method: 'DELETE'
        }});
        return response.json();
    }} catch (error) {{
        console.error("Failed to delete {model_name}.", error);
        return null;
    }}
}}
"""

def create_utils_for_model(model_name):
    """Create utility functions for the given model."""
    model_name_cap = model_name.capitalize()
    utils_content = UTILS_TEMPLATE.format(
        model_name=model_name, model_name_cap=model_name_cap).lstrip()

    # Write the utility functions to a file within the utils directory
    file_path = os.path.join(app_name, UTILS_DIR, f"{model_name}.js")
    write_to_file(file_path, utils_content)

def main():
    """Main function to generate utility functions for each migration file."""
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):  # Filter out non-JavaScript files
            migration_filename = os.path.join(app_name,
                MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            model_name = table_name
            create_utils_for_model(model_name)

if __name__ == "__main__":
    main()
