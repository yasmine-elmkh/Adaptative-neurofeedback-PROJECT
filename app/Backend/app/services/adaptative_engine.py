"""
NeuroCap — Moteur d'Adaptation Dynamique
==========================================
Ce moteur différencie NeuroCap d'un neurofeedback générique (CdC Section 2.6).

Trois niveaux d'adaptation :
  1. TEMPS RÉEL (500ms) : lissage EWMA des features
  2. INTRA-SESSION (par bloc de 3 min) : ajustement des seuils (Mou et al., 2024)
  3. INTER-SESSIONS : recalibration quotidienne

Règle de Mou et al. (2024) — Zone 40-60% :
  - Taux succès > 60% → seuil +0.5 (augmenter le challenge)
  - Taux succès 40-60% → seuil inchangé (zone optimale d'apprentissage)
  - Taux succès < 40% → seuil −0.5 (réduire la difficulté)

Cette approche maintient l'utilisateur dans la zone de flow
(ni frustration, ni ennui) pour maximiser l'apprentissage.
"""

import numpy as np
from typing import Dict, Optional
from dataclasses import dataclass, field


@dataclass
class AdaptiveState:
    """
    État interne du moteur adaptatif pour une session en cours.
    Maintenu en mémoire pendant la durée de la session WebSocket.
    """
    # Seuil courant de feedback (ajusté dynamiquement)
    threshold: float = 0.5

    # Compteurs du bloc courant (3 min = ~360 epochs)
    block_successes: int = 0
    block_total: int = 0
    block_number: int = 0

    # EWMA des features (lissage temps réel)
    ewma_concentration: float = 50.0
    ewma_stress: float = 50.0
    ewma_tbr: float = 2.5
    ewma_ei: float = 0.5

    # Score cumulé de la session (0-100)
    session_score: float = 0.0
    session_total_success: int = 0
    session_total_epochs: int = 0

    # Palier de difficulté
    palier: str = "P1"

    # Historique pour les graphiques
    history: list = field(default_factory=list)


