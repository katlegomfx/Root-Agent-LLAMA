# utils\nextBuilder\frontend\admin\components\admin_main_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    process_migration_files,
    generate_main_component_content_with_state,
    write_to_file,
    read_json_manifest,
    filter_entities_by_role,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    app_name
)


def create_component_admin_page():
    public_access_manifest = read_json_manifest('./am_file.json')
    admin_entities = filter_entities_by_role(
        public_access_manifest, 'admin_page_view')

    # Process migration files to generate links for the admin role
    links = process_migration_files(
        MIGRATIONS_DIR, admin_entities, 'admin')

    main_component_content = generate_main_component_content_with_state(links, 'admin')

    admin_component_dir = os.path.join(app_name, COMPONENT_DIR, 'admin')

    admin_component_path = os.path.join(
        admin_component_dir, 'AdminMainLinks.jsx')

    # Write the generated content to the main admin page file
    write_to_file(admin_component_path, main_component_content)


if __name__ == "__main__":
    create_component_admin_page()
