# utils\nextBuilder\frontend\auth\login_page.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import app_name, write_to_file  # nopep8

USER_CONTENT_DIR = "./src/app/auth/login"

# Template for the login page
LOGIN_PAGE_TEMPLATE = """
import LoginForm from '@/components/LoginForm'

export default function LoginPage() {

    return (
        <div className="min-h-screen flex items-center justify-center">
            < LoginForm />
        </div>
    );
}
"""


def create_login_page():
    """Generate the login page for the Next.js application."""

    # Write the generated content to the login.jsx file
    login_page_path = os.path.join(
        app_name, USER_CONTENT_DIR, 'page.jsx')
    write_to_file(login_page_path, LOGIN_PAGE_TEMPLATE)


if __name__ == "__main__":
    create_login_page()
