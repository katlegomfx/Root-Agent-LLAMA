# utils\nextBuilder\frontend\components\socialLinks.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8

COMPONENT_TEMPLATE = """
'use client'
import React from 'react';
// import socialLinks from '../socialLinksData';
import { IconContext } from 'react-icons';
import { FaFacebook, FaTwitter, FaInstagram } from 'react-icons/fa';

const iconComponents = {
  facebook: FaFacebook,
  twitter: FaTwitter,
  instagram: FaInstagram,
  // Add more icons as needed
};

const socialLinks = [
  { name: 'Facebook', url: 'https://facebook.com', icon: 'facebook' },
  { name: 'Twitter', url: 'https://twitter.com', icon: 'twitter' },
  { name: 'Instagram', url: 'https://instagram.com', icon: 'instagram' },
 ]

const SocialLinks = () => (
  <ul style={{ listStyleType: 'none', display: 'flex', justifyContent: 'space-around' }}>
    <IconContext.Provider value={{ style: { fontSize: '20px' } }}>
      {socialLinks.map(({ name, url, icon }) => {
        const SocialIcon = iconComponents[icon];
        return (
          <li key={name}>
            <a href={url} aria-label={name} target="_blank" rel="noopener noreferrer">
              <SocialIcon />
            </a>
          </li>
        );
      })}
    </IconContext.Provider>
  </ul>
);

export default SocialLinks;
"""


create_component('SocialLinks', COMPONENT_TEMPLATE)
