"use client";

import { useRef, useEffect } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

interface AvatarModelProps {
  emotionConfig: any;
  isSpeaking: boolean;
}

export function AvatarModel({ emotionConfig, isSpeaking }: AvatarModelProps) {
  const groupRef = useRef<THREE.Group>(null);
  const headRef = useRef<THREE.Mesh>(null);
  const bodyRef = useRef<THREE.Mesh>(null);

  // Parse animation & appearance configs
  const animation = emotionConfig?.animation || { movement: "moderate", head_tilt: "straight" };
  const baseColor = emotionConfig?.animation?.color_overlay || "#ffffff";

  // Set target positions based on emotion
  let targetHeadRotationX = 0;
  if (animation.head_tilt === "down") targetHeadRotationX = 0.3; // Tilt down
  if (animation.head_tilt === "up") targetHeadRotationX = -0.2;  // Tilt up

  // Base movement speed
  let moveSpeed = 1;
  if (animation.movement === "energetic") moveSpeed = 2.5;
  if (animation.movement === "minimal") moveSpeed = 0.3;

  useFrame((state, delta) => {
    if (!groupRef.current || !headRef.current) return;

    // Smoothly rotate head towards target rotation
    headRef.current.rotation.x = THREE.MathUtils.lerp(
      headRef.current.rotation.x,
      targetHeadRotationX,
      0.05
    );

    // Apply ambient breathing / movement based on energy level
    const time = state.clock.getElapsedTime();
    groupRef.current.position.y = Math.sin(time * moveSpeed) * 0.05;

    // Add speaking animation (bobbing head slightly)
    if (isSpeaking) {
      headRef.current.position.y = 1.2 + Math.sin(time * 10) * 0.02;
    } else {
      headRef.current.position.y = 1.2;
    }
  });

  return (
    <group ref={groupRef} position={[0, -1, 0]}>
      {/* Body */}
      <mesh ref={bodyRef} position={[0, 0.5, 0]}>
        <cylinderGeometry args={[0.5, 0.5, 1.5, 32]} />
        <meshStandardMaterial color={baseColor} />
      </mesh>

      {/* Head */}
      <mesh ref={headRef} position={[0, 1.2, 0]}>
        <sphereGeometry args={[0.4, 32, 32]} />
        <meshStandardMaterial color={baseColor} />

        {/* Simple Eyes to indicate direction */}
        <mesh position={[-0.15, 0.1, 0.35]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshBasicMaterial color="black" />
        </mesh>
        <mesh position={[0.15, 0.1, 0.35]}>
          <sphereGeometry args={[0.05, 16, 16]} />
          <meshBasicMaterial color="black" />
        </mesh>

        {/* Simple Mouth indicator */}
        <mesh position={[0, -0.1, 0.38]} scale={[isSpeaking ? 1.5 : 1, isSpeaking ? 0.8 : 0.2, 1]}>
          <boxGeometry args={[0.15, 0.1, 0.05]} />
          <meshBasicMaterial color="black" />
        </mesh>

      </mesh>
    </group>
  );
}
