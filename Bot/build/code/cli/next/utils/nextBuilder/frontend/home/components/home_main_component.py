# utils\nextBuilder\frontend\home\components\home_main_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    process_migration_files,
    generate_main_component_content_with_state,
    generate_main_component_content_without,
    write_to_file,
    read_json_manifest,
    filter_entities_by_role,
    MIGRATIONS_DIR,
    COMPONENT_DIR,
    app_name
)


def create_component_public_page():
    public_access_manifest = read_json_manifest('./am_file.json')
    public_entities = filter_entities_by_role(
        public_access_manifest, 'public_page_view')

    # Process migration files to generate links for the public role
    links = process_migration_files(
        MIGRATIONS_DIR, public_entities, 'home')

    main_component_content = generate_main_component_content_without(
        links, 'home')

    public_component_dir = os.path.join(app_name, COMPONENT_DIR, 'home')

    public_component_path = os.path.join(
        public_component_dir, 'PublicMainLinks.jsx')

    # Write the generated content to the main public page file
    write_to_file(public_component_path, main_component_content)


if __name__ == "__main__":
    create_component_public_page()
