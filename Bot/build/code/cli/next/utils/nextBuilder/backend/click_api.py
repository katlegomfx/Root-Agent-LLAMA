# utils\nextBuilder\backend\click_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

# Template for the ClickWrapper component
clickWrapperJSContent = """'use client'
import { useState, ReactNode } from 'react';
import { useSelector } from 'react-redux';
import { useRouter } from 'next/navigation';
import { RootState } from '@/store';  // Adjust the import path according to your file structure



const ClickWrapper = ({ children }) => {
    const [clicked, setClicked] = useState('');
    const router = useRouter();
    const geolocation = useSelector((state) => state.geolocation);
    const siteInfo = useSelector((state) => state.siteInfo);

    const sendLog = async () => {
        const endedLike = await fetch('/api/auditTrails', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({

                user_id: siteInfo.user,
                visitor_id: siteInfo.user,
                machineAddress: siteInfo.clientIP,
                platform: siteInfo.platform,
                userAgent: siteInfo.userAgent,
                appVersion: siteInfo.appVersion,
                vendor: siteInfo.vendor,
                latitude: geolocation.position.latitude,
                longitude: geolocation.position.longitude,
                current_url: router.pathname,
                previous_url: document.referrer,
                action: clicked,
                description: clicked

            })
        });
        const result = await endedLike.json();
        // console.log(result);
    };

    const handleClick = async (event) => {
        const target = event.target;
        setClicked(target.innerText);
        sendLog();
    };

    return <div onClick={handleClick}>{children}</div>;
};

export default ClickWrapper;
"""


def create_click_wrapper_component():
    component_name = 'ClickWrapper'  # Name of your component
    create_component(component_name, clickWrapperJSContent, 'jsx')

if __name__ == "__main__":
    create_click_wrapper_component()
