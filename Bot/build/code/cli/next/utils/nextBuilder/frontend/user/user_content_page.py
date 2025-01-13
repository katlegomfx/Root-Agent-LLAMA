# utils\nextBuilder\frontend\user\user_content_page.py
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

CREATOR_UI_DIR = "./src/app/user"


def create_user_card_template(model_name, model_name_cap, model_name_low, fields):
    """Generates a React page template for a given model."""

    flex = f"""import {model_name_cap}UserComponent from '@/components/user/{model_name}/{model_name_cap}UserComponent'

export default function {model_name_cap}UserPage() {{

    return (
    <>
        <{model_name_cap}UserComponent />
    </>
    );
}}
"""
    return flex


def create_user_main_page_for_model(model_name, fields):
    """Creates a main page for a model under the user UI directory."""

    model_name_cap = model_name.capitalize()
    model_name_low = model_name.lower()
    page_content = create_user_card_template(
        model_name, model_name_cap, model_name_low, fields)

    subdirectory = os.path.join("user", model_name)

    create_page("page",
                page_content, subdirectory=subdirectory)


def main():
    """Main function to generate the User UI Main Page for each migration file."""
    public_access_manifest = read_json_manifest('./am_file.json')

    user_entities = filter_entities_by_role(
        public_access_manifest, 'user_page_view')

    for migration_file in os.listdir(os.path.join(app_name, MIGRATIONS_DIR)):
        if migration_file.endswith(".js"):
            migration_filename = os.path.join(
                app_name, MIGRATIONS_DIR, migration_file)
            table_name, fields = extract_table_details_from_migration(
                migration_filename)

            if table_name in user_entities:
                create_user_main_page_for_model(table_name, fields)


if __name__ == "__main__":
    main()
