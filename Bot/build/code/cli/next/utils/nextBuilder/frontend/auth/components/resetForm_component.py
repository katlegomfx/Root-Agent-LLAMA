# utils\nextBuilder\frontend\auth\components\resetForm_component.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

ADMIN_COMPONENT_TEMPLATE = """'use client'
import React from 'react';
import { useRouter, useSearchParams } from 'next/navigation';
import { useRef, useEffect } from 'react';
import { signIn, getSession } from 'next-auth/react';
import useRedirectIfAuthenticated from '@/components/authedWrapper';

import { useSelector, useDispatch } from 'react-redux';

export default function ResetForm() {
    useRedirectIfAuthenticated();
    const dispatch = useDispatch();
    const router = useRouter();
    const searchParams = useSearchParams()
    const token = searchParams.get('token')

    const emailRef = useRef(null);
    const passwordRef = useRef(null);
    const confirmPasswordRef = useRef(null);

    const handleReset = async () => {

        const data = await fetch('/api/auth/password/reset', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                'token': token,
                'email': emailRef.current.value,
                'password': passwordRef.current.value,
                'password_confirmation': confirmPasswordRef.current.value,
            }),
        });

        if (data.status) {
            router.push('/auth/login')
        }
        // else {
        //     // console.log(data)
        // }
    }

    return (
        <form className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
            <h1 className="text-2xl font-bold text-center mb-6">Reset Password</h1>
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="login-email">
                    Email
                </label>
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                    id="login-email"
                    type="email"
                    placeholder="Email"
                    ref={emailRef}
                />
            </div>
            <div className="mb-4">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="register-password">
                    Password
                </label>
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                    id="register-password"
                    type="password"
                    placeholder="Password"
                    ref={passwordRef}
                />
            </div>
            <div className="mb-6">
                <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="register-confirm-password">
                    Confirm Password
                </label>
                <input
                    className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                    id="register-confirm-password"
                    type="password"
                    placeholder="Confirm Password"
                    ref={confirmPasswordRef}
                />
            </div>
            <div className="flex items-center justify-between">
                <button
                    className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline"
                    type="button"
                    onClick={handleReset}
                >
                    Reset Password
                </button>
            </div>
        </form>
    );
}
"""


def create_component_admin_page():

    admin_component_path = os.path.join(app_name,
                                        COMPONENT_DIR, 'ResetForm.jsx')
    write_to_file(admin_component_path, ADMIN_COMPONENT_TEMPLATE)


if __name__ == "__main__":
    create_component_admin_page()
