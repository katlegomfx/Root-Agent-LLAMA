# Bot\build\code\cli\next\utils\nextBuilder\frontend\home\home_main_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8

def public_main_page():
    # Template for the Public Main Page
    flex = """import React from 'react';
import PublicMainLinks from "@/components/home/PublicMainLinks";

export default function PublicMainPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <PublicMainLinks />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='home')

if __name__ == "__main__":
    public_main_page()
