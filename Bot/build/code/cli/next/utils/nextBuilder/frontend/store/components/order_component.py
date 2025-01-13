# utils\nextBuilder\frontend\store\components\order_component.py

import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

order_component_template = """
'use client'
import React, { useEffect, useState } from 'react';
import { fetchOrderDetails } from '@/store/actions/orderActions';
import { useSelector, useDispatch } from 'react-redux';

export default function OrderComponent({ orderId }) {
    const dispatch = useDispatch();
    const orderDetails = useSelector(state => state.order.orderDetails);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        async function loadOrderDetails() {
            await dispatch(fetchOrderDetails(orderId));
            setIsLoading(false);
        }
        loadOrderDetails();
    }, [dispatch, orderId]);

    if (isLoading) return <p>Loading...</p>;

    return (
        <div>
            {/* Display order details */}
            <h1>Order Details</h1>
            {/* Implement the display of order details */}
        </div>
    );
}
""".strip()

# Write the generated content to the OrderComponent.jsx file
file_path = os.path.join(app_name, COMPONENT_DIR,
                         'store', 'OrderComponent.jsx')
write_to_file(file_path, order_component_template)
