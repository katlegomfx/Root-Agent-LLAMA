// ./web/sites/src/app/page.js
"use client"; // Keep this, although dynamic import handles client-side focus

import dynamic from 'next/dynamic';
import React from 'react';

// Dynamically import the OfficeScene component with SSR disabled
// This is crucial because Three.js relies on browser APIs (window, document)
const OfficeScene = dynamic(
  () => import('./components/OfficeScene').then(mod => mod.OfficeScene),
  {
    ssr: false, // Disable server-side rendering for this component
    loading: () => <p style={{ textAlign: 'center', marginTop: '20px' }}>Loading 3D Scene...</p> // Optional loading indicator
  }
);

export default function Home() {
  return (
    // Ensure the container takes full height - className="h-full w-full" works because of globals.css changes
    // And because the parent elements (html, body, #__next) are also set to 100% height.
    <div className="h-full w-full">
      {/* Render the dynamically imported component */}
      <OfficeScene />
    </div>
  );
}