// ./web/sites/src/app/components/Employee.js
"use client";

import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
import { Capsule, Text } from "@react-three/drei";
import * as THREE from "three";

// --- Constants ---
export const bounds = { x: [-5.5, 5.5], z: [-5.5, 5.5] }; // Movement boundaries
const MOVE_SPEED = 0.8; // Units per second
const TURN_SPEED_FACTOR = Math.PI * 0.5; // Radians per second base for turning
const MOVEMENT_LERP_FACTOR = 2.5; // How quickly velocity adjusts to target direction
const ROTATION_SLERP_FACTOR = 2.5; // How quickly rotation adjusts to look direction
const RANDOM_TURN_PROBABILITY = 0.008; // Chance per frame to initiate a random turn
const TEXT_Y_OFFSET = 0.8; // How far above the capsule's center the text should be
const CAPSULE_RADIUS = 0.25;
const CAPSULE_LENGTH = 0.5;
// Note: employeeHeight derived as (CAPSULE_LENGTH + 2 * CAPSULE_RADIUS) = 1.0, but not directly used here.

export function Employee({ initialPosition, color = "royalblue", role = "Employee" }) {
  const groupRef = useRef(); // Ref for the entire group (capsule + text)

  // Initial direction (memoized)
  const initialDirection = useMemo(() =>
    new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5)
      .normalize(),
    []
  );

  // State refs for movement
  const velocity = useRef(initialDirection.clone().multiplyScalar(MOVE_SPEED));
  const targetDirection = useRef(initialDirection.clone());

  useFrame((state, delta) => {
    if (!groupRef.current) return; // Guard clause

    const position = groupRef.current.position;
    const currentVelocity = velocity.current; // More readable alias

    // --- Boundary Check and Direction Change ---
    let needsNewDirection = false;
    // Check slightly ahead to anticipate collision with bounds
    const checkPos = position.clone().add(currentVelocity.clone().multiplyScalar(delta * 5));

    // Check X bounds
    if (checkPos.x < bounds.x[0] || checkPos.x > bounds.x[1]) {
        // Reverse X component and add some randomness to Z for a more natural turn
        targetDirection.current.x = -Math.sign(currentVelocity.x);
        targetDirection.current.z = (Math.random() - 0.5) * 1.5; // Allow wider turn angle
        needsNewDirection = true;
    }
    // Check Z bounds
     else if (checkPos.z < bounds.z[0] || checkPos.z > bounds.z[1]) {
        // Reverse Z component and add some randomness to X
        targetDirection.current.z = -Math.sign(currentVelocity.z);
        targetDirection.current.x = (Math.random() - 0.5) * 1.5; // Allow wider turn angle
        needsNewDirection = true;
    }

    // Randomly decide to change direction occasionally if not already turning
     if (!needsNewDirection && Math.random() < RANDOM_TURN_PROBABILITY) {
        targetDirection.current.set(Math.random() - 0.5, 0, Math.random() - 0.5);
        needsNewDirection = true;
     }

     // Normalize the target direction if it changed
     if (needsNewDirection) {
        targetDirection.current.normalize();
     }

     // --- Smooth Turning & Velocity Update ---
     // Lerp current velocity towards the target direction * speed
     const targetVelocity = targetDirection.current.clone().multiplyScalar(MOVE_SPEED);
     currentVelocity.lerp(targetVelocity, delta * MOVEMENT_LERP_FACTOR);
     currentVelocity.y = 0; // Ensure no vertical movement

     // --- Update Position ---
     const movementThisFrame = currentVelocity.clone().multiplyScalar(delta);
     groupRef.current.position.add(movementThisFrame);

     // Clamp position strictly to bounds to prevent drifting out
     groupRef.current.position.x = Math.max(bounds.x[0], Math.min(bounds.x[1], groupRef.current.position.x));
     groupRef.current.position.z = Math.max(bounds.z[0], Math.min(bounds.z[1], groupRef.current.position.z));

    // --- Smooth Look Rotation (apply to the group) ---
    // Only rotate if there's significant movement
    if (currentVelocity.lengthSq() > 0.0001) { // Use lengthSq for efficiency
        const lookDirection = currentVelocity.clone().normalize();
        const targetQuaternion = new THREE.Quaternion();
        // Create a rotation matrix that looks in the movement direction
        const lookAtMatrix = new THREE.Matrix4().lookAt(
            position, // Look from current position
            position.clone().add(lookDirection), // Look towards position + direction
            THREE.Object3D.DEFAULT_UP // Keep the default up vector
        );
        targetQuaternion.setFromRotationMatrix(lookAtMatrix);

        // Slerp the group's quaternion towards the target rotation
        groupRef.current.quaternion.slerp(targetQuaternion, delta * ROTATION_SLERP_FACTOR * TURN_SPEED_FACTOR);
    }
  });

  return (
    // Group holds the capsule and text, manages shared position and rotation
    <group ref={groupRef} position={initialPosition} castShadow>
        <Capsule
            args={[CAPSULE_RADIUS, CAPSULE_LENGTH, 8, 16]} // radius, length, T-segments, P-segments
            // Mesh is centered within the group
        >
            <meshStandardMaterial color={color} metalness={0.2} roughness={0.6} />
        </Capsule>
        <Text
            position={[0, TEXT_Y_OFFSET, 0]} // Position text relative to the group's origin
            fontSize={0.22}
            color="black"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.01}
            outlineColor="#ffffff"
            // Consider adding billboard={true} if you always want text facing the camera
            // regardless of the capsule's rotation.
            // billboard
        >
            {role}
        </Text>
    </group>
  );
}