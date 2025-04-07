// ./web/sites/src/app/page.js
"use client"; // Keep this

import dynamic from 'next/dynamic';
import React, { useState } from 'react'; // Import useState

// Dynamically import the OfficeScene component with SSR disabled
const OfficeScene = dynamic(
  () => import('./components/OfficeScene').then(mod => mod.OfficeScene),
  {
    ssr: false, // Disable server-side rendering for this component
    loading: () => <p style={{ textAlign: 'center', marginTop: '20px' }}>Loading 3D Scene...</p> // Optional loading indicator
  }
);

export default function Home() {
  // State for the goal textbox
  const [goal, setGoal] = useState('');

  return (
    // Use flex column layout to stack elements vertically, taking full height/width
    // Assuming TailwindCSS or similar utility classes are available based on existing className
    <div className="flex flex-col h-full w-full">
      {/* Top section for the goal input */}
      <div className="p-3 bg-gray-100 border-b border-gray-300 shadow-sm"> {/* Added padding, background, border */}
        <label htmlFor="goalInput" className="block text-sm font-medium text-gray-700 mb-1">
          Enter Goal:
        </label>
        <input
          type="text"
          id="goalInput"
          value={goal}
          onChange={(e) => setGoal(e.target.value)}
          placeholder="What is the team working towards?"
          className="w-full p-2 border border-gray-300 rounded shadow-sm focus:ring-indigo-500 focus:border-indigo-500 text-sm" // Basic input styling
        />
      </div>

      {/* Container for the OfficeScene, allowing it to take remaining space */}
      {/* Added relative positioning in case child elements need absolute positioning relative to the container */}
      <div className="flex-grow relative w-full h-full">
        {/* Render the dynamically imported component */}
        <OfficeScene />
      </div>
    </div>
  );
}
