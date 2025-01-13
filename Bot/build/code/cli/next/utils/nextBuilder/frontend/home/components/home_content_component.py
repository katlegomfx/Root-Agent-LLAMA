# utils\nextBuilder\frontend\home\components\home_content_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    ensure_folder_exists,
    create_react_page_template,
    write_to_file,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    read_json_manifest,
    filter_entities_by_role,
    extract_table_details_from_migration,
    generate_grid_items,
    app_name
)


def create_public_content_components():
    # Load and filter entities for public access from the manifest
    public_access_manifest = read_json_manifest('./am_file.json')
    public_entities = filter_entities_by_role(
        public_access_manifest, 'public_page_view')

    # Iterate over migration files to generate content components for public entities
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            if table_name in public_entities:
                # Generate the React page template for the entity
                grid_items = generate_grid_items(fields, table_name)

                page_content = create_react_page_template(
                    table_name, 'Public', grid_items, fields)

                # Determine the directory path for the public component
                component_path = os.path.join(app_name,
                                              COMPONENT_DIR, 'home', table_name, f"{table_name.capitalize()}PublicContent.jsx")

                write_to_file(
                    component_path, page_content)


if __name__ == "__main__":
    create_public_content_components()
