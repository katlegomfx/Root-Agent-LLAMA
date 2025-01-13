# utils\nextBuilder\backend\redux\redux_past_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8


# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from "@reduxjs/toolkit"

const pastSlice = createSlice(
    {
        name: 'past',
        initialState: [],
        reducers: {
            setPast: (state, action) => {
                return action.payload;
            }
        }
    }
)

export const {
    setPast
} = pastSlice.actions
export default pastSlice.reducer
"""


if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'pastSlice')
