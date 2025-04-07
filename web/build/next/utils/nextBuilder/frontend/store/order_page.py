# Bot\build\code\cli\next\utils\nextBuilder\frontend\store\order_page.py

import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page  # nopep8

def creator_main_page():
    # Template for the Creator Main Page
    flex = """import React from 'react';
import Order from "@/components/store/order";

export default function OrderPage() {
    return (
        <main className="flex min-h-screen items-center justify-center pt-30 p-10 bg-gray-100">
            <div className="w-full max-w-lg">
                <Order />
            </div>
        </main>
    );
}
"""
    create_page('page', flex, subdirectory='store/order')

if __name__ == "__main__":
    creator_main_page()
