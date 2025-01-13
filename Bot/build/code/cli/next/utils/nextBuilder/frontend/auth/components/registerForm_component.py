# utils\nextBuilder\frontend\auth\components\registerForm_component.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the main register page
REGISTER_COMPONENT_TEMPLATE = """'use client'
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signIn, getSession } from 'next-auth/react';
import useRedirectIfAuthenticated from './authedWrapper';

export default function RegistrationForm() {
    useRedirectIfAuthenticated()
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [confirmPassword, setConfirmPassword] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (password !== confirmPassword) {
            console.error("Passwords don't match!");
            return;
        }

        try {
            const view = await signIn('credential',
                {
                    redirect: false,
                    'username': username,
                    'email': email,
                    'password': password,
                    'type': 'register',
                    callbackUrl: '/auth/login'
                }
            )

            if (!view.ok) {
                return
            } else {
                router.push(view.url);
            }

        } catch (error) {
            return
        }
    };

    return (
            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <h1 className="text-2xl font-bold text-center mb-6">Register</h1>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="username">
                        Username
                    </label>
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        id="username"
                        type="text"
                        placeholder="Username"
                        value={username}
                        onChange={(e) => setUsername(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="email">
                        Email
                    </label>
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        id="email"
                        type="email"
                        placeholder="Email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                    />
                </div>
                <div className="mb-4">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                        Password
                    </label>
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        id="password"
                        type="password"
                        placeholder="Password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                <div className="mb-6">
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="confirmPassword">
                        Confirm Password
                    </label>
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 leading-tight focus:outline-none focus:shadow-outline"
                        id="confirmPassword"
                        type="password"
                        placeholder="Confirm Password"
                        value={confirmPassword}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                    />
                </div>
                <div className="flex items-center justify-between">
                    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        Register
                    </button>
                    <a href="/auth/login" className="ml-4 inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                        Already have an account?
                    </a>
                </div>
            </form>
    );
}
"""


def create_component_register_page():

    register_component_path = os.path.join(app_name,
                                           COMPONENT_DIR, 'RegisterForm.jsx')
    write_to_file(register_component_path, REGISTER_COMPONENT_TEMPLATE)

if __name__ == "__main__":
    create_component_register_page()
