# utils\nextBuilder\backend\redux\redux_delivery_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8


# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from "@reduxjs/toolkit"

const deliverySlice = createSlice(
    {
        name: 'delivery',
        initialState: [],
        reducers: {
            setDelivery: (state, action) => {
                return action.payload;
            }
        }
    }
)

export const {
    setDelivery
} = deliverySlice.actions
export default deliverySlice.reducer
"""


if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'deliverySlice')
