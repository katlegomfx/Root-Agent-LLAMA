# utils\nextBuilder\frontend\basic\layout.py
import json
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_page, write_to_file, write_to_file, app_name, PAGE_DIR  # nopep8

# Template for the layout component
LAYOUT_TEMPLATE = """import { Metadata } from 'next'
import './globals.css'

import { fetchMenus } from '@/lib/utils/menus';
import { fetchSites } from '@/lib/utils/sites';
import { fetchLatestDate } from '@/lib/utils/date';

import Footer from '@/components/Footer';
import Navbar from '@/components/Navbar';

import ClickWrapper from '@/components/ClickWrapper';
import GeoLocationLogger from '@/components/GeoLocationLogger';
import SiteInformation from '@/components/siteInformation';
import BackButton from '@/components/goBack';

import SessionWrapper from '@/components/SessionWrapper'


export const metadata = {
  title: "FlexData Hub",
  description: "Discover world's best Data Driven Saas application",
};

export default async function RootLayout({ children }) {
  const allMenu = await fetchMenus();
  const allSite = await fetchSites();
  const timing = await fetchLatestDate();

  return (
    <html lang='en'>
      <body className='relative'>
        <SessionWrapper>
          <GeoLocationLogger />
          <SiteInformation />
          <ClickWrapper>
            <Navbar site={allSite} menu={allMenu} />
            <div className="mt-20"> {/* Adjust the value as needed */}
              <BackButton />
            </div>
            {children}
            <Footer site={allSite} menu={allMenu} timing={timing} />
          </ClickWrapper>
        </SessionWrapper>
      </body>
    </html>
  );
}
"""

def create_root_layout():
    try:
      os.remove(os.path.join(app_name, PAGE_DIR, 'layout.js'))
    except:
        pass
    layout_path = os.path.join(app_name, PAGE_DIR, 'layout.jsx')

    write_to_file(layout_path, LAYOUT_TEMPLATE.strip())


if __name__ == "__main__":
    create_root_layout()
