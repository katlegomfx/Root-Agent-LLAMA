// ./web/sites/src/app/components/OfficeScene.js
"use client";

import React, { Suspense, useMemo } from "react";
import { Canvas } from "@react-three/fiber";
import { OrbitControls, Plane, Box, Environment } from "@react-three/drei";
// Import Employee and the bounds it exports
import { Employee, bounds as employeeBoundsDefinition } from "./Employee";
import * as THREE from "three";

// Consistent bounds definition, derived from the Employee component's export
const bounds = employeeBoundsDefinition;

// Simple representation of desks
function Desk({ position }) {
    return (
        <Box
            position={position} // Center of the desk box
            args={[1.2, 0.75, 0.6]} // width, height, depth
            castShadow
            receiveShadow
        >
             <meshStandardMaterial color="#A0522D" metalness={0.1} roughness={0.8}/> {/* Sienna Brown color */}
        </Box>
    );
}

export function OfficeScene() {
  const numEmployees = 7;

  // Define roles for each employee
  const employeeRoles = useMemo(() => [
      "CEO",
      "Lead Developer",
      "Frontend Dev",
      "Backend Dev",
      "UI/UX Designer",
      "Marketing Lead",
      "Intern",
      // Add more roles if numEmployees increases
  ], []); // Keep dependency array empty if roles are static

  // Define desk positions first
  const deskPositions = useMemo(() => [
      // [x, y (center), z]
      [-3, 0.375, -3], // Desk height is 0.75, so center Y is 0.75 / 2 = 0.375
      [ 3, 0.375, -3],
      [-3, 0.375,  3],
      [ 3, 0.375,  3],
      [ 0, 0.375, -4],
      [ 0, 0.375,  0], // Added a central desk
  ], []);


  // Generate initial positions for employees, avoiding desks and other employees
  const employeePositions = useMemo(() => {
      const positions = [];
      const employeeRadius = 0.3; // Slightly larger than capsule radius for spacing
      const deskFootprintRadius = 0.7; // Approx radius around desk center to avoid
      const employeeBaseY = 0.5; // Base height Y = capsule_length/2 + capsule_radius = 0.25 + 0.25

      for (let i = 0; i < numEmployees; i++) {
          let posValid = false;
          let x, z;
          let attempts = 0;
          const maxAttempts = 100; // Increased attempts

          while (!posValid && attempts < maxAttempts) {
              attempts++;
              // Generate random position within bounds, accounting for radius
              x = THREE.MathUtils.randFloat(bounds.x[0] + employeeRadius, bounds.x[1] - employeeRadius);
              z = THREE.MathUtils.randFloat(bounds.z[0] + employeeRadius, bounds.z[1] - employeeRadius);
              posValid = true;

              // Check collision with desks (using 2D distance on XZ plane)
              for (const deskPos of deskPositions) {
                  const dx = x - deskPos[0]; // Desk X
                  const dz = z - deskPos[2]; // Desk Z
                  // Using squared distance avoids sqrt, add radii squared
                  if ((dx * dx + dz * dz) < (employeeRadius + deskFootprintRadius) ** 2) {
                      posValid = false;
                      break; // No need to check other desks
                  }
              }

              // Check collision with already placed employees if desk check passed
              if (posValid) {
                  for(const existingPos of positions) {
                      const dx = x - existingPos[0]; // Existing employee X
                      const dz = z - existingPos[2]; // Existing employee Z
                      // Check distance between employee centers (radius * 2)
                      if ((dx * dx + dz * dz) < (employeeRadius * 2.2) ** 2) { // Added slight buffer
                         posValid = false;
                         break; // No need to check other employees
                      }
                  }
              }
          } // End while loop

          if (!posValid) {
              console.warn(`Could not find valid position for employee ${i+1} after ${attempts} attempts. Placing near center as fallback.`);
              // Fallback: Place in a circle around the center
              const angle = (i / numEmployees) * Math.PI * 2;
              const radius = 1.5 + Math.random() * 0.5; // Slightly larger circle
              x = Math.cos(angle) * radius;
              z = Math.sin(angle) * radius;
              // Ensure fallback is within bounds too (simple clamp)
              x = Math.max(bounds.x[0] + employeeRadius, Math.min(bounds.x[1] - employeeRadius, x));
              z = Math.max(bounds.z[0] + employeeRadius, Math.min(bounds.z[1] - employeeRadius, z));

          }
          // Add the valid or fallback position [x, y, z]
          positions.push([x, employeeBaseY, z]); // Use calculated base Y
      }
      return positions;
  }, [numEmployees, deskPositions]); // Recalculate if numEmployees or desks change


  // Generate random colors for employees
  const employeeColors = useMemo(() =>
    Array.from({ length: numEmployees }, () =>
      `hsl(${Math.random() * 360}, 70%, 60%)`
    ), [numEmployees] // Recalculate if numEmployees changes
  );


  return (
    <Canvas
        camera={{ position: [0, 8, 14], fov: 55 }}
        shadows
        style={{ background: "#e0f2fe" }} // Light sky blue background
        gl={{ antialias: true }} // Enable anti-aliasing
    >
      {/* Lighting Setup */}
      <ambientLight intensity={0.6} /> {/* Softer ambient light */}
      <directionalLight
          position={[10, 15, 10]} // Adjusted angle slightly
          intensity={1.0}
          castShadow
          shadow-mapSize-width={2048} // Good resolution for shadows
          shadow-mapSize-height={2048}
          shadow-camera-far={50}
          shadow-camera-left={-10} // Adjusted bounds to fit scene better
          shadow-camera-right={10}
          shadow-camera-top={10}
          shadow-camera-bottom={-10}
          shadow-bias={-0.0005} // Helps prevent shadow acne
       />
       {/* Add subtle point lights for fill */}
       <pointLight position={[-10, 10, -10]} intensity={0.3} />
       <pointLight position={[10, 5, 5]} intensity={0.2} />
       <pointLight position={[0, -10, 0]} intensity={0.1} /> {/* Underneath light */}


      {/* Environment Map for reflections and ambient lighting */}
       <Suspense fallback={null}>
         <Environment preset="city" /> {/* Changed preset for different ambiance */}
       </Suspense>

      {/* Floor Plane */}
      <Plane
        // Make plane slightly larger than bounds to avoid seeing edges
        args={[bounds.x[1]*2 + 2, bounds.z[1]*2 + 2]}
        rotation={[-Math.PI / 2, 0, 0]} // Rotate to be horizontal
        position={[0, 0, 0]} // Position at the scene origin Y=0
        receiveShadow // Allow the floor to receive shadows
      >
        {/* A slightly more interesting floor material */}
        <meshStandardMaterial color="#cfd8dc" roughness={0.7} metalness={0.1} /> {/* Blue Grey color */}
      </Plane>

       {/* Render Desks */}
       {deskPositions.map((pos, i) => (
           <Desk key={`desk-${i}`} position={pos} />
       ))}

      {/* Render Employees */}
      {employeePositions.map((pos, i) => (
        <Employee
            key={`employee-${i}`}
            initialPosition={pos}
            color={employeeColors[i]}
            // Safely access role, fallback handled by Employee prop default
            role={employeeRoles[i] ?? 'Staff'} // Use nullish coalescing, or rely on default prop in Employee
        />
      ))}

      {/* Camera Controls */}
      <OrbitControls
          minDistance={3}     // Don't zoom in too close
          maxDistance={35}    // Don't zoom out too far
          maxPolarAngle={Math.PI / 2 - 0.05} // Limit vertical rotation (don't go below floor)
          target={[0, 0.5, 0]} // Point camera slightly above the floor origin
          enablePan={true}    // Allow panning
          enableDamping={true} // Smooth camera movement
          dampingFactor={0.1}
       />
    </Canvas>
  );
}