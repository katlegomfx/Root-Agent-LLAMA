# utils\nextBuilder\backend\model_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, write_to_file, MIGRATIONS_DIR, API_ROUTE_DIR, app_name  # nopep8


def generate_api_template(model_name):
    model_name_cap = str(model_name)[0].capitalize()+str(model_name)[1:]
    """Generate the API template for the given model."""
    return f"""
import db from '../../../models';  

export default async function handler(req, res) {{
    const {{ method }} = req;

    switch (method) {{
        case 'GET':
            try {{
                await db.sequelize.authenticate();
                const items = await db.{model_name_cap}.findAll();
                res.status(200).json(items);
            }} catch (error) {{
                res.status(500).json({{ error: error.message }});
            }}
            break;
        case 'POST':
            try {{
                const newItem = await db.{model_name_cap}.create(req.body);
                res.status(201).json(newItem);
            }} catch (error) {{
                res.status(500).json({{ error: error.message }});
            }}
            break;
        case 'PUT':
            try {{
                const {{ id }} = req.body;
                await db.{model_name_cap}.update(req.body, {{ where: {{ id }} }});
                res.status(200).json({{ message: '{model_name} updated successfully' }});
            }} catch (error) {{
                res.status(500).json({{ error: error.message }});
            }}
            break;
        case 'DELETE':
            try {{
                const {{ id }} = req.body;
                await db.{model_name_cap}.destroy({{ where: {{ id }} }});
                res.status(200).json({{ message: '{model_name} deleted successfully' }});
            }} catch (error) {{
                res.status(500).json({{ error: error.message }});
            }}
            break;
        default:
            res.setHeader('Allow', ['GET', 'POST', 'PUT', 'DELETE']);
            res.status(405).end(`Method ${{method}} Not Allowed`);
    }}
}}
"""


def create_api_route_for_model(model_name):
    """Create an API route for the given model."""
    new_path_api_dir = os.path.join(app_name, API_ROUTE_DIR, model_name, )
    path = os.path.join(new_path_api_dir, f"index.js")
    write_to_file(path, generate_api_template(model_name).lstrip())


def main():
    """Main function to generate API routes for each migration file."""
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):  # Filter out non-JavaScript files

            model_name = migration_filename = os.path.join(app_name,
                MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            model_name = table_name
            create_api_route_for_model(model_name)


main()
