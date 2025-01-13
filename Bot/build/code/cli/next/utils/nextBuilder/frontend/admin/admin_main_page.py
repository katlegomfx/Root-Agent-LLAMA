# utils\nextBuilder\frontend\admin\admin_main_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def admin_main_page():
    # Template for the Admin Main Page
    flex = """import React from 'react';
import AdminMainLinks from "@/components/admin/AdminMainLinks";

export default function AdminMainPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <h1 className="text-xl font-bold mb-6 text-black">Admin Dashboard</h1>
                <AdminMainLinks />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='admin')


if __name__ == "__main__":
    admin_main_page()
