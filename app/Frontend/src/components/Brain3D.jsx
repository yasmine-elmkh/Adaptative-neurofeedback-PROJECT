/**
 * NeuroCap – Brain3D  (Professional v3)
 *
 * Two rendering paths:
 *   A) Real cortical mesh  → loads /brain_mesh.json (generate with scripts/generate_brain_mesh.py)
 *      Per-vertex activation heat-map updated in real-time.
 *   B) Procedural fallback → mild, clean gyri, NO extreme fissure displacement.
 *
 * Material: MeshPhysicalMaterial with clearcoat + Environment for reflections.
 * Color:    Medical blue-gray (#8898b5) — looks like a high-quality anatomy illustration.
 */
import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { OrbitControls } from '@react-three/drei'
import * as THREE from 'three'

// ── Constants ───────────────────────────────────────────────────────────────
const BRAIN_COLOR  = '#8898b5'   // medical blue-gray
const CEREB_COLOR  = '#7585a0'
const STEM_COLOR   = '#606878'

// Prefrontal (Fz) position in normalized mesh space
const FZ = new THREE.Vector3(0, 0.45, 0.58)

// ── A) Real mesh path ───────────────────────────────────────────────────────

function useBrainMeshJson() {
  const [data, setData] = useState(null)

  useEffect(() => {
    fetch('/brain_mesh.json')
      .then((r) => (r.ok ? r.json() : null))
      .then((d) => d && setData(d))
      .catch(() => {})
  }, [])

  return useMemo(() => {
    if (!data) return null

    const geo = new THREE.BufferGeometry()
    const verts = new Float32Array(data.vertices)
    geo.setAttribute('position', new THREE.BufferAttribute(verts, 3))
    geo.setIndex(new THREE.BufferAttribute(new Uint32Array(data.faces), 1))
    geo.computeVertexNormals()

    // Initialise vertex colors (base brain color)
    const n      = verts.length / 3
    const colors = new Float32Array(n * 3)
    const base   = new THREE.Color(BRAIN_COLOR)
    for (let i = 0; i < n; i++) {
      colors[i * 3]     = base.r
      colors[i * 3 + 1] = base.g
      colors[i * 3 + 2] = base.b
    }
    geo.setAttribute('color', new THREE.BufferAttribute(colors, 3))

    return { geo, nLeft: data.n_left ?? 0 }
  }, [data])
}

function RealBrainMesh({ concentration, stress, meshData }) {
  const meshRef   = useRef()
  const frameRef  = useRef(0)
  const { geo }   = meshData
  const pos       = geo.attributes.position
  const colorAttr = geo.attributes.color
  const tmp       = useMemo(() => new THREE.Vector3(), [])
  const base      = useMemo(() => new THREE.Color(BRAIN_COLOR), [])
  const activeClr = useMemo(() => new THREE.Color(), [])

  useFrame(({ clock }) => {
    frameRef.current++
    if (frameRef.current % 4 !== 0) return   // 15 fps colour update is enough

    const t   = clock.getElapsedTime()
    const n   = pos.count
    const isStress = stress > 0.6 && concentration < 0.45

    for (let i = 0; i < n; i++) {
      tmp.set(pos.getX(i), pos.getY(i), pos.getZ(i))
      const dist2    = tmp.distanceToSquared(FZ)
      const act      = concentration * Math.exp(-dist2 * 2.8)
      const pulse    = 1 + Math.sin(t * 3 + i * 0.0008) * 0.015 * act

      if (isStress) {
        activeClr.setHSL(0.04, 0.9, 0.52)
      } else {
        activeClr.setHSL(0.57, 0.85, 0.52)
      }

      const r = base.r + (activeClr.r - base.r) * act * pulse
      const g = base.g + (activeClr.g - base.g) * act * pulse
      const b = base.b + (activeClr.b - base.b) * act * pulse
      colorAttr.setXYZ(i, r, g, b)
    }
    colorAttr.needsUpdate = true
  })

  return (
    <mesh ref={meshRef} geometry={geo}>
      <meshPhysicalMaterial
        vertexColors
        roughness={0.28}
        metalness={0.18}
        clearcoat={0.90}
        clearcoatRoughness={0.18}
        envMapIntensity={0.0}
      />
    </mesh>
  )
}

// ── B) Procedural fallback ───────────────────────────────────────────────────

// Mild, organised coronal gyri using cylindrical angle — no extreme fissures
function applyGyri(geometry, amp) {
  const pos  = geometry.attributes.position
  const norm = geometry.attributes.normal
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i)
    const nx = norm.getX(i), ny = norm.getY(i), nz = norm.getZ(i)
    const theta = Math.atan2(z, x)
    const d =
      Math.sin(5.5 * y + Math.sin(2.8 * theta) * 0.90) * amp +
      Math.sin(5.5 * y + 2.1 + Math.cos(3.3 * theta) * 0.80) * amp * 0.62 +
      Math.sin(9.2 * y + Math.cos(5.1 * theta + 0.8) * 0.95) * amp * 0.33 +
      Math.sin(9.2 * y + 1.8 + Math.sin(6.0 * theta) * 0.70) * amp * 0.24
    pos.setXYZ(i, x + nx * d, y + ny * d, z + nz * d)
  }
  geometry.computeVertexNormals()
}

function applyFolia(geometry) {
  const pos  = geometry.attributes.position
  const norm = geometry.attributes.normal
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i), z = pos.getZ(i)
    const nx = norm.getX(i), ny = norm.getY(i), nz = norm.getZ(i)
    const d = Math.cos(20 * y + Math.sin(x * 4) * 0.4) * 0.016
            + Math.cos(28 * y + Math.cos(z * 5) * 0.3) * 0.009
    pos.setXYZ(i, x + nx * d, y + ny * d, z + nz * d)
  }
  geometry.computeVertexNormals()
}

function ProceduralHemisphere({ side, concentration, stress }) {
  const meshRef = useRef()
  const matRef  = useRef()

  const geo = useMemo(() => {
    const g  = new THREE.SphereGeometry(1.0, 72, 72)
    const sx = side === 'left' ? -0.93 : 0.93
    g.applyMatrix4(new THREE.Matrix4().makeScale(sx, 0.86, 0.93))
    g.computeVertexNormals()

    // Flatten inferior surface
    const pos = g.attributes.position
    for (let i = 0; i < pos.count; i++) {
      const y = pos.getY(i)
      if (y < -0.24) pos.setY(i, -0.24 + (y + 0.24) * 0.28)
    }
    pos.needsUpdate = true
    g.computeVertexNormals()

    applyGyri(g, 0.038)
    return g
  }, [side])

  useFrame(({ clock }) => {
    if (!meshRef.current || !matRef.current) return
    const t = clock.getElapsedTime()
    const breathe = 1 + Math.sin(t * 0.65 + (side === 'left' ? 0 : 1.0)) * 0.005
    meshRef.current.scale.setScalar(breathe)

    matRef.current.color.setHSL(0.60, 0.22, 0.58 + concentration * 0.06)

    if (stress > 0.6 && concentration < 0.45) {
      matRef.current.emissive.setHSL(0.04, 0.85, 0.32)
      matRef.current.emissiveIntensity = stress * 0.13
    } else if (concentration > 0.35) {
      matRef.current.emissive.setHSL(0.57, 0.90, 0.28)
      matRef.current.emissiveIntensity = concentration * 0.10
    } else {
      matRef.current.emissiveIntensity = 0
    }
  })

  return (
    <mesh ref={meshRef} geometry={geo}
          position={[side === 'left' ? -0.13 : 0.13, 0.05, 0]}>
      <meshPhysicalMaterial
        ref={matRef}
        color={BRAIN_COLOR}
        roughness={0.28}
        metalness={0.18}
        clearcoat={0.90}
        clearcoatRoughness={0.18}
        envMapIntensity={0.0}
        emissive="#000000"
        emissiveIntensity={0}
      />
    </mesh>
  )
}

function Cerebellum() {
  const geo = useMemo(() => {
    const g = new THREE.SphereGeometry(0.42, 56, 56)
    g.applyMatrix4(new THREE.Matrix4().makeScale(1.36, 0.55, 0.96))
    g.computeVertexNormals()
    applyFolia(g)
    return g
  }, [])
  return (
    <mesh geometry={geo} position={[0, -0.80, -0.52]}>
      <meshPhysicalMaterial
        color={CEREB_COLOR}
        roughness={0.38}
        metalness={0.10}
        clearcoat={0.50}
        clearcoatRoughness={0.30}
        envMapIntensity={0.0}
      />
    </mesh>
  )
}

function BrainStem() {
  return (
    <mesh position={[0, -1.06, -0.25]}>
      <cylinderGeometry args={[0.10, 0.08, 0.52, 16]} />
      <meshPhysicalMaterial
        color={STEM_COLOR}
        roughness={0.45}
        metalness={0.08}
        clearcoat={0.40}
        clearcoatRoughness={0.35}
        envMapIntensity={0.0}
      />
    </mesh>
  )
}

// ── Electrodes ──────────────────────────────────────────────────────────────
const ELECTRODES = [
  [0,     0.87,  0.74],   // Fz
  [0,     0.95,  0.02],   // Cz
  [0,     0.79, -0.60],   // Pz
  [-0.62, 0.52,  0.48],   // F3
  [ 0.62, 0.52,  0.48],   // F4
  [-0.87, 0.08,  0.00],   // T3
  [ 0.87, 0.08,  0.00],   // T4
  [-0.63, 0.48, -0.50],   // P3
  [ 0.63, 0.48, -0.50],   // P4
]

