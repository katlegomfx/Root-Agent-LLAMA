# utils\nextBuilder\frontend\user\user_main_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def user_main_page():
    # Template for the User Main Page
    flex = """import React from 'react';
import UserMainLinks from "@/components/user/UserMainLinks";

export default function UserMainPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <h1 className="text-xl font-bold mb-6 text-black">User</h1>
                <UserMainLinks />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='user')


if __name__ == "__main__":
    user_main_page()
