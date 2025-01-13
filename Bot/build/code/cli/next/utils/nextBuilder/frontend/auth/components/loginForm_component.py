# utils\nextBuilder\frontend\auth\components\loginForm_component.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the main login page
LOGIN_COMPONENT_TEMPLATE = """'use client'
import React, { useState } from 'react';
import { useRouter } from 'next/navigation';
import { signIn, getSession } from 'next-auth/react';
import { useSelector } from 'react-redux';
import useRedirectIfAuthenticated from './authedWrapper';

export default function LoginComponent() {
    useRedirectIfAuthenticated()
    const past = useSelector(state => state.past)
    const router = useRouter();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [loginError, setLoginError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoginError('');
        try {
            const view = await signIn('credential',
                {
                    redirect: false,
                    'username': username,
                    'password': password,
                    // 'remember': rememberMeRef.current.value,
                    'type': 'login',
                    callbackUrl: `${past}`

                }
            )

            if (view.error) {
                if (view?.error === "CredentialsSignin") {
                    setLoginError("Incorrect username or password");
                } else {
                    setLoginError(view.error);
                }
            } else {
                router.push(view.url || '/user');
            }

        } catch (error) {
            setLoginError('An unexpected error occurred');
        }
    };

    return (
            <form onSubmit={handleSubmit} className="bg-white shadow-md rounded px-8 pt-6 pb-8 mb-4">
                <h1 className="text-2xl font-bold text-center mb-6">Login</h1>
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
                    <label className="block text-gray-700 text-sm font-bold mb-2" htmlFor="password">
                        Password
                    </label>
                    <input
                        className="shadow appearance-none border rounded w-full py-2 px-3 text-gray-700 mb-3 leading-tight focus:outline-none focus:shadow-outline"
                        id="password"
                        type="password"
                        placeholder="******************"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                    />
                </div>
                {loginError && <p className="text-red-500">{loginError}</p>}
                <div className="flex items-center justify-between mb-2">
                    <button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded focus:outline-none focus:shadow-outline" type="submit">
                        Sign In
                    </button>
                    <a href="/auth/register" className="ml-4 inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                        Don&apos;t have an account?
                    </a>
                </div>
                <div className="flex items-center justify-between">
                    <a href="/auth/password/send" className="inline-block align-baseline font-bold text-sm text-blue-500 hover:text-blue-800">
                        Forgot Password?
                    </a>
                </div>
            </form>
    );
}
"""


def create_component_login_page():

    login_component_path = os.path.join(app_name,
                                        COMPONENT_DIR, 'LoginForm.jsx')
    write_to_file(login_component_path, LOGIN_COMPONENT_TEMPLATE)


if __name__ == "__main__":
    create_component_login_page()
