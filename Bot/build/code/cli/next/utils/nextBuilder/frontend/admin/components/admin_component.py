# Bot\build\code\cli\next\utils\nextBuilder\frontend\admin\components\admin_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    extract_table_details_from_migration,
    create_view_component,
    read_json_manifest,
    filter_entities_by_role,
    write_to_file,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    app_name
)

def create_admin_components():
    # Load the manifest and filter for entities with admin page access
    public_access_manifest = read_json_manifest('./am_file.json')
    admin_entities = filter_entities_by_role(
        public_access_manifest, 'admin_page_view')

    # Process each migration file to create a component if it's marked as a admin entity
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            if table_name in admin_entities:
                model_name_cap = table_name.capitalize()
                model_name_low = table_name.lower()
                component_content = create_view_component(
                    table_name, model_name_cap, model_name_low, fields, 'Admin')
                model_admin_dir = os.path.join(app_name,
                                               COMPONENT_DIR, 'admin', table_name)
                admin_component_path = os.path.join(
                    model_admin_dir, f"{model_name_cap}AdminComponent.jsx")

                write_to_file(
                    admin_component_path, component_content)

if __name__ == "__main__":
    create_admin_components()
