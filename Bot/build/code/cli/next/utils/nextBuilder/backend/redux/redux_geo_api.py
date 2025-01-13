# utils\nextBuilder\backend\redux\redux_geo_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_reducer_js  # nopep8


# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { createSlice } from '@reduxjs/toolkit';

const initialState = {
  position: {
    latitude: null,
    longitude: null,
  },
  loading: 'idle',
};

const geolocationSlice = createSlice({
  name: 'geolocation',
  initialState,
  reducers: {
    setPosition: (state, action) => {
      state.position = action.payload;
    },
  },
});

export const { setPosition } = geolocationSlice.actions;

export default geolocationSlice.reducer;
"""


if __name__ == "__main__":
    create_redux_reducer_js(STORE_INDEX_TEMPLATE, 'geolocationSlice')
