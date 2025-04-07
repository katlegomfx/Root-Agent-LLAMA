# Bot\build\code\cli\next\utils\nextBuilder\backend\redux\redux_siteInfo_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8

# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
    clientIP: null,
    platform: '',
    userAgent: '',
    appVersion: '',
    vendor: '',
    loading: 'idle',
};

const siteInfoSlice = createSlice({
    name: 'siteInfo',
    initialState,
    reducers: {
        setSiteInfo: (state, action) => {
            state.clientIP = action.payload.clientIP;
            state.platform = action.payload.platform;
            state.userAgent = action.payload.userAgent;
            state.appVersion = action.payload.appVersion;
            state.vendor = action.payload.vendor;
        },
    },
});

export const { setSiteInfo } = siteInfoSlice.actions;

export default siteInfoSlice.reducer;
"""

if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'siteInfoSlice')
