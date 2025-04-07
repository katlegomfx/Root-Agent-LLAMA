# Bot\build\code\cli\next\utils\nextBuilder\frontend\auth\components\deauth_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

DEAUTH_TEMPLATE = """'use client'
import { useEffect } from 'react';
import { getSession } from 'next-auth/react';
import { useRouter, usePathname } from 'next/navigation';

export default function useRedirectIfUnauthenticated() {
    const router = useRouter();
    const pathname = usePathname();

    useEffect(() => {
        const checkUserSession = async () => {
            const session = await getSession();

            if (!session) {
                // No session found, redirect to login page
                router.push('/auth/login');
                return;
            }

            // Extract role from session
            const { role } = session?.user?.info || {};

            // Define allowed access for each role
            const allowedAccess = {
                Admin: ['/admin', '/user', '/creator'],
                Creator: ['/creator', '/user'],
                Regular: ['/user'],
            };

            // Determine if the current path is allowed for the user's role
            const isAllowedToAccess = allowedAccess[role]?.some(allowedPath => pathname.startsWith(allowedPath));

            if (!isAllowedToAccess) {
                // If the user's role does not allow accessing the current path, redirect to the base path of their role
                const basePathForRole = {
                    Admin: '/admin',
                    Creator: '/creator',
                    Regular: '/user',
                }[role] || '/'; // Default redirect if role is unrecognized

                router.push(basePathForRole);
                return;
            }
        };

        checkUserSession();
    }, [router, pathname]);
}
"""

def create_flex_gpt_page_file():
    """Generate the flexGPT page file for the Next.js application."""

    flex_gpt_page_path = os.path.join(
        app_name, COMPONENT_DIR, 'deauthedWrapper.jsx')

    write_to_file(flex_gpt_page_path, DEAUTH_TEMPLATE)

if __name__ == "__main__":
    create_flex_gpt_page_file()