class AdaptiveEngine:
    """
    Moteur d'adaptation dynamique NeuroCap.
    Une instance par session WebSocket active.
    """

    # ── Constantes EWMA ──────────────────────────────────────────────
    # α = 0.3 → 30% nouveau + 70% historique (CdC Section 2.6)
    EWMA_ALPHA = 0.3

    # ── Constantes bloc ──────────────────────────────────────────────
    BLOCK_DURATION_EPOCHS = 360   # 3 min × 60 s × 2 epochs/s
    THRESHOLD_STEP = 0.5          # Pas d'ajustement du seuil
    THRESHOLD_MIN = 0.2           # Seuil minimum (jamais trop facile)
    THRESHOLD_MAX = 0.9           # Seuil maximum (jamais impossible)

    # ── Limites des paliers ──────────────────────────────────────────
    PALIERS = {
        "P1": {"min_threshold": 0.2, "max_threshold": 0.45},
        "P2": {"min_threshold": 0.40, "max_threshold": 0.60},
        "P3": {"min_threshold": 0.55, "max_threshold": 0.75},
        "P4": {"min_threshold": 0.70, "max_threshold": 0.90},
    }

    def __init__(self, initial_threshold: float = 0.5, palier: str = "P1"):
        """
        Initialise le moteur avec les paramètres du profil utilisateur.

        Paramètres :
            initial_threshold : seuil initial (depuis eeg_profiles.current_threshold)
            palier : palier initial (depuis eeg_profiles.palier)
        """
        self.state = AdaptiveState(
            threshold=initial_threshold,
            palier=palier,
        )

    def update(self, prediction: Dict) -> Dict:
        """
        Met à jour l'état adaptatif avec une nouvelle prédiction.

        Appelé toutes les 500ms par le WebSocket handler.

        Paramètres :
            prediction : sortie du classifieur
                {"concentration_rate": float, "stress_rate": float,
                 "confidence": float, "tbr": float, "ei": float}

        Retourne :
            État adaptatif mis à jour (seuil, score, feedback_active, etc.)
        """
        conc = prediction.get("concentration_rate", 50)
        stress = prediction.get("stress_rate", 50)
        confidence = prediction.get("confidence", 50)
        tbr = prediction.get("tbr", 2.5)
        ei = prediction.get("ei", 0.5)

        # ── 1. LISSAGE EWMA (temps réel) ────────────────────────────
        a = self.EWMA_ALPHA
        self.state.ewma_concentration = a * conc + (1 - a) * self.state.ewma_concentration
        self.state.ewma_stress = a * stress + (1 - a) * self.state.ewma_stress
        self.state.ewma_tbr = a * tbr + (1 - a) * self.state.ewma_tbr
        self.state.ewma_ei = a * ei + (1 - a) * self.state.ewma_ei

        # ── Déterminer si feedback actif ─────────────────────────────
        # Feedback suspendu si confiance < 60% (CdC Section 2.5.1)
        feedback_active = confidence >= 60.0

        # ── Déterminer le succès de cet epoch ────────────────────────
        # Succès = concentration normalisée > seuil adaptatif
        normalized_conc = conc / 100.0
        is_success = normalized_conc > self.state.threshold

        # Compteurs bloc
        self.state.block_total += 1
        self.state.session_total_epochs += 1
        if is_success:
            self.state.block_successes += 1
            self.state.session_total_success += 1

        # ── 2. AJUSTEMENT INTRA-SESSION (fin de bloc) ────────────────
        if self.state.block_total >= self.BLOCK_DURATION_EPOCHS:
            self._adjust_threshold()

        # ── Calcul du score de session ───────────────────────────────
        if self.state.session_total_epochs > 0:
            self.state.session_score = (
                self.state.session_total_success / self.state.session_total_epochs
            ) * 100

        return {
            "feedback_active": feedback_active,
            "threshold": self.state.threshold,
            "block_number": self.state.block_number,
            "session_score": round(self.state.session_score, 1),
            "palier": self.state.palier,
            "ewma_concentration": round(self.state.ewma_concentration, 1),
            "ewma_stress": round(self.state.ewma_stress, 1),
            "ewma_tbr": round(self.state.ewma_tbr, 3),
            "ewma_ei": round(self.state.ewma_ei, 3),
        }

    def _adjust_threshold(self):
        """
        Ajustement du seuil à la fin d'un bloc de 3 minutes.

        Règle de Mou et al. (2024) :
          > 60% succès → augmenter le seuil (plus difficile)
          40-60%       → zone optimale, ne rien changer
          < 40%        → diminuer le seuil (plus facile)

        Le seuil est contraint par les limites du palier courant.
        Si le seuil dépasse la limite haute du palier, on passe au palier suivant.
        """
        if self.state.block_total == 0:
            return

        success_rate = self.state.block_successes / self.state.block_total

        # Application de la règle 40-60%
        if success_rate > 0.60:
            self.state.threshold += self.THRESHOLD_STEP * 0.1
        elif success_rate < 0.40:
            self.state.threshold -= self.THRESHOLD_STEP * 0.1

        # Contraindre aux limites globales
        self.state.threshold = np.clip(
            self.state.threshold, self.THRESHOLD_MIN, self.THRESHOLD_MAX
        )

        # Vérifier progression de palier
        palier_limits = self.PALIERS.get(self.state.palier, {})
        max_thresh = palier_limits.get("max_threshold", 0.9)
        if self.state.threshold >= max_thresh:
            self._advance_palier()

        # Reset compteurs bloc
        self.state.block_successes = 0
        self.state.block_total = 0
        self.state.block_number += 1

    def _advance_palier(self):
        """Passe au palier suivant (P1 → P2 → P3 → P4)."""
        progression = {"P1": "P2", "P2": "P3", "P3": "P4"}
        next_palier = progression.get(self.state.palier)
        if next_palier:
            self.state.palier = next_palier
            # Réinitialiser le seuil au minimum du nouveau palier
            new_limits = self.PALIERS[next_palier]
            self.state.threshold = new_limits["min_threshold"]

    def get_recommendations(self) -> str:
        """
        Génère des recommandations textuelles à la fin de la session.
        Utilisées dans le rapport de session et par l'assistant RAG.
        """
        score = self.state.session_score

        if score >= 70:
            return (
                "Excellente session ! Votre concentration est bien au-dessus "
                "de la moyenne. Continuez avec des sessions plus longues ou "
                "passez au palier suivant pour maintenir le challenge."
            )
        elif score >= 50:
            return (
                "Bonne session. Votre taux de réussite est dans la zone optimale. "
                "Continuez à ce rythme, votre cerveau s'adapte progressivement."
            )
        elif score >= 30:
            return (
                "Session correcte mais le taux de réussite est un peu bas. "
                "Essayez de vous entraîner dans un environnement plus calme "
                "et assurez-vous que le casque est bien positionné."
            )
        else:
            return (
                "Session difficile. Ne vous découragez pas, les premières sessions "
                "sont souvent les plus dures. Vérifiez le placement des électrodes "
                "et essayez des sessions plus courtes (10-15 min)."
            )

    @staticmethod
    def compute_inter_session_threshold(
        long_term_avg: float,
        today_measured: float,
    ) -> float:
        """
        Recalibration inter-session (CdC Section 2.6, niveau 3).

        Formule : Seuil_jour = 0.70 × moyenne_long_terme + 0.30 × mesure_du_jour

        Cette pondération privilégie la tendance long terme (70%)
        tout en s'adaptant à l'état du jour (30%).
        """
        return 0.70 * long_term_avg + 0.30 * today_measured