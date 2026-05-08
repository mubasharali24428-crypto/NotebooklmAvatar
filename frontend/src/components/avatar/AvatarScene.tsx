"use client";

import { Canvas } from "@react-three/fiber";
import { OrbitControls, Environment, ContactShadows } from "@react-three/drei";
import { AvatarModel } from "./AvatarModel";

interface AvatarSceneProps {
  emotionConfig: any;
  isSpeaking: boolean;
}

export function AvatarScene({ emotionConfig, isSpeaking }: AvatarSceneProps) {

  // Adjust lighting mood based on emotion color overlay
  const ambientLightColor = emotionConfig?.animation?.color_overlay || "#ffffff";
  const lightIntensity = emotionConfig?.emotion === "heartbroken" ? 0.3 : 1;

  return (
    <Canvas camera={{ position: [0, 0, 4], fov: 45 }}>
      <color attach="background" args={["#111111"]} />

      {/* Dynamic Lighting */}
      <ambientLight intensity={lightIntensity} color={ambientLightColor} />
      <directionalLight position={[5, 5, 5]} intensity={1} color={ambientLightColor} />
      <pointLight position={[-5, 5, -5]} intensity={0.5} />

      {/* 3D Avatar Group */}
      <AvatarModel emotionConfig={emotionConfig} isSpeaking={isSpeaking} />

      {/* Environment Settings */}
      <OrbitControls enableZoom={false} enablePan={false} maxPolarAngle={Math.PI / 2} minPolarAngle={Math.PI / 3} />
      <ContactShadows opacity={0.5} scale={5} blur={2.4} />
      <Environment preset="city" />
    </Canvas>
  );
}