function Electrodes({ concentration }) {
  const groupRef = useRef()
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    groupRef.current?.children.forEach((m, i) => {
      if (m.material) {
        const base = i === 0 ? 0.9 : 0.55
        m.material.emissiveIntensity =
          base + Math.sin(t * 2.8 + i * 0.6) * 0.45 * Math.max(concentration, 0.18)
      }
    })
  })
  return (
    <group ref={groupRef}>
      {ELECTRODES.map((pos, i) => (
        <mesh key={i} position={pos}>
          <sphereGeometry args={[0.038, 12, 12]} />
          <meshStandardMaterial color="#00d4ff" emissive="#00d4ff" emissiveIntensity={0.7} />
        </mesh>
      ))}
    </group>
  )
}

// ── Neural fibers ────────────────────────────────────────────────────────────
function NeuralFibers({ concentration }) {
  const groupRef = useRef()
  const geos = useMemo(() => {
    const fz = ELECTRODES[0]
    return [
      [fz, ELECTRODES[3]],
      [fz, ELECTRODES[4]],
      [fz, ELECTRODES[7]],
      [fz, ELECTRODES[8]],
      [fz, ELECTRODES[2]],
      [ELECTRODES[3], ELECTRODES[4]],
      [ELECTRODES[5], ELECTRODES[6]],
    ].map(([a, b]) =>
      new THREE.BufferGeometry().setFromPoints([
        new THREE.Vector3(...a),
        new THREE.Vector3(...b),
      ])
    )
  }, [])

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime()
    groupRef.current?.children.forEach((line, i) => {
      line.material.opacity =
        0.07 + concentration * 0.42 + Math.sin(t * 2.0 + i * 1.2) * 0.06
      line.material.color.setHSL(0.55 + i * 0.02, 0.75, 0.62)
    })
  })

  return (
    <group ref={groupRef}>
      {geos.map((g, i) => (
        <line key={i} geometry={g}>
          <lineBasicMaterial transparent opacity={0.1} />
        </line>
      ))}
    </group>
  )
}

// ── Main scene ───────────────────────────────────────────────────────────────
function BrainScene({ concentration = 0.5, stress = 0.3 }) {
  const realMesh = useBrainMeshJson()

  return (
    <>
      {/* Studio-quality lighting rig — no CDN required */}
      <hemisphereLight skyColor="#ddeeff" groundColor="#223344" intensity={0.55} />
      <ambientLight intensity={0.20} />

      {/* Key light — warm white from upper right */}
      <directionalLight position={[ 4,  8,  5]} intensity={1.10} color="#fff8f0" castShadow={false} />
      {/* Fill light — cool blue from upper left */}
      <directionalLight position={[-5,  3, -2]} intensity={0.45} color="#b8ccff" />
      {/* Rim light — creates the "floating" edge highlight */}
      <directionalLight position={[ 0, -3, -5]} intensity={0.30} color="#8899cc" />
      {/* Top specular bounce */}
      <directionalLight position={[ 0,  6,  0]} intensity={0.25} color="#ffffff" />

      {/* Activity glow */}
      <pointLight position={[0,  0.4,  2.0]} intensity={concentration * 3.2}
                  color="#40c8ff" distance={5} decay={2} />
      <pointLight position={[0,  0.2, -1.2]} intensity={stress       * 2.0}
                  color="#ff4020" distance={4} decay={2} />

      <group rotation={[-0.18, 0, 0]}>
        {realMesh ? (
          // ── A: Real cortical mesh ────────────────────────────────────────
          <RealBrainMesh
            concentration={concentration}
            stress={stress}
            meshData={realMesh}
          />
        ) : (
          // ── B: Procedural fallback ───────────────────────────────────────
          <>
            <ProceduralHemisphere side="left"  concentration={concentration} stress={stress} />
            <ProceduralHemisphere side="right" concentration={concentration} stress={stress} />
          </>
        )}
        <Cerebellum />
        <BrainStem />
        <Electrodes concentration={concentration} />
        <NeuralFibers concentration={concentration} />
      </group>

      <OrbitControls
        enableZoom={false}
        enablePan={false}
        autoRotate
        autoRotateSpeed={0.65}
        maxPolarAngle={Math.PI * 0.82}
        minPolarAngle={Math.PI * 0.18}
      />
    </>
  )
}

// ── Export ───────────────────────────────────────────────────────────────────
export default function Brain3D({ concentration = 0.5, stress = 0.3, className = '' }) {
  return (
    <div className={`w-full h-full min-h-[300px] ${className}`}>
      <Canvas
        camera={{ position: [0, 0.3, 3.5], fov: 46 }}
        gl={{ antialias: true, alpha: true, toneMapping: THREE.ACESFilmicToneMapping }}
        style={{ background: 'transparent' }}
      >
        <BrainScene concentration={concentration} stress={stress} />
      </Canvas>
    </div>
  )
}
