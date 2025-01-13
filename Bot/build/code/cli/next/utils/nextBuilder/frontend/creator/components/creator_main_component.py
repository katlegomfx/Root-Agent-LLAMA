# utils\nextBuilder\frontend\creator\components\creator_main_component.py
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


def create_component_creator_page():
    public_access_manifest = read_json_manifest('./am_file.json')
    creator_entities = filter_entities_by_role(
        public_access_manifest, 'creator_page_view')

    # Process migration files to generate links for the creator role
    links = process_migration_files(
        MIGRATIONS_DIR, creator_entities, 'creator')

    main_component_content = generate_main_component_content_with_state(
        links, 'creator')

    creator_component_dir = os.path.join(app_name, COMPONENT_DIR, 'creator')

    creator_component_path = os.path.join(
        creator_component_dir, 'CreatorMainLinks.jsx')

    # Write the generated content to the main creator page file
    write_to_file(creator_component_path, main_component_content)


if __name__ == "__main__":
    create_component_creator_page()
