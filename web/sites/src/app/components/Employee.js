// ./web/sites/src/app/components/Employee.js
"use client";

import React, { useRef, useMemo } from "react";
import { useFrame } from "@react-three/fiber";
// Remove Text from this import if you comment it out below
import { Capsule /*, Text */ } from "@react-three/drei";
import * as THREE from "three";

// --- Constants ---
// ... (constants remain the same)
export const bounds = { x: [-5.5, 5.5], z: [-5.5, 5.5] };
const MOVE_SPEED = 0.8;
const TURN_SPEED_FACTOR = Math.PI * 0.5;
const MOVEMENT_LERP_FACTOR = 2.5;
const ROTATION_SLERP_FACTOR = 2.5;
const RANDOM_TURN_PROBABILITY = 0.008;
const TEXT_Y_OFFSET = 0.8;
const CAPSULE_RADIUS = 0.25;
const CAPSULE_LENGTH = 0.5;


export function Employee({ initialPosition, color = "royalblue", role = "Employee" }) {
  const groupRef = useRef(); // Ref for the entire group (capsule + text)

  // ... (initialDirection and state refs remain the same)
  const initialDirection = useMemo(() =>
    new THREE.Vector3(Math.random() - 0.5, 0, Math.random() - 0.5)
      .normalize(),
    []
  );
  const velocity = useRef(initialDirection.clone().multiplyScalar(MOVE_SPEED));
  const targetDirection = useRef(initialDirection.clone());


  useFrame((state, delta) => {
    // ... (useFrame logic remains the same)
    if (!groupRef.current) return;

    const position = groupRef.current.position;
    const currentVelocity = velocity.current;

    // --- Boundary Check and Direction Change ---
    let needsNewDirection = false;
    const checkPos = position.clone().add(currentVelocity.clone().multiplyScalar(delta * 5));

    if (checkPos.x < bounds.x[0] || checkPos.x > bounds.x[1]) {
        targetDirection.current.x = -Math.sign(currentVelocity.x);
        targetDirection.current.z = (Math.random() - 0.5) * 1.5;
        needsNewDirection = true;
    }
     else if (checkPos.z < bounds.z[0] || checkPos.z > bounds.z[1]) {
        targetDirection.current.z = -Math.sign(currentVelocity.z);
        targetDirection.current.x = (Math.random() - 0.5) * 1.5;
        needsNewDirection = true;
    }

     if (!needsNewDirection && Math.random() < RANDOM_TURN_PROBABILITY) {
        targetDirection.current.set(Math.random() - 0.5, 0, Math.random() - 0.5);
        needsNewDirection = true;
     }

     if (needsNewDirection) {
        targetDirection.current.normalize();
     }

     // --- Smooth Turning & Velocity Update ---
     const targetVelocity = targetDirection.current.clone().multiplyScalar(MOVE_SPEED);
     currentVelocity.lerp(targetVelocity, delta * MOVEMENT_LERP_FACTOR);
     currentVelocity.y = 0;

     // --- Update Position ---
     const movementThisFrame = currentVelocity.clone().multiplyScalar(delta);
     groupRef.current.position.add(movementThisFrame);

     // Clamp position strictly to bounds
     groupRef.current.position.x = Math.max(bounds.x[0], Math.min(bounds.x[1], groupRef.current.position.x));
     groupRef.current.position.z = Math.max(bounds.z[0], Math.min(bounds.z[1], groupRef.current.position.z));

    // --- Smooth Look Rotation (apply to the group) ---
    if (currentVelocity.lengthSq() > 0.0001) {
        const lookDirection = currentVelocity.clone().normalize();
        const targetQuaternion = new THREE.Quaternion();
        const lookAtMatrix = new THREE.Matrix4().lookAt(
            position,
            position.clone().add(lookDirection),
            THREE.Object3D.DEFAULT_UP
        );
        targetQuaternion.setFromRotationMatrix(lookAtMatrix);
        groupRef.current.quaternion.slerp(targetQuaternion, delta * ROTATION_SLERP_FACTOR * TURN_SPEED_FACTOR);
    }
  });

  return (
    // Group holds the capsule and text, manages shared position and rotation
    <group ref={groupRef} position={initialPosition} castShadow>
        <Capsule
            args={[CAPSULE_RADIUS, CAPSULE_LENGTH, 8, 16]}
        >
            <meshStandardMaterial color={color} metalness={0.2} roughness={0.6} />
        </Capsule>

        {/* --- >>> COMMENT OUT THE TEXT COMPONENT <<< --- */}
        {/*
        <Text
            position={[0, TEXT_Y_OFFSET, 0]} // Position text relative to the group's origin
            fontSize={0.22}
            color="black"
            anchorX="center"
            anchorY="middle"
            outlineWidth={0.01}
            outlineColor="#ffffff"
        >
            {role}
        </Text>
        */}
         {/* --- >>> END OF COMMENTED OUT BLOCK <<< --- */}
    </group>
  );
}