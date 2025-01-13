# utils\nextBuilder\backend\siteInfo_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

# Template for the SiteInformation component
SITE_INFORMATION_CONTENT = """'use client'
import { useDispatch, useSelector } from 'react-redux';
import { useEffect } from 'react';
import { setSiteInfo } from '@/store/states/siteInfoSlice';
import { getSession, Session } from 'next-auth/react';
import { RootState } from '@/store';


export default function SiteInformation() {
    const dispatch = useDispatch();
    const siteInfo = useSelector((state) => state.siteInfo);

    useEffect(() => {
        const Process = async () => {
            const session = await getSession();
            try {
                const response = await fetch('https://api.ipify.org?format=json');
                const data = await response.json();

                const userId = session?.user?.id ?? '';
                const clientIP = data.ip || null;  // Ensure clientIP is null if not available
                const platform = navigator.platform;
                const userAgent = navigator.userAgent;
                const appVersion = navigator.appVersion;
                const vendor = navigator.vendor;

                await dispatch(
                    setSiteInfo({
                        clientIP,
                        user: userId,
                        platform,
                        userAgent,
                        appVersion,
                        vendor,
                    })
                );
            } catch (error) {
                const userId = session?.user?.id ?? '';
                const platform = navigator.platform;
                const userAgent = navigator.userAgent;
                const appVersion = navigator.appVersion;
                const vendor = navigator.vendor;

                await dispatch(
                    setSiteInfo({
                        clientIP: siteInfo.clientIP || null,  // Fallback to null if clientIP is undefined
                        user: userId,
                        platform,
                        userAgent,
                        appVersion,
                        vendor,
                    })
                );
            }
        }
        Process();
    }, [dispatch, siteInfo.clientIP]);

    return null;
}
"""

def create_site_information_component():
    create_component('SiteInformation', SITE_INFORMATION_CONTENT)


if __name__ == "__main__":
    create_site_information_component()
