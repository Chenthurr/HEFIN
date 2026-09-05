"use client";

import { useMemo, useRef } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import * as THREE from "three";

const NODE_COUNT = 140;
const CONNECT_DISTANCE = 2.6;
const RADIUS = 6;

function generateNodes(count: number, radius: number) {
  const positions = new Float32Array(count * 3);
  for (let i = 0; i < count; i++) {
    const y = 1 - (i / (count - 1)) * 2;
    const r = Math.sqrt(1 - y * y);
    const theta = Math.PI * (3 - Math.sqrt(5)) * i;
    const jitter = 0.85 + Math.random() * 0.3;
    positions[i * 3] = Math.cos(theta) * r * radius * jitter;
    positions[i * 3 + 1] = y * radius * jitter;
    positions[i * 3 + 2] = Math.sin(theta) * r * radius * jitter;
  }
  return positions;
}
function buildEdges(positions: Float32Array, maxDistance: number) {
  const points: number[] = []; const count = positions.length / 3;
  for (let i = 0; i < count; i++) for (let j = i + 1; j < count; j++) {
    const dx = positions[i * 3] - positions[j * 3], dy = positions[i * 3 + 1] - positions[j * 3 + 1], dz = positions[i * 3 + 2] - positions[j * 3 + 2];
    if (Math.sqrt(dx * dx + dy * dy + dz * dz) < maxDistance) points.push(positions[i * 3], positions[i * 3 + 1], positions[i * 3 + 2], positions[j * 3], positions[j * 3 + 1], positions[j * 3 + 2]);
  }
  return new Float32Array(points);
}
function GalaxyNetwork() {
  const groupRef = useRef<THREE.Group>(null);
  const nodePositions = useMemo(() => generateNodes(NODE_COUNT, RADIUS), []);
  const edgePositions = useMemo(() => buildEdges(nodePositions, CONNECT_DISTANCE), [nodePositions]);
  useFrame((_, delta) => { if (groupRef.current) { groupRef.current.rotation.y += delta * 0.045; groupRef.current.rotation.x = Math.sin(Date.now() * 0.00005) * 0.15; } });
  return <group ref={groupRef}><points><bufferGeometry><bufferAttribute attach="attributes-position" count={nodePositions.length / 3} array={nodePositions} itemSize={3} /></bufferGeometry><pointsMaterial size={0.06} color="#4FD1C5" sizeAttenuation transparent opacity={0.9} /></points><lineSegments><bufferGeometry><bufferAttribute attach="attributes-position" count={edgePositions.length / 3} array={edgePositions} itemSize={3} /></bufferGeometry><lineBasicMaterial color="#2E4A52" transparent opacity={0.35} /></lineSegments></group>;
}
export default function MedicalGalaxyScene() { return <Canvas camera={{ position: [0, 0, 11], fov: 50 }} dpr={[1, 1.5]} gl={{ antialias: true, alpha: true }}><ambientLight intensity={0.4} /><GalaxyNetwork /></Canvas>; }
