# Bot\build\code\cli\next\utils\nextBuilder\backend\date_utils_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import extract_table_details_from_migration, write_to_file, MIGRATIONS_DIR, UTILS_DIR, app_name  # nopep8

# Template for the latest date utility function
LATEST_DATE_UTILS_TEMPLATE = """
/**
 * Fetch the latest date.
 */
export const fetchLatestDate = async () => {{
    try {{
        const response = await fetch('http://localhost:3000/api/date');
        const data = await response.json();
        return data;
    }} catch (error) {{
        console.error("Failed to fetch the latest date.", error);
        return null;
    }}
}}
"""

def create_latest_date_utils():
    """Create a utility function for fetching the latest date."""
    utils_content = LATEST_DATE_UTILS_TEMPLATE.lstrip()

    write_to_file(os.path.join(app_name, UTILS_DIR, "date.js"), utils_content)

def main():
    """Main function to generate utility functions for each migration file and the latest date."""
    # Generate the latest date utility function
    create_latest_date_utils()

if __name__ == "__main__":
    main()
