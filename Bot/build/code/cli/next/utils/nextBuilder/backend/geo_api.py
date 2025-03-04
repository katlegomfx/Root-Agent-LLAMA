# Bot\build\code\cli\next\utils\nextBuilder\backend\geo_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

# Template for the GeoLocationLogger component
GEOLOCATION_COMPONENT_JS_CONTENT = """'use client'
import { useSelector, useDispatch } from 'react-redux';
import { useEffect } from 'react';
import { setPosition } from '@/store/states/geolocationSlice';

const logLocation = (dispatch) => {
    const getLocation = () => {
        if (navigator.geolocation) {
            navigator.geolocation.watchPosition(showPosition);
        } else {
            console.log('Geolocation is not supported by this browser.');
        }
    };

    const showPosition = async (position) => {
        // console.log('Latitude: ' + position.coords.latitude);
        // console.log('Longitude: ' + position.coords.longitude);

        await dispatch(
            setPosition({
                latitude: position.coords.latitude,
                longitude: position.coords.longitude,
            })
        );
    };

    getLocation();
};

const GeoLocationLogger = () => {
    const dispatch = useDispatch();

    useEffect(() => {
        logLocation(dispatch);
        const clickHandler = () => logLocation(dispatch);
        window.addEventListener('click', clickHandler);

        return () => {
            window.removeEventListener('click', clickHandler);
        };
    }, [dispatch]); // Add dispatch to the dependency array

    return null;
};

export default GeoLocationLogger;
"""

# Function to create the Geolocation component in JavaScript
def create_geolocation_component_js():
    create_component('GeoLocationLogger', GEOLOCATION_COMPONENT_JS_CONTENT)

if __name__ == "__main__":
    create_geolocation_component_js()
