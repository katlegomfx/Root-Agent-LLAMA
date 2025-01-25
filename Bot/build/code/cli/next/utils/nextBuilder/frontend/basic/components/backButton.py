# Bot\build\code\cli\next\utils\nextBuilder\frontend\basic\components\backButton.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import COMPONENT_DIR, app_name, write_to_file  # nopep8

# Template for the back button
BACKBUTTON_TEMPLATE = """// src\components\goBack.jsx
'use client'
import { usePathname } from 'next/navigation';
import { getSession } from 'next-auth/react';
import { useState, useEffect } from 'react';

const RenderObject = ({ obj }) => {
    return (
        <div>
            {Object.entries(obj).map(([key, value]) => {
                // Check if the value is an object and not null or an array
                if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
                    // Recursively render nested objects
                    return (
                        <div key={key}>
                            <strong>{key}:</strong>
                            <div style={{ marginLeft: '20px' }}>
                                <RenderObject obj={value} />
                            </div>
                        </div>
                    );
                } else {
                    // For direct properties, display them as key-value pairs
                    return (
                        <div key={key}>
                            <strong>{key}:</strong> {String(value)}
                        </div>
                    );
                }
            })}
        </div>
    );
};

export default function BackButton() {
    const pathname = usePathname();
    const [currSession, setCurrSession] = useState({})

    useEffect(() => {
        const checkUserSession = async () => {
            const session = await getSession();

            setCurrSession(session)
        };

        checkUserSession();
    }, []);

    return (
        <div className={`container mx-auto px-4 ${pathname !== "/" ? "mt-4" : ""}`}>
            {pathname !== "/" && (
                <div className="flex items-center justify-start">
                    <button
                        onClick={() => window.history.back()}
                        className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
                        id='back-btn'
                    >
                        {"<"} Back
                    </button>
                    {currSession && (
                        <div className="ml-4 text-white">
                            {currSession && (
                                <div className="ml-4 text-white">
                                    <RenderObject obj={currSession} />
                                </div>
                            )}
                        </div>
                    )}
                    {pathname}

                </div>
            )}
            <div className="mt-4"></div>
        </div>
    );
}
"""

def create_back_button_component():
    """Generate the back button component for the Next.js application."""
    # Write the generated content to the goBack.jsx file
    back_button_path = os.path.join(app_name, COMPONENT_DIR, 'goBack.jsx')
    write_to_file(back_button_path, BACKBUTTON_TEMPLATE)

if __name__ == "__main__":
    create_back_button_component()
