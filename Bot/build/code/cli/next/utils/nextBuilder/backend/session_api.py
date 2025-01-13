# utils\nextBuilder\backend\session_api.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component   # nopep8

# Template for the SessionWrapper component
SESSION_WRAPPER_CONTENT = """\"use client\";
import { SessionProvider } from \"next-auth/react\"
import { Provider } from \"react-redux\";

import { store } from '@/store'

import React from 'react'

const SessionWrapper = ({ children }) => {
    return (
        <Provider store={store}>
            <SessionProvider>{children}</SessionProvider>
        </Provider>
    )
}

export default SessionWrapper
"""


def create_session_wrapper_component():
    create_component('SessionWrapper', SESSION_WRAPPER_CONTENT)


if __name__ == "__main__":
    create_session_wrapper_component()
