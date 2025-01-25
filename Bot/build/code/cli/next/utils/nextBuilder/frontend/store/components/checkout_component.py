# Bot\build\code\cli\next\utils\nextBuilder\frontend\store\components\checkout_component.py

import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the Navbar component
checkout_component_template = """
'use client'
import React, { useState } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { proceedToPayment } from '@/store/actions/checkoutActions';

export default function CheckoutComponent() {
    const dispatch = useDispatch();
    const cart = useSelector(state => state.cart);
    const [formData, setFormData] = useState({
        name: '',
        address: '',
        creditCardNumber: '',
        // Add other fields as necessary
    });

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData(prevState => ({ ...prevState, [name]: value }));
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        dispatch(proceedToPayment(formData));
        // Navigate to confirmation page or handle next steps
    };

    return (
        <form onSubmit={handleSubmit}>
            {/* Form fields for checkout */}
            <input type="text" name="name" value={formData.name} onChange={handleChange} placeholder="Full Name" />
            <input type="text" name="address" value={formData.address} onChange={handleChange} placeholder="Shipping Address" />
            <input type="text" name="creditCardNumber" value={formData.creditCardNumber} onChange={handleChange} placeholder="Credit Card Number" />
            {/* Add other fields as necessary */}
            <button type="submit">Proceed to Payment</button>
        </form>
    );
}
""".strip()

# Write the generated content to the Navbar.jsx file
file_path = os.path.join(app_name, COMPONENT_DIR,
                         'store', 'CheckoutComponent.jsx')
write_to_file(file_path, checkout_component_template)
