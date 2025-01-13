# utils\nextBuilder\frontend\creator\creator_content_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    extract_table_details_from_migration,
    read_json_manifest,
    filter_entities_by_role,
    create_page,
    MIGRATIONS_DIR,
    app_name
)

CREATOR_UI_DIR = "./src/app/creator"


def create_creator_card_template(model_name, model_name_cap, model_name_low, fields):
    """Generates a React page template for a given model."""

    flex = f"""import {model_name_cap}CreatorComponent from '@/components/creator/{model_name}/{model_name_cap}CreatorComponent'

export default function {model_name_cap}CreatorPage() {{

    return (
    <>
        <{model_name_cap}CreatorComponent />
    </>
    );
}}
"""
    return flex


def create_creator_main_page_for_model(model_name, fields):
    """Creates a main page for a model under the creator UI directory."""

    model_name_cap = model_name.capitalize()
    model_name_low = model_name.lower()
    page_content = create_creator_card_template(
        model_name, model_name_cap, model_name_low, fields)

    subdirectory = os.path.join("creator", model_name)

    create_page("page",
                page_content, subdirectory=subdirectory)


def main():
    """Main function to generate the Creator UI Main Page for each migration file."""
    public_access_manifest = read_json_manifest('./am_file.json')

    creator_entities = filter_entities_by_role(
        public_access_manifest, 'creator_page_view')

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            if table_name in creator_entities:
                create_creator_main_page_for_model(table_name, fields)


if __name__ == "__main__":
    main()
