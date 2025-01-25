# Bot\build\code\cli\next\utils\nextBuilder\backend\redux\redux_nft_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8

# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from "@reduxjs/toolkit"

const nftSlice = createSlice(
    {
        name: 'nft',
        initialState: [],
        reducers: {
            setNft: (state, action) => {
                return action.payload;
            }
        }
    }
)

export const {
    setNft
} = nftSlice.actions
export default nftSlice.reducer
"""

if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'nftSlice')
