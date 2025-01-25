# Bot\build\code\cli\next\utils\nextBuilder\frontend\basic\components\navbar.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the Navbar component
NAVBAR_TEMPLATE = """'use client'
import { useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { useSession, signIn, signOut } from "next-auth/react";
import ShoppingCart from '@/components/cartFeature'

export default function Navbar({ site, menu }) {
  const [isNavOpen, setIsNavOpen] = useState(false);
  const { data: session } = useSession();

  const logoPath = site[0].site_logo.startsWith('http') ? site[0].site_logo : `/${site[0].site_logo}`;

  // Function to close the menu
  const closeMenu = () => {
    setIsNavOpen(false);
  };

  return (
    <div className="w-full fixed top-0 z-50 shadow-md bg-white">
      <div className="max-w-[1440px] mx-auto flex justify-between items-center p-4 border-b border-gray-400">
        <Link href="/">
          <div className="flex items-center cursor-pointer">
            <Image src={logoPath} alt='logo' width={35} height={18} />
            <span className="ml-2 text-lg text-black">{site[0].site_name}</span>
          </div>
        </Link>
        <nav>
          <section className="MOBILE-MENU flex items-center">
            <div
              className={`HAMBURGER-ICON space-y-2 ${isNavOpen ? 'hidden' : 'block'}`}
              onClick={() => setIsNavOpen(true)}
            >
              <span className="block h-0.5 w-8 bg-black"></span>
              <span className="block h-0.5 w-8 bg-black"></span>
              <span className="block h-0.5 w-8 bg-black"></span>
            </div>

            <div
              className={`CLOSE-ICON ${isNavOpen ? 'block' : 'hidden'}`}
              onClick={() => setIsNavOpen(false)}
            >
              <svg
                className="h-8 w-8 text-gray-600"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <line x1="18" y1="6" x2="6" y2="18" />
                <line x1="6" y1="6" x2="18" y2="18" />
              </svg>
            </div>

            <div className={isNavOpen ? "showMenuNav" : "hideMenuNav"}>
              <div className="flex flex-col items-center justify-between min-h-[100px]">
                <ShoppingCart />
              </div>
              <ul className="flex flex-col items-center justify-between min-h-[250px]">
                {menu.map((item) => (
                  <li className="border-b border-gray-400 my-8 uppercase" key={item.menu_id}>
                    <Link key={item.id} href={item.menu_link} passHref>
                      <span onClick={closeMenu} className="block px-4 py-2 text-black hover:bg-gray-100 cursor-pointer">{item.menu_page}</span>
                    </Link>
                  </li>
                ))}
              </ul>
              <>
              {session ?
                (<div className="flex flex-col items-center justify-between min-h-[100px]">
                  <Link href="/user" passHref>
                      <p className="block px-4 py-2 text-black hover:bg-gray-100 cursor-pointer">Welcome {session.user?.username}</p>
                    </Link>
                    <button onClick={() => signOut()} className="block px-4 py-2 text-black hover:bg-gray-100 cursor-pointer">Sign out</button>
                </div>) :
              (<div className="flex flex-col items-center justify-between min-h-[100px]">
                <Link href="/auth/login" passHref>
                  <span onClick={closeMenu} className="block px-4 py-2 text-black hover:bg-gray-100 cursor-pointer">Login</span>
                </Link>
                <Link href="/auth/register" passHref>
                  <span onClick={closeMenu} className="block px-4 py-2 text-black hover:bg-gray-100 cursor-pointer">Sign Up</span>
                </Link>
              </div>)
              }
              </>
            </div>
          </section>
        </nav>
      </div>
      <style jsx>{`
        .hideMenuNav {
          display: none;
        }
        .showMenuNav {
          display: block;
          position: absolute;
          width: 100%;
          height: 100vh;
          top: 0;
          left: 0;
          background: white;
          z-index: 10;
          display: flex;
          flex-direction: column;
          justify-content: space-evenly;
          align-items: center;
        }
        .CLOSE-ICON {
          z-index: 20; /* Ensure it's above other content */
        }
      `}</style>
    </div>
  );
}
"""

# Write the generated content to the Navbar.jsx file
navbar_path = os.path.join(app_name, COMPONENT_DIR, 'Navbar.jsx')

write_to_file(navbar_path, NAVBAR_TEMPLATE)
