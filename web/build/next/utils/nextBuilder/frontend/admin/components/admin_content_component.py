# Bot\build\code\cli\next\utils\nextBuilder\frontend\admin\components\admin_content_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    create_react_page_template,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    read_json_manifest,
    filter_entities_by_role,
    extract_table_details_from_migration,
    generate_grid_items,
    write_to_file,
    app_name
)

def create_admin_content_components():
    # Load and filter entities for admin access from the manifest
    public_access_manifest = read_json_manifest('./am_file.json')
    admin_entities = filter_entities_by_role(
        public_access_manifest, 'admin_page_view')

    # Iterate over migration files to generate content components for admin entities
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            if table_name in admin_entities:
                grid_items = generate_grid_items(fields, table_name)
                page_content = create_react_page_template(
                    table_name, 'Admin', grid_items, fields)
                component_path = os.path.join(app_name,
                                              COMPONENT_DIR, 'admin', table_name, f"{table_name.capitalize()}AdminContent.jsx")
                write_to_file(component_path,
                              page_content)

if __name__ == "__main__":
    create_admin_content_components()
