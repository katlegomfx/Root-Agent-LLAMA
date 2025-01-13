# utils\nextBuilder\frontend\basic\components\navCart.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the Navbar component
CART_TEMPLATE = """'use client'
import React from 'react';
import { useDispatch, useSelector } from "react-redux";
import { addToCart, removeFromCart, clearCart } from '@/store/states/cartSlice';
import { usePathname } from 'next/navigation';
import Link from 'next/link';
import Image from "next/image";

export default function ShoppingCart() {
    const pathname = usePathname();
    const dispatch = useDispatch();

    const handleAddCart = (item) => {
        dispatch(addToCart(item));
    };
    const handleRemoveCart = (item) => {
        dispatch(removeFromCart(item));
    };
    const handleClearCart = () => {
        dispatch(clearCart());
    };

    const cart = useSelector((state) => state.cart);
    const total = cart.reduce((acc, item) => acc + item.price * item.quantity, 0);

    return (
        <>
            {pathname !== '/shop/checkout' && cart.length > 0 && (
                <div className="relative">
                    <button className="flex items-center justify-center w-12 h-12 rounded-full bg-green-500 text-white">
                        <Image src="/data/image/photos/cart.png" alt="Cart" />
                    </button>
                    <div className="absolute right-0 z-50 w-64 mt-2 bg-green-500 text-white">
                        <div className="p-4">
                            <p>Cart ({cart.length})</p>
                            <ul>
                                {cart.map((item) => (
                                    <li key={item.id} className="flex justify-between items-center py-2">
                                        <span>{item.quantity} {item.name} - R{item.price * item.quantity}</span>
                                        <button onClick={() => handleRemoveCart(item.id)} className="px-2 py-1 text-xs text-red-500 border border-red-500 rounded">
                                            Remove
                                        </button>
                                    </li>
                                ))}
                            </ul>
                            <div className="pt-4 border-t border-white">
                                <p className="mb-2">Total: R{total}</p>
                                <Link href="/shop/cart">
                                    <a className="inline-block px-4 py-2 bg-white text-green-500 rounded">View Cart</a>
                                </Link>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </>
    );
}
"""


# Write the generated content to the Navbar.jsx file
navbar_path = os.path.join(app_name, COMPONENT_DIR, 'cartFeature.jsx')
write_to_file(navbar_path, CART_TEMPLATE)
