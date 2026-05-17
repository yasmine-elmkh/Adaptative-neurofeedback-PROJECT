/**
 * =============================================================================
 * JEU INTERACTIF DE NEUROFEEDBACK
 * =============================================================================
 * Gameplay:
 * - Balle que l'utilisateur contrôle via l'alpha EEG
 * - Obstacles à éviter (représentent le stress)
 * - Points gagnés pour maintenir concentration élevée
 * 
 * Principes pédagogiques:
 * - Gamification pour maintenir l'engagement
 * - Feedback immédiat et motivant
 * - Difficulté adaptée au niveau de l'utilisateur
 */

import { useState, useEffect, useRef } from 'react';

export default function BiofeedbackGame({ concentration = 0.5, stress = 0.5 }) {
  const canvasRef = useRef(null);
  const [score, setScore] = useState(0);
  const gameStateRef = useRef({
    ballX: 250,
    ballY: 250,
    ballVelocityY: 0,
    obstacles: [],
    score: 0,
  });

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    const gameState = gameStateRef.current;

    // ===== CRÉATION DES OBSTACLES =====
    // Les obstacles représentent les tentations/stress
    const createObstacle = () => ({
      x: Math.random() * (canvas.width - 40),
      y: -40,
      width: 40,
      height: 40,
      speed: 3 + stress * 5, // Plus de stress = obstacles plus rapides
    });

    // Générer les obstacles initiaux
    if (gameState.obstacles.length === 0) {
      for (let i = 0; i < 3; i++) {
        gameState.obstacles.push({
          ...createObstacle(),
          y: Math.random() * canvas.height,
        });
      }
    }

    // ===== BOUCLE DE JEU =====
    let animationId;
    const gameLoop = () => {
      // Effacer le canvas
      ctx.fillStyle = '#0f172a';
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Contrôler la balle avec la concentration
      // Concentration élevée = la balle monte
      gameState.ballVelocityY = -(concentration - 0.5) * 8;
      gameState.ballY += gameState.ballVelocityY;

      // Limites du canvas
      gameState.ballY = Math.max(20, Math.min(canvas.height - 20, gameState.ballY));

      // Dessiner la balle
      ctx.fillStyle = '#10b981'; // vert
      ctx.beginPath();
      ctx.arc(gameState.ballX, gameState.ballY, 15, 0, Math.PI * 2);
      ctx.fill();

      // Dessiner et mettre à jour les obstacles
      ctx.fillStyle = '#ef4444'; // rouge
      gameState.obstacles = gameState.obstacles.filter((obs) => {
        obs.y += obs.speed;

        // Dessiner l'obstacle
        ctx.fillRect(obs.x, obs.y, obs.width, obs.height);

        // Détection de collision
        const ballLeft = gameState.ballX - 15;
        const ballRight = gameState.ballX + 15;
        const ballTop = gameState.ballY - 15;
        const ballBottom = gameState.ballY + 15;

        if (
          ballRight > obs.x &&
          ballLeft < obs.x + obs.width &&
          ballBottom > obs.y &&
          ballTop < obs.y + obs.height
        ) {
          // Collision détectée - perdre des points
          gameState.score = Math.max(0, gameState.score - 10);
          return false; // Supprimer l'obstacle
        }

        return obs.y < canvas.height;
      });

      // Créer de nouveaux obstacles
      if (Math.random() < 0.02) {
        gameState.obstacles.push(createObstacle());
      }

      // Augmenter le score si concentration reste élevée
      if (concentration > 0.7) {
        gameState.score += 1;
      }

      setScore(gameState.score);

      // Afficher le score
      ctx.fillStyle = '#ffffff';
      ctx.font = 'bold 20px Arial';
      ctx.fillText(`Score: ${gameState.score}`, 10, 30);

      // Afficher l'état du stress
      ctx.fillStyle = stress > 0.6 ? '#ef4444' : '#10b981';
      ctx.fillText(`Stress: ${(stress * 100).toFixed(0)}%`, 10, 60);

      animationId = requestAnimationFrame(gameLoop);
    };

    gameLoop();

    return () => cancelAnimationFrame(animationId);
  }, [concentration, stress]);

  return (
    <div className="flex flex-col items-center">
      <h3 className="text-xl font-bold mb-4">Focus Challenge</h3>
      <canvas
        ref={canvasRef}
        width={500}
        height={400}
        className="border-2 border-green-500 rounded-lg"
      />
      <p className="mt-4 text-sm text-gray-300">
        Maintenez votre concentration pour contrôler la balle verte.
        Évitez les obstacles rouges !
      </p>
      <p className="text-2xl font-bold mt-2">Score: {score}</p>
    </div>
  );
}