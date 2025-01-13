# utils\nextBuilder\frontend\auth\components\authed_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name   # nopep8

AUTHED_TEMPLATE = """'use client'
import { useEffect } from 'react';
import { getSession } from 'next-auth/react';

import { setPast } from '@/store/states/pastSlice';
import { useSelector, useDispatch } from 'react-redux';
import { useRouter } from 'next/navigation';

export default async function useRedirectIfAuthenticated() {
    const router = useRouter();
    const past = useSelector(state => state.past)
    const dispatch = useDispatch();

    useEffect(() => {
        const checkUserSession = async () => {
            const session = await getSession();

            if (session) {
                router.push(past);
            } else {
                return
            }
        };

        checkUserSession();
    }, [past, router]);
};
"""


def create_flex_gpt_page_file():
    """Generate the flexGPT page file for the Next.js application."""

    flex_gpt_page_path = os.path.join(
        app_name, COMPONENT_DIR, 'authedWrapper.jsx')

    write_to_file(flex_gpt_page_path, AUTHED_TEMPLATE)


if __name__ == "__main__":
    create_flex_gpt_page_file()
