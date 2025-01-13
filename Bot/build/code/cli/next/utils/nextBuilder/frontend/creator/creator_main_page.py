# utils\nextBuilder\frontend\creator\creator_main_page.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def creator_main_page():
    # Template for the Creator Main Page
    flex = """import React from 'react';
import CreatorMainLinks from "@/components/creator/CreatorMainLinks";

export default function CreatorMainPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <h1 className="text-xl font-bold mb-6 text-black">Creator Dashboard</h1>
                <CreatorMainLinks />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='creator')


if __name__ == "__main__":
    creator_main_page()
