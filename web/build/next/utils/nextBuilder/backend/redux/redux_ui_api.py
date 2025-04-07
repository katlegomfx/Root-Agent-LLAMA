# Bot\build\code\cli\next\utils\nextBuilder\backend\redux\redux_ui_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8

# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from "@reduxjs/toolkit";

const uiSlice = createSlice({
  name: "ui",
  initialState: {
    activeComponent: 'none', // 'none', 'create', 'update'
    activeItem: null, // 'none', 'create', 'update'
  },
  reducers: {
    setActiveComponent: (state, action) => {
      state.activeComponent = action.payload;
    },
    setActiveItem: (state, action) => {
      state.activeItem = action.payload;
    },
    // selectActiveItem: () => {
    // TODO
    // }
  },
});

export const selectActiveItem = (state) => state.ui.activeItem;

export const { setActiveComponent, setActiveItem } = uiSlice.actions;

export const selectUIState = (state) => state.ui;

export default uiSlice.reducer;

"""

if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'uiSlice')
