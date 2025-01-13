# utils\nextBuilder\frontend\user\components\user_content_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    ensure_folder_exists,
    create_react_page_template_without,
    write_to_file,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    read_json_manifest,
    filter_entities_by_role,
    extract_table_details_from_migration,
    generate_grid_items_without,
    app_name
)


def create_user_content_components():
    # Load and filter entities for user access from the manifest
    public_access_manifest = read_json_manifest('./am_file.json')
    user_entities = filter_entities_by_role(
        public_access_manifest, 'user_page_view')

    # Iterate over migration files to generate content components for user entities
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            if table_name in user_entities:
                # Generate the React page template for the entity
                grid_items = generate_grid_items_without(fields, table_name)

                page_content = create_react_page_template_without(
                    table_name, 'User', grid_items, fields)

                # Determine the directory path for the user component
                component_path = os.path.join(app_name,
                                              COMPONENT_DIR, 'user', table_name, f"{table_name.capitalize()}UserContent.jsx")

                write_to_file(
                    component_path, page_content)



if __name__ == "__main__":
    create_user_content_components()
