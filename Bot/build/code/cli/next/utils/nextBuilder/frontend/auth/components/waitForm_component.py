# utils\nextBuilder\frontend\auth\components\waitForm_component.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

ADMIN_COMPONENT_TEMPLATE = """'use client'
import React, { useEffect } from 'react';

import useRedirectIfAuthenticated from '@/components/authedWrapper';
import Link from 'next/link';

export default function WaitForm() {
    useRedirectIfAuthenticated();

    return (
        <div className="flex flex-col items-center justify-center h-screen">
            <p className="text-center text-lg mt-4">
                Wait for an email sent to the mailbox you provided
            </p>
        </div>
    );
}

"""


def create_component_admin_page():


    admin_component_path = os.path.join(app_name,
                                        COMPONENT_DIR, 'WaitForm.jsx')
    write_to_file(admin_component_path, ADMIN_COMPONENT_TEMPLATE)


if __name__ == "__main__":
    create_component_admin_page()
