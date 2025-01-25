# Bot\build\code\cli\next\utils\nextBuilder\frontend\admin\components\admin_interactive_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    create_form_for_entity,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    read_json_manifest,
    filter_entities_by_role,
    extract_table_details_from_migration,
    app_name,
)

def create_admin_interactive_components():
    # Load and filter entities designated for admin access
    public_access_manifest = read_json_manifest('./am_file.json')
    admin_entities = filter_entities_by_role(
        public_access_manifest, 'admin_page_view')

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)
            if table_name in admin_entities:
                primary_key = fields.get('primary_key')
                if primary_key:
                    create_form_for_entity(
                        table_name, fields, primary_key, 'Admin', os.path.join(app_name, COMPONENT_DIR))

if __name__ == "__main__":
    create_admin_interactive_components()
