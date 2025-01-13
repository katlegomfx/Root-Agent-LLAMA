# utils\nextBuilder\frontend\store\components\productView_component.py

import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

product_view_component_template = """
'use client'
import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom'; // Assuming you're using React Router for routing

export default function ProductViewComponent() {
    const { productId } = useParams();
    const [product, setProduct] = useState(null);

    useEffect(() => {
        async function fetchProduct() {
            // Fetch a single product logic
            const response = await fetch(`/api/products/${productId}`);
            const data = await response.json();
            setProduct(data);
        }
        fetchProduct();
    }, [productId]);

    if (!product) return <p>Loading...</p>;

    return (
        <div>
            <h1>{product.name}</h1>
            {/* Display product details */}
        </div>
    );
}
""".strip()

# Write the generated content to the ProductViewComponent.jsx file
file_path = os.path.join(app_name, COMPONENT_DIR,
                         'store', 'ProductViewComponent.jsx')
write_to_file(file_path, product_view_component_template)
