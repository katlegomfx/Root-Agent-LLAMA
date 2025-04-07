# Bot\build\code\cli\next\utils\nextBuilder\frontend\auth\components\sendForm_component.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

ADMIN_COMPONENT_TEMPLATE = """'use client'
import { useRouter } from 'next/navigation';
import React, { useRef, useEffect } from 'react';
import useRedirectIfAuthenticated from '@/components/authedWrapper';

export default function SendForm() {
    useRedirectIfAuthenticated();
    const router = useRouter();
    // const dispatch = useDispatch();
    const emailRef = useRef(null);

    const handleSendReset = async () => {
        let url = '/api/auth/password/send';
        const data = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 'email': emailRef.current.value }),
        });

        const result = await data.json();
        
        // Check if the request was successful
        if(data.ok) {
            // Navigate to the wait page
            router.push('/auth/password/wait');
        } else {
            // Handle errors or unsuccessful attempts
            console.error('Failed to send password reset:', result.error);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center">
            <div className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <div className="text-center mb-4">
                    <h3 className="font-bold text-xl text-black">Reset Password</h3>
                </div>
                <div className="mb-4">
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        type="email"
                        placeholder="Email"
                        ref={emailRef}
                    />
                </div>
                <div className="flex items-center justify-center">
                    <button
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                        type="button"
                        onClick={handleSendReset}
                    >
                        Send Password Reset
                    </button>
                </div>
            </div>
        </div>
    );
}
"""

def create_component_admin_page():

    admin_component_path = os.path.join(app_name,
        COMPONENT_DIR, 'SendForm.jsx')
    write_to_file(admin_component_path, ADMIN_COMPONENT_TEMPLATE)

if __name__ == "__main__":
    create_component_admin_page()
