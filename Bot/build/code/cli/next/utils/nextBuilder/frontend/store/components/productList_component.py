# Bot\build\code\cli\next\utils\nextBuilder\frontend\store\components\productList_component.py

import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

product_list_component_template = """
'use client'
import React, { useEffect, useState } from 'react';
import ProductCard from './ProductCard'; // Assume you have a ProductCard component

export default function ProductListComponent() {
    const [products, setProducts] = useState([]);

    useEffect(() => {
        async function fetchProducts() {
            // Fetch products logic
            const response = await fetch('/api/products');
            const data = await response.json();
            setProducts(data);
        }
        fetchProducts();
    }, []);

    return (
        <div className="grid grid-cols-3 gap-4">
            {products.map(product => (
                <ProductCard key={product.id} product={product} />
            ))}
        </div>
    );
}
""".strip()

# Write the generated content to the ProductListComponent.jsx file
file_path = os.path.join(app_name, COMPONENT_DIR,
                         'store', 'ProductListComponent.jsx')
write_to_file(file_path, product_list_component_template)
