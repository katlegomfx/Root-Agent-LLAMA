# Bot\build\code\cli\next\utils\nextBuilder\frontend\auth\reset_page.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import app_name, write_to_file  # nopep8

USER_CONTENT_DIR = "./src/app/auth/password/reset"

REGISTRATION_PAGE_TEMPLATE = """import ResetForm from '@/components/ResetForm'

export default function Page() {

    return (
            <div className="min-h-screen flex items-center justify-center">
                <ResetForm />
            </div>
        )
}
"""

def create_registration_page():
    """Generate the registration page for the Next.js application."""

    registration_page_path = os.path.join(
        app_name, USER_CONTENT_DIR, 'page.jsx')
    write_to_file(registration_page_path, REGISTRATION_PAGE_TEMPLATE)

if __name__ == "__main__":
    create_registration_page()
