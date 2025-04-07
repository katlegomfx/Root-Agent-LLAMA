# Bot\build\code\cli\next\utils\nextBuilder\backend\redux\redux_cart_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8

# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from "@reduxjs/toolkit"

const cartSlice = createSlice(
    {
        name: 'cart',
        initialState: [],
        reducers: {
            addToCart: (state, action) => {
                const itemIndex = state.findIndex(item => item.id === action.payload.id);
                if (itemIndex > -1) {
                    state[itemIndex].quantity += action.payload.quantity;
                } else {
                    state.push(action.payload);
                }
            },
            removeFromCart: (state, action) => {
                return state.filter(item => item.id !== action.payload)
            },
            clearCart: () => {
                return []
            }
        }
    }
)

export const {
    addToCart,
    removeFromCart,
    clearCart
} = cartSlice.actions
export default cartSlice.reducer
"""

if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'cartSlice')
