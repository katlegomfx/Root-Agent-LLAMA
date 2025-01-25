# Bot\build\code\cli\next\utils\nextBuilder\frontend\home\components\home_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    ensure_folder_exists,
    extract_table_details_from_migration,
    create_view_component,
    read_json_manifest,
    filter_entities_by_role,
    write_to_file,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    app_name
)

def create_public_components():
    # Load the manifest and filter for entities with public page access
    public_access_manifest = read_json_manifest('./am_file.json')
    public_entities = filter_entities_by_role(
        public_access_manifest, 'public_page_view')

    # Process each migration file to create a component if it's marked as a public entity
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            # Extract model details
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            # Check if the table/model is designated for public page generation
            if table_name in public_entities:
                # Generate and save the component
                model_name_cap = table_name.capitalize()
                model_name_low = table_name.lower()
                component_content = create_view_component(
                    table_name, model_name_cap, model_name_low, fields, 'Public')

                # Define the component directory path
                model_public_dir = os.path.join(app_name,
                                                 COMPONENT_DIR, 'home', table_name)

                # Path where the component will be saved
                public_component_path = os.path.join(
                    model_public_dir, f"{model_name_cap}PublicComponent.jsx")

                write_to_file(
                    public_component_path, component_content)

if __name__ == "__main__":
    create_public_components()
