# Bot\build\code\cli\next\utils\nextBuilder\backend\model_wildcard_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, write_to_file, MIGRATIONS_DIR, API_ROUTE_DIR, app_name  # nopep8

def generate_api_template(model_name, fields):
    model_name_cap = str(model_name)[0].capitalize()+str(model_name)[1:]
    primary_key = fields['primary_key']
    """Generate the API template for the given model."""
    return f"""
import db from '../../../models';

export default async function handler(req, res) {{
    const {{
        query: { primary_key },
        method,
        body,
    }} = req;

    switch (method) {{
        case 'GET':
            try {{
                const item = await db.{model_name_cap}.findByPk({primary_key});
                if (!item) return res.status(404).json({{ message: 'Service not found' }});
                return res.status(200).json(item);
            }} catch (error) {{
                return res.status(500).json({{ error: error.message }});
            }}

        case 'PUT':
            try {{
                const [updated] = await db.{model_name_cap}.update(body, {{ where: { primary_key } }});
                if (!updated) return res.status(404).json({{ message: 'Service not found' }});
                return res.status(200).json({{ message: 'Service updated successfully' }});
            }} catch (error) {{
                return res.status(500).json({{ error: error.message }});
            }}

        case 'DELETE':
            try {{
                const deleted = await db.{model_name_cap}.destroy({{ where: { primary_key } }});
                if (!deleted) return res.status(404).json({{ message: 'Service not found' }});
                return res.status(200).json({{ message: 'Service deleted successfully' }});
            }} catch (error) {{
                return res.status(500).json({{ error: error.message }});
            }}

        default:
            res.setHeader('Allow', ['GET', 'PUT', 'DELETE']);
            res.status(405).end(`Method ${{method}} Not Allowed`);
    }}
}}
"""

def create_api_route_for_model(model_name, fields):
    """Create an API route for the given model."""
    new_path_api_dir = os.path.join(app_name, API_ROUTE_DIR, model_name, )
    primary_key = fields['primary_key']
    path = os.path.join(new_path_api_dir, f"[{primary_key}].js")
    write_to_file(path, (generate_api_template(model_name, fields).lstrip()))

def main():
    """Main function to generate API routes for each migration file."""
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):  # Filter out non-JavaScript files

            model_name = migration_filename = os.path.join(app_name,
                MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            model_name = table_name
            create_api_route_for_model(model_name, fields)

main()
