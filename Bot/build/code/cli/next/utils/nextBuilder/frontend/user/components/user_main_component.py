# utils\nextBuilder\frontend\user\components\user_main_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    ensure_folder_exists,
    process_migration_files,
    generate_main_component_content_with_state,
    write_to_file,
    read_json_manifest,
    filter_entities_by_role,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    app_name
)


def create_component_user_page():
    public_access_manifest = read_json_manifest('./am_file.json')
    user_entities = filter_entities_by_role(
        public_access_manifest, 'user_page_view')

    # Process migration files to generate links for the user role
    links = process_migration_files(
        MIGRATIONS_DIR, user_entities, 'user')

    main_component_content = generate_main_component_content_with_state(
        links, 'user')

    user_component_dir = os.path.join(app_name, COMPONENT_DIR, 'user')

    user_component_path = os.path.join(
        user_component_dir, 'UserMainLinks.jsx')

    # Write the generated content to the main user page file
    write_to_file(user_component_path, main_component_content)


if __name__ == "__main__":
    create_component_user_page()
