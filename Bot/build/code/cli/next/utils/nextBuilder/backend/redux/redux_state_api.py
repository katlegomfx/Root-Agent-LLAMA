# Bot\build\code\cli\next\utils\nextBuilder\backend\redux\redux_state_api.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_redux_store_js  # nopep8

# Template for the store index component
STORE_INDEX_TEMPLATE = """
import { combineReducers, configureStore } from "@reduxjs/toolkit";
import storage from "redux-persist/lib/storage";
import { persistReducer, persistStore } from "redux-persist";

import cartReducer from "@/store/states/cartSlice";
import nftReducer from "@/store/states/nftSlice";
import deliveryReducer from "@/store/states/deliverySlice";

import pastReducer from "@/store/states/pastSlice";
import uiReducer from "@/store/states/uiSlice";
import geolocationReducer from "@/store/states/geolocationSlice";
import siteInfoReducer from "@/store/states/siteInfoSlice";

const persistConfig = {
    key: 'root',
    storage
};

const rootReducer = combineReducers({
    cart: cartReducer,
    nft: nftReducer,
    delivery: deliveryReducer,

    past: pastReducer,
    ui: uiReducer,
    geolocation: geolocationReducer,
    siteInfo: siteInfoReducer,
});

const persistedReducer = persistReducer(persistConfig, rootReducer);

export const store = configureStore({
    reducer: persistedReducer,
    devTools: true,
    // middleware: getDefaultMiddleware({
    //     serializableCheck: false,
    // }),
});

export const RootState = store.getState;
export const AppDispatch = store.dispatch;

export const persistor = persistStore(store);
"""

if __name__ == "__main__":
    create_redux_store_js(STORE_INDEX_TEMPLATE)
