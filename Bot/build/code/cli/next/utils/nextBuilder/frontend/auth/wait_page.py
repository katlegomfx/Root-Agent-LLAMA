# utils\nextBuilder\frontend\auth\wait_page.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, app_name  # nopep8

USER_CONTENT_DIR = "./src/app/auth/password/wait"

REGISTRATION_PAGE_TEMPLATE = """import WaitForm from '@/components/WaitForm'

export default function Page() {

    return (
            <div className="min-h-screen flex items-center justify-center">
                <WaitForm />
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
