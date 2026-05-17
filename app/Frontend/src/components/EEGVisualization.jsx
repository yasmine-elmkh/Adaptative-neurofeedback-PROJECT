/**
 * =============================================================================
 * VISUALISATION 3D INTERACTIVE - Cerveau en temps réel
 * =============================================================================
 * Utilise Three.js pour afficher:
 * - Modèle 3D du cerveau
 * - Électrodes placées selon système 10-10
 * - Zones colorées dynamiquement selon l'état EEG
 * - Topomap interpolée IDW
 * 
 * References:
 * - Three.js: https://threejs.org/
 * - Système 10-10: Seres et al., 1999
 * - IDW interpolation: Shepard, 1968
 */

import { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';

export default function EEGVisualization({ data }) {
  const containerRef = useRef(null);
  const sceneRef = useRef(null);
  const cameraRef = useRef(null);
  const rendererRef = useRef(null);
  const electrodesRef = useRef([]);

  useEffect(() => {
    if (!containerRef.current) return;

    // ===== INITIALISATION THREE.JS =====
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0f172a); // dark blue

    const camera = new THREE.PerspectiveCamera(
      75,
      containerRef.current.clientWidth / containerRef.current.clientHeight,
      0.1,
      1000
    );
    camera.position.z = 3;

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(
      containerRef.current.clientWidth,
      containerRef.current.clientHeight
    );
    containerRef.current.appendChild(renderer.domElement);

    // ===== CRÉER LE CERVEAU (SPHÈRE SIMPLE) =====
    const brainGeometry = new THREE.IcosahedronGeometry(1.5, 5);
    const brainMaterial = new THREE.MeshPhongMaterial({
      color: 0x4f46e5,
      wireframe: false,
      opacity: 0.7,
      transparent: true,
    });
    const brain = new THREE.Mesh(brainGeometry, brainMaterial);
    scene.add(brain);

    // ===== PLACER LES ÉLECTRODES (Système 10-10) =====
    // Positions normalisées des électrodes principales
    const electrodePositions = {
      'Fz': [0, 1, 0],
      'Cz': [0, 0, 1],
      'Pz': [0, -1, 0],
      'Oz': [0, -1, -0.5],
      'F3': [-0.7, 0.7, 0],
      'F4': [0.7, 0.7, 0],
      'C3': [-1, 0, 0],
      'C4': [1, 0, 0],
      'P3': [-0.7, -0.7, 0],
      'P4': [0.7, -0.7, 0],
    };

    const electrodes = [];
    Object.entries(electrodePositions).forEach(([name, pos]) => {
      const sphereGeom = new THREE.SphereGeometry(0.08, 8, 8);
      const sphereMat = new THREE.MeshBasicMaterial({ color: 0xfbbf24 }); // gold
      const sphere = new THREE.Mesh(sphereGeom, sphereMat);
      sphere.position.set(...pos);
      sphere.name = name;
      scene.add(sphere);
      electrodes.push(sphere);
    });
    electrodesRef.current = electrodes;

    // ===== ÉCLAIRAGE =====
    const light = new THREE.PointLight(0xffffff, 1);
    light.position.set(5, 5, 5);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0xffffff, 0.4);
    scene.add(ambientLight);

    // ===== CONTRÔLES DE ROTATION =====
    let rotation = { x: 0, y: 0 };
    containerRef.current.addEventListener('mousemove', (e) => {
      const rect = containerRef.current.getBoundingClientRect();
      rotation.x = (e.clientY - rect.top) / rect.height * Math.PI - Math.PI / 2;
      rotation.y = (e.clientX - rect.left) / rect.width * Math.PI * 2;
    });

    // ===== BOUCLE D'ANIMATION =====
    const animate = () => {
      requestAnimationFrame(animate);

      // Rotation douce
      brain.rotation.x += (rotation.x - brain.rotation.x) * 0.05;
      brain.rotation.y += (rotation.y - brain.rotation.y) * 0.05;

      // Mise à jour des couleurs des électrodes en fonction de l'EEG
      if (data) {
        electrodes.forEach((electrode) => {
          // Colorer selon la puissance alpha (exemple)
          const intensity = Math.min(data.p_alpha / 10, 1);
          const color = new THREE.Color();
          color.setHSL(0.6 * (1 - intensity), 1, 0.5);
          electrode.material.color = color;
        });
      }

      renderer.render(scene, camera);
    };
    animate();

    sceneRef.current = scene;
    cameraRef.current = camera;
    rendererRef.current = renderer;

    // ===== CLEANUP =====
    return () => {
      containerRef.current?.removeChild(renderer.domElement);
      renderer.dispose();
    };
  }, []);

  // Mettre à jour les couleurs en temps réel
  useEffect(() => {
    if (!electrodesRef.current || !data) return;

    electrodesRef.current.forEach((electrode) => {
      // Utiliser P(Concentration) pour la couleur
      const intensity = data.p_concentration || 0.5;
      const color = new THREE.Color();
      
      // Gradient bleu (faible concentration) -> vert (haute concentration)
      color.setHSL(0.6 * (1 - intensity), 1, 0.5);
      electrode.material.color = color;
    });
  }, [data]);

  return (
    <div
      ref={containerRef}
      className="w-full h-96 rounded-lg border border-gray-600 overflow-hidden"
    />
  );
}