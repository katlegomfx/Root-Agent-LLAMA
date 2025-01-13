# utils\nextBuilder\frontend\basic\components\footer.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, COMPONENT_DIR, app_name  # nopep8

# Template for the Footer component
FOOTER_TEMPLATE = """'use client'
import React from "react";
import Image from "next/image";
import Link from "next/link";

const Footer = ({ site, menu, timing }) => {

  const logoPath = site[0].site_logo.startsWith('http') ? site[0].site_logo : `/${site[0].site_logo}`;

  return (
    <footer className='w-full bg-gray-100 text-black border-t border-gray-200'>
      <div className='max-w-[1440px] mx-auto flex flex-col md:flex-row justify-between items-center sm:px-16 px-6 py-10'>

        <div className='flex flex-col justify-start items-start mb-4 md:mb-0'>
          <Image src={logoPath} alt='logo' width={35} height={18} className='object-contain' />
          <p className='text-base text-gray-700'>
            {site[0].site_name} {timing.year} <br />
            All Rights Reserved &copy;
          </p>
        </div>

        {/* <div className="flex flex-col sm:flex-row gap-4 items-center">
          {menu.map((item) => (
            <Link key={item.id} href={item.menu_link} className="text-gray-500 hover:text-gray-600">
              {item.menu_page}
            </Link>
          ))}
        </div> */}
      </div>
    </footer>
  )
}

export default Footer;
"""


# Write the generated content to the Footer.jsx file
footer_path = os.path.join(app_name, COMPONENT_DIR, 'Footer.jsx')
write_to_file(footer_path, FOOTER_TEMPLATE)
