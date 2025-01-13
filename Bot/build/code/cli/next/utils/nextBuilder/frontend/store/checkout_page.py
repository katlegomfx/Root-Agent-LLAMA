# utils\nextBuilder\frontend\store\checkout_page.py

import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8


def creator_main_page():
    # Template for the Creator Main Page
    flex = """import React from 'react';
import CheckoutComponent from "@/components/store/CheckoutComponent";

export default function CheckoutPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <CheckoutComponent />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='store/checkout')


if __name__ == "__main__":
    creator_main_page()
