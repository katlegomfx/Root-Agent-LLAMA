# utils\nextBuilder\frontend\creator\components\creator_interactive_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    ensure_folder_exists,
    create_form_for_entity,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    read_json_manifest,
    filter_entities_by_role,
    extract_table_details_from_migration,
    app_name,

)

# Function to generate interactive components for entities with creator access


def create_creator_interactive_components():
    # Load and filter entities designated for creator access
    public_access_manifest = read_json_manifest('./am_file.json')
    creator_entities = filter_entities_by_role(
        public_access_manifest, 'creator_page_view')

    # Iterate over migration files to generate interactive components for the filtered entities
    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            # Check if the entity is designated for creator access
            if table_name in creator_entities:
                primary_key = fields.get('primary_key')
                if primary_key:
                    # Generate and create a form component for the entity
                    create_form_for_entity(
                        table_name, fields, primary_key, 'Creator', os.path.join(app_name,COMPONENT_DIR))


if __name__ == "__main__":
    create_creator_interactive_components()
