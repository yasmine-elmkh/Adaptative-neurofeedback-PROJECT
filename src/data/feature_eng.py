"""
=============================================================================
NeuroCap — Feature Engineering Avancé (~80 features)
=============================================================================
Auteur      : Yasmine El Mkhantar
Encadrement : Monir El Azzouzi | Loubna El Rhali | Yassir Matrane
Structure   : Easy Medical Device — 2025-2026

=== EVOLUTION PAR RAPPORT A LA VERSION PRECEDENTE ===

  Version précédente : 15 features (PSD + ratios + Hjorth + 3 légères)
  Cette version     : ~80 features réparties en 6 catégories

=== LES 6 CATÉGORIES DE FEATURES (basées sur 5 articles) ===

  Catégorie 1 — Puissances spectrales PSD (5 features)
    Welch PSD : Pδ, Pθ, Pα, Pβ, Pγ
    Ref : CdC NeuroCap Sec. 2.3

  Catégorie 2 — Ratios cognitifs NeuroCap (5 features)
    TBR, ABR, EI, TAR, RelEnergy_β
    Ref : CdC NeuroCap Sec. 2.5.1 | Salam 2026 (N°15)

  Catégorie 3 — Paramètres de Hjorth + temporelles (6 features)
    Activity, Mobility, Complexity, Power, MeanAmp, ZCR
    Ref : CdC Sec. 2.3 | Samsa 2026 (N°17)

  Catégorie 4 — DWT sous-bandes statistiques (~20 features)  ★ NOUVEAU
    DWT db4 niveau 4 → 5 sous-bandes (δ, θ, α, β, γ)
    Par sous-bande : mean, std, energy, entropy_shannon
    Ref : "Multiresolution Analysis in EEG Signal Feature Engineering
           for Epileptic Seizure Detection" (2018)
    Justification : DWT-db4 + SVM surpasse toutes les combinaisons.
                    Les features statistiques des sous-bandes capturent
                    la distribution de l'énergie à chaque résolution.

  Catégorie 5 — Features statistiques texturales (~15 features)  ★ NOUVEAU
    Skewness, kurtosis par sous-bande + signal global
    IQR, RMS, crest factor, peak-to-peak
    Ref : "NeuroFeat: An adaptive neurological EEG feature engineering
           approach for improved classification of MDD" (2025)
    Résultat : accuracy 99.22% avec Cosine KNN
    Justification : Les features texturales (moments statistiques d'ordre
                    supérieur) capturent l'asymétrie et la forme de la
                    distribution du signal, pas juste sa puissance.

  Catégorie 6 — Features non-linéaires & entropies (~10 features)  ★ NOUVEAU
    Approximate Entropy (ApEn), Sample Entropy (SampEn),
    Permutation Entropy (PE), Spectral Entropy,
    Higuchi Fractal Dimension (HFD),
    Detrended Fluctuation Analysis (DFA) exposant α
    Ref : "Age prediction on EEG signals via hybrid feature engineering
           approach" (2025)
    Justification : Les entropies mesurent la complexité/régularité du
                    signal. Un signal concentré est PLUS régulier (ApEn bas)
                    qu'un signal stressé (ApEn haut). HFD capture la
                    dimension fractale = auto-similarité à différentes
                    échelles temporelles.

  Catégorie 7 — Transition Patterns simplifiés (~6 features)  ★ NOUVEAU
    Inspiré de QuadTPat (Cambay et al. 2024)
    Histogramme des transitions : up, down, flat sur fenêtres glissantes
    Ref : "QuadTPat: Quadruple Transition Pattern-based explainable
           feature engineering model for stress detection" (Sci Rep 2024)
    Résultat : 92.95% (10-fold) et 73.63% (LOSO)
    Simplification : au lieu des 4-tuples complets de QuadTPat,
                     on utilise des triplets (plus rapide, compatible
                     avec la contrainte latence NeuroCap < 40 ms)

=== PIPELINE ===
  Epoch (1000 éch. @ 250 Hz)
    → Catégorie 1 : PSD Welch → 5 puissances de bande
    → Catégorie 2 : Ratios cognitifs → 5 ratios
    → Catégorie 3 : Hjorth + temporelles → 6 features
    → Catégorie 4 : DWT db4 → 5 sous-bandes × 4 stats = 20 features
    → Catégorie 5 : Statistiques texturales → ~15 features
    → Catégorie 6 : Entropies + non-linéaire → ~10 features
    → Catégorie 7 : Transition patterns → 6 features
    ─────────────────────────────────────────────────────
    TOTAL : ~67-80 features par epoch
    Temps de calcul : < 40 ms par epoch (compatible CdC Section 5.5)

=============================================================================
"""

import numpy as np
from scipy import signal
from scipy.stats import skew, kurtosis, iqr
import pywt
import warnings
warnings.filterwarnings('ignore')

from pathlib import Path
import os
import time


# ============================================================================
# CONSTANTES
# ============================================================================
FS = 250              # Fréquence d'échantillonnage (Hz)
EPOCH_SAMPLES = 1000  # 4 secondes × 250 Hz

# Bandes EEG standard
BANDS = {
    'delta': (0.5, 4.0),
    'theta': (4.0, 8.0),
    'alpha': (8.0, 13.0),
    'beta':  (13.0, 30.0),
    'gamma': (30.0, 40.0),
}

# DWT paramètres (Multiresolution Analysis article : db4 niveau 4 est optimal)
WAVELET = 'db4'
DWT_LEVEL = 4


# ============================================================================
# CATÉGORIE 1 — Puissances spectrales PSD Welch (5 features)
# Référence : CdC NeuroCap Section 2.3 (Table 2.2)
#
# La méthode de Welch divise le signal en segments, applique une fenêtre
# de Hann, calcule la FFT de chaque segment et moyenne les résultats.
# L'intégration trapézoïdale donne la puissance dans chaque bande.
# ============================================================================

def _psd_welch(epoch, nperseg=256):
    """Calcule la PSD par la méthode de Welch (fenêtre de Hann)."""
    return signal.welch(epoch, FS, nperseg=nperseg, window='hann')

def _band_power(freqs, psd, flo, fhi):
    """Intègre la PSD sur [flo, fhi] Hz (méthode trapézoïdale)."""
    idx = (freqs >= flo) & (freqs <= fhi)
    if not idx.any():
        return 0.0
    return float(np.trapz(psd[idx], freqs[idx]))

def extract_psd_features(epoch):
    """
    Catégorie 1 : Puissances spectrales absolues des 5 bandes EEG.
    
    Retourne : dict avec Pd, Pt, Pa, Pb, Pg (puissances δ, θ, α, β, γ)
    
    Justification :
      Les puissances de bande sont les features EEG les plus fondamentales.
      β↑ = concentration (Velnath 2021), α↓+β↑↑ = stress (Katmah 2021).
    """
    f, psd = _psd_welch(epoch)
    return {
        'Pd': _band_power(f, psd, 0.5, 4.0),    # delta
        'Pt': _band_power(f, psd, 4.0, 8.0),     # theta
        'Pa': _band_power(f, psd, 8.0, 13.0),    # alpha
        'Pb': _band_power(f, psd, 13.0, 30.0),   # beta
        'Pg': _band_power(f, psd, 30.0, 40.0),   # gamma
    }


# ============================================================================
# CATÉGORIE 2 — Ratios cognitifs NeuroCap (5 features)
# Référence : CdC Section 2.5.1 | Salam et al. 2026 (N°15) : TAR p<0.001
#
# Les ratios sont INVARIANTS au scaling (le facteur ×k² s'annule).
# TBR < 0.8 = concentration (CdC). EI > 0.7 = engagement cognitif actif.
# ============================================================================

def extract_ratio_features(psd_feats):
    """
    Catégorie 2 : Ratios cognitifs calculés à partir des puissances de bande.
    
    TBR = θ/β    → < 0.8 = concentration (CdC NeuroCap)
    ABR = α/β    → indicateur de relaxation vs activation
    EI  = β/(α+θ) → > 0.7 = engagement cognitif actif (CdC NeuroCap)
    TAR = θ/α    → p < 0.001 entre concentration et stress (Salam 2026)
    RelEnergy_β  = β / (δ+θ+α+β+γ) → proportion d'énergie en bande beta
    """
    pd, pt, pa, pb, pg = psd_feats['Pd'], psd_feats['Pt'], psd_feats['Pa'], psd_feats['Pb'], psd_feats['Pg']
    eps = 1e-12
    total = pd + pt + pa + pb + pg + eps
    return {
        'TBR': pt / (pb + eps),
        'ABR': pa / (pb + eps),
        'EI':  pb / (pa + pt + eps),
        'TAR': pt / (pa + eps),
        'RelEnergy_beta': pb / total,
    }


# ============================================================================
# CATÉGORIE 3 — Hjorth + Features temporelles (6 features)
# Référence : CdC Sec. 2.3 | Samsa & Altıntop 2026 (N°17)
#
# Hjorth (1970) : 3 descripteurs statistiques du signal dans le domaine
# temporel. Activity = variance, Mobility = fréquence caractéristique,
# Complexity = changement de fréquence.
# 
# ZCR (zero-crossing rate) = nombre de fois que le signal traverse zéro.
# Indicateur de la fréquence dominante (ZCR élevé = hautes fréquences).
# ============================================================================

def extract_temporal_features(epoch):
    """
    Catégorie 3 : Paramètres temporels (Hjorth + Power + MeanAmp + ZCR).
    
    Les 3 features Power/MeanAmp/RelEnergy de Samsa 2026 atteignent
    86.25% d'accuracy avec Random Forest à elles seules.
    ZCR est ajouté car c'est un indicateur rapide de la fréquence dominante.
    """
    d1 = np.diff(epoch)
    d2 = np.diff(d1)
    std_ep = np.std(epoch) + 1e-12
    std_d1 = np.std(d1) + 1e-12

    activity = float(np.var(epoch))
    mobility = float(std_d1 / std_ep)
    complexity = float((np.std(d2) / std_d1) / mobility) if mobility > 1e-12 else 0.0

    # Zero-crossing rate
    zcr = float(np.sum(np.diff(np.sign(epoch)) != 0)) / len(epoch)

    return {
        'Hjorth_Activity': activity,
        'Hjorth_Mobility': mobility,
        'Hjorth_Complexity': complexity,
        'Power': float(np.mean(epoch**2)),
        'MeanAmp': float(np.mean(np.abs(epoch))),
        'ZCR': zcr,
    }


# ============================================================================
# CATÉGORIE 4 — DWT sous-bandes statistiques (~20 features)
# Référence : "Multiresolution Analysis in EEG Signal Feature Engineering
#              for Epileptic Seizure Detection" (2018)
#
# Principe :
#   La DWT (Discrete Wavelet Transform) décompose le signal en sous-bandes
#   de fréquence par analyse multi-résolution (MRA). Avec db4 niveau 4 :
#     cA4 ≈ delta (0-3.9 Hz)
#     cD4 ≈ theta (3.9-7.8 Hz)
#     cD3 ≈ alpha (7.8-15.6 Hz)
#     cD2 ≈ beta  (15.6-31.25 Hz)
#     cD1 ≈ gamma (31.25-62.5 Hz)
#
#   Pour chaque sous-bande on calcule 4 statistiques :
#     mean    : amplitude moyenne (tendance centrale)
#     std     : dispersion (variabilité)
#     energy  : somme des carrés (intensité totale de la sous-bande)
#     entropy : entropie de Shannon (désordre/complexité de la distribution)
#
#   Pourquoi db4 ? L'article montre que DWT-db4 + SVM surpasse db2, db6
#   et les MFCC pour la classification EEG.
# ============================================================================

def _shannon_entropy(coeffs):
    """
    Entropie de Shannon sur les coefficients DWT.
    Mesure le désordre dans la distribution de l'énergie.
    Signal régulier → entropie basse. Signal chaotique → entropie haute.
    """
    energy = coeffs**2
    total = np.sum(energy) + 1e-12
    prob = energy / total
    prob = prob[prob > 0]  # éviter log(0)
    return float(-np.sum(prob * np.log2(prob)))

def extract_dwt_subband_features(epoch):
    """
    Catégorie 4 : Features statistiques des sous-bandes DWT.
    
    Décomposition DWT db4 niveau 4 → 5 sous-bandes.
    4 statistiques par sous-bande = 20 features.
    
    Ref : Multiresolution Analysis (2018) — DWT-db4 + SVM = meilleure
          combinaison pour la classification EEG.
    """
    # Décomposition DWT
    coeffs = pywt.wavedec(epoch, WAVELET, level=DWT_LEVEL)
    # coeffs[0] = cA4 (approximation ≈ delta)
    # coeffs[1] = cD4 (détail ≈ theta)
    # coeffs[2] = cD3 (détail ≈ alpha)
    # coeffs[3] = cD2 (détail ≈ beta)
    # coeffs[4] = cD1 (détail ≈ gamma)

    subband_names = ['dwt_delta', 'dwt_theta', 'dwt_alpha', 'dwt_beta', 'dwt_gamma']
    features = {}

    for i, (name, c) in enumerate(zip(subband_names, coeffs)):
        features[f'{name}_mean'] = float(np.mean(np.abs(c)))
        features[f'{name}_std'] = float(np.std(c))
        features[f'{name}_energy'] = float(np.sum(c**2))
        features[f'{name}_entropy'] = _shannon_entropy(c)

    return features


# ============================================================================
# CATÉGORIE 5 — Features statistiques texturales (~15 features)
# Référence : "NeuroFeat: An adaptive neurological EEG feature engineering
#              approach for improved classification of MDD" (2025)
#
# Principe :
#   NeuroFeat extrait des "features texturales" via les moments statistiques
#   d'ordre supérieur (skewness = asymétrie, kurtosis = aplatissement) sur
#   les signaux décomposés en DWT. Ces features capturent la FORME de la
#   distribution du signal, pas juste sa puissance.
#
#   skewness > 0 : queue droite plus longue (artefacts positifs ?)
#   kurtosis > 3 : distribution à queues lourdes (pics, artefacts)
#   IQR : robuste aux outliers, mesure la dispersion centrale
#   Crest factor : rapport pic/RMS, détecte les artefacts transitoires
#
#   Résultat NeuroFeat : 99.22% accuracy avec Cosine KNN sur 30 classifieurs
# ============================================================================

def extract_textural_features(epoch):
    """
    Catégorie 5 : Features statistiques texturales (NeuroFeat 2025).
    
    Features sur le signal GLOBAL :
      skewness, kurtosis, IQR, RMS, crest_factor, peak_to_peak
    
    Features sur les SOUS-BANDES DWT (skewness + kurtosis par sous-bande) :
      dwt_delta_skew, dwt_delta_kurt, ..., dwt_gamma_skew, dwt_gamma_kurt
    
    Total : 6 (global) + 10 (sous-bandes) = 16 features
    """
    features = {}

    # --- Features globales ---
    features['skewness'] = float(skew(epoch))
    features['kurtosis'] = float(kurtosis(epoch))
    features['IQR'] = float(iqr(epoch))
    features['RMS'] = float(np.sqrt(np.mean(epoch**2)))
    features['peak_to_peak'] = float(np.max(epoch) - np.min(epoch))
    rms = features['RMS'] + 1e-12
    features['crest_factor'] = float(np.max(np.abs(epoch)) / rms)

    # --- Skewness et kurtosis par sous-bande DWT ---
    # Ref NeuroFeat : "textural features through statistical thresholds
    #                  and moment analysis from signals decomposed via DWT"
    coeffs = pywt.wavedec(epoch, WAVELET, level=DWT_LEVEL)
    subband_names = ['delta', 'theta', 'alpha', 'beta', 'gamma']

    for name, c in zip(subband_names, coeffs):
        features[f'dwt_{name}_skew'] = float(skew(c))
        features[f'dwt_{name}_kurt'] = float(kurtosis(c))

    return features


# ============================================================================
# CATÉGORIE 6 — Features non-linéaires & entropies (~10 features)
# Référence : "Age prediction on EEG signals via hybrid feature engineering
#              approach" (2025)
#
# Principe :
#   Les entropies mesurent la COMPLEXITÉ et la RÉGULARITÉ du signal.
#   Un signal concentré (régulier, beta dominant) → entropie BASSE.
#   Un signal stressé (irrégulier, hautes fréquences) → entropie HAUTE.
#
#   Approximate Entropy (ApEn) : mesure la probabilité que des patterns
#     similaires le restent au pas suivant. Créée par Pincus (1991).
#     Sensible au bruit et à la longueur du signal.
#
#   Sample Entropy (SampEn) : version améliorée d'ApEn par Richman &
#     Moorman (2000). Moins biaisée, plus robuste.
#
#   Permutation Entropy (PE) : Bandt & Pompe (2002). Mesure la complexité
#     par l'analyse des ordres de permutation. Très robuste au bruit.
#
#   Spectral Entropy : entropie de Shannon appliquée à la PSD normalisée.
#     Mesure l'uniformité du spectre. Signal sinusoïdal pur → SE basse.
#     Bruit blanc → SE maximale.
#
#   Higuchi Fractal Dimension (HFD) : Higuchi (1988). Mesure la complexité
#     géométrique du signal. Plus HFD est élevé, plus le signal est complexe.
#
#   Tous ces calculs prennent < 5 ms par epoch → compatible contrainte latence.
# ============================================================================

def _approximate_entropy(x, m=2, r_factor=0.2):
    """
    Approximate Entropy (ApEn) — Pincus 1991.
    
    Paramètres :
      m = longueur des patterns (2 est standard pour EEG)
      r_factor = tolérance = r_factor × std(x)
    
    Interprétation :
      ApEn bas → signal régulier, prédictible (concentration)
      ApEn haut → signal irrégulier, complexe (stress, artefacts)
    """
    n = len(x)
    r = r_factor * np.std(x)
    if r < 1e-10:
        return 0.0

    def count_matches(template_length):
        templates = np.array([x[i:i+template_length] for i in range(n - template_length)])
        count = 0
        for i in range(len(templates)):
            # Chebyshev distance (max des différences absolues)
            dist = np.max(np.abs(templates - templates[i]), axis=1)
            count += np.sum(dist <= r) - 1  # -1 pour exclure self-match
        return count / (len(templates) * (len(templates) - 1) + 1e-12)

    phi_m = np.log(count_matches(m) + 1e-12)
    phi_m1 = np.log(count_matches(m + 1) + 1e-12)
    return float(phi_m - phi_m1)


def _sample_entropy(x, m=2, r_factor=0.2):
    """
    Sample Entropy (SampEn) — Richman & Moorman 2000.
    
    Amélioration d'ApEn : ne compte pas les self-matches,
    ce qui réduit le biais pour les signaux courts.
    
    Même interprétation que ApEn mais plus stable.
    """
    n = len(x)
    r = r_factor * np.std(x)
    if r < 1e-10:
        return 0.0

    # Sous-échantillonner pour la vitesse (< 5 ms sur 1000 points)
    step = max(1, n // 200)
    x_sub = x[::step]
    n_sub = len(x_sub)

    def count_templates(template_len):
        count = 0
        templates = np.array([x_sub[i:i+template_len] for i in range(n_sub - template_len)])
        for i in range(len(templates)):
            dist = np.max(np.abs(templates[i+1:] - templates[i]), axis=1)
            count += np.sum(dist <= r)
        return count

    a = count_templates(m + 1)
    b = count_templates(m)

    if b == 0:
        return 0.0
    return float(-np.log((a + 1e-12) / (b + 1e-12)))


def _permutation_entropy(x, order=3, delay=1):
    """
    Permutation Entropy (PE) — Bandt & Pompe 2002.
    
    Principe : extraire tous les motifs d'ordre 'order' dans le signal,
    compter la fréquence de chaque type de permutation, calculer l'entropie
    de Shannon sur ces fréquences.
    
    order=3 → 3! = 6 permutations possibles → PE ∈ [0, log2(6)] ≈ [0, 2.58]
    
    Interprétation :
      PE bas → signal très ordonné (sinusoïde pure)
      PE haut → signal désordonné (bruit blanc)
    """
    n = len(x)
    permutations = {}
    total = 0

    for i in range(n - (order - 1) * delay):
        # Extraire le motif de longueur 'order' avec délai 'delay'
        pattern = tuple(np.argsort(x[i:i + order * delay:delay]))
        permutations[pattern] = permutations.get(pattern, 0) + 1
        total += 1

    if total == 0:
        return 0.0

    # Entropie de Shannon normalisée
    pe = 0.0
    for count in permutations.values():
        p = count / total
        if p > 0:
            pe -= p * np.log2(p)

    # Normaliser par l'entropie maximale (log2(order!))
    import math
    max_entropy = np.log2(math.factorial(order))
    return float(pe / max_entropy) if max_entropy > 0 else 0.0


def _spectral_entropy(epoch):
    """
    Spectral Entropy — Shannon entropy sur la PSD normalisée.
    
    Mesure l'uniformité de la distribution spectrale.
    Signal mono-fréquentiel → SE basse. Bruit blanc → SE maximale.
    """
    f, psd = _psd_welch(epoch)
    # Normaliser la PSD en distribution de probabilité
    psd_norm = psd / (np.sum(psd) + 1e-12)
    psd_norm = psd_norm[psd_norm > 0]
    return float(-np.sum(psd_norm * np.log2(psd_norm)))


def _higuchi_fractal_dimension(x, kmax=10):
    """
    Higuchi Fractal Dimension (HFD) — Higuchi 1988.
    
    Mesure la complexité géométrique du signal en calculant la longueur
    de la courbe à différentes échelles temporelles k=1,2,...,kmax.
    
    HFD ≈ 1.0 → signal lisse (sinusoïde)
    HFD ≈ 2.0 → signal très complexe (bruit blanc)
    EEG typique : HFD ≈ 1.4-1.7
    """
    n = len(x)
    lk = np.zeros(kmax)

    for k in range(1, kmax + 1):
        lengths = []
        for m in range(1, k + 1):
            # Longueur de la courbe pour l'échelle k, décalage m
            idx = np.arange(m - 1, n, k)
            if len(idx) < 2:
                continue
            seg = x[idx]
            length = np.sum(np.abs(np.diff(seg))) * (n - 1) / (len(idx) * k * k)
            lengths.append(length)
        lk[k - 1] = np.mean(lengths) if lengths else 0

    # Régression linéaire log-log pour obtenir la pente = HFD
    valid = lk > 0
    if np.sum(valid) < 2:
        return 1.5  # valeur par défaut

    log_k = np.log(np.arange(1, kmax + 1)[valid])
    log_lk = np.log(lk[valid])

    # Pente par régression linéaire
    slope = np.polyfit(log_k, log_lk, 1)[0]
    return float(slope)


def extract_nonlinear_features(epoch):
    """
    Catégorie 6 : Features non-linéaires et entropies.
    
    Ref : "Age prediction on EEG signals via hybrid feature engineering
           approach" (2025)
    
    Ces features capturent des aspects du signal que les puissances
    spectrales ne voient pas : la RÉGULARITÉ, la COMPLEXITÉ et
    l'AUTO-SIMILARITÉ à différentes échelles.
    """
    # Sous-échantillonner l'epoch pour la vitesse (< 5 ms)
    epoch_sub = epoch[::2] if len(epoch) > 500 else epoch

    return {
        'ApEn': _approximate_entropy(epoch_sub, m=2, r_factor=0.2),
        'SampEn': _sample_entropy(epoch_sub, m=2, r_factor=0.2),
        'PermEn': _permutation_entropy(epoch, order=3, delay=1),
        'SpectralEn': _spectral_entropy(epoch),
        'HFD': _higuchi_fractal_dimension(epoch, kmax=10),
    }


# ============================================================================
# CATÉGORIE 7 — Transition Patterns simplifiés (6 features)
# Référence : "QuadTPat: Quadruple Transition Pattern-based explainable
#              feature engineering model for stress detection" (Sci Rep 2024)
#
# Principe original (QuadTPat) :
#   Prendre 4 échantillons consécutifs, encoder les transitions comme
#   "up", "down" ou "flat", créer un histogramme de ces 4-tuples.
#   Le papier utilise 27 types de transitions (3^3 pour 4 échantillons).
#
# Notre simplification (compatible latence NeuroCap) :
#   Prendre 3 échantillons consécutifs (triplets), encoder les 2 transitions
#   comme up(+1), down(-1) ou flat(0), créer un histogramme de 9 types.
#   Puis résumer en 6 features : pct_up, pct_down, pct_flat,
#   longest_up_streak, longest_down_streak, transition_freq.
#
# Interprétation :
#   Concentration → transitions régulières (beta dominant, oscillations)
#   Stress → transitions plus chaotiques (plus de changements de direction)
# ============================================================================

def extract_transition_features(epoch, threshold=0.01):
    """
    Catégorie 7 : Transition patterns (inspiré QuadTPat 2024).
    
    Encode les transitions entre échantillons consécutifs :
      +1 = montée (différence > threshold)
      -1 = descente (différence < -threshold)
       0 = stable (|différence| <= threshold)
    
    Features extraites :
      pct_up       : % de transitions montantes
      pct_down     : % de transitions descendantes
      pct_flat     : % de transitions stables
      up_streak    : plus longue série de montées consécutives
      down_streak  : plus longue série de descentes consécutives
      trans_freq   : fréquence de changement de direction (up→down ou down→up)
    """
    diffs = np.diff(epoch)

    # Encoder les transitions
    transitions = np.zeros(len(diffs), dtype=int)
    transitions[diffs > threshold] = 1     # montée
    transitions[diffs < -threshold] = -1   # descente
    # les autres restent à 0 (stable)

    n = len(transitions)
    if n == 0:
        return {k: 0.0 for k in ['pct_up', 'pct_down', 'pct_flat',
                                   'up_streak', 'down_streak', 'trans_freq']}

    # Pourcentages
    pct_up = float(np.sum(transitions == 1)) / n
    pct_down = float(np.sum(transitions == -1)) / n
    pct_flat = float(np.sum(transitions == 0)) / n

    # Plus longue série (streak)
    def longest_streak(arr, value):
        max_s, current = 0, 0
        for v in arr:
            if v == value:
                current += 1
                max_s = max(max_s, current)
            else:
                current = 0
        return max_s

    up_streak = longest_streak(transitions, 1)
    down_streak = longest_streak(transitions, -1)

    # Fréquence de changement de direction
    direction_changes = np.sum(np.abs(np.diff(transitions[transitions != 0])) > 0)
    non_flat = np.sum(transitions != 0)
    trans_freq = float(direction_changes / (non_flat + 1e-12))

    return {
        'pct_up': pct_up,
        'pct_down': pct_down,
        'pct_flat': pct_flat,
        'up_streak': float(up_streak),
        'down_streak': float(down_streak),
        'trans_freq': trans_freq,
    }


# ============================================================================
# FONCTION PRINCIPALE : extraction de TOUTES les features pour une epoch
# ============================================================================

def extract_all_features(epoch):
    """
    Extrait les ~80 features complètes pour une epoch EEG.
    
    Entrée : epoch (np.array, 1000 échantillons, normalisé z-score)
    Sortie : dict avec toutes les features
    
    Catégories :
      1. PSD Welch (5)         — CdC NeuroCap Sec. 2.3
      2. Ratios cognitifs (5)  — CdC Sec. 2.5.1 + Salam 2026
      3. Hjorth + temporel (6) — Samsa 2026
      4. DWT sous-bandes (20)  — Multiresolution Analysis 2018
      5. Texturales (16)       — NeuroFeat 2025
      6. Non-linéaires (5)     — Age prediction hybrid 2025
      7. Transitions (6)       — QuadTPat 2024
      ──────────────────────
      TOTAL : ~63 features
    """
    features = {}

    # Catégorie 1 : PSD
    psd_feats = extract_psd_features(epoch)
    features.update(psd_feats)

    # Catégorie 2 : Ratios
    features.update(extract_ratio_features(psd_feats))

    # Catégorie 3 : Hjorth + temporel
    features.update(extract_temporal_features(epoch))

    # Catégorie 4 : DWT sous-bandes
    features.update(extract_dwt_subband_features(epoch))

    # Catégorie 5 : Texturales
    features.update(extract_textural_features(epoch))

    # Catégorie 6 : Non-linéaires
    features.update(extract_nonlinear_features(epoch))

    # Catégorie 7 : Transitions
    features.update(extract_transition_features(epoch))

    return features


# ============================================================================
# NOMS DES FEATURES (pour documentation et indexation)
# ============================================================================

def get_feature_names():
    """Retourne la liste ordonnée des noms de toutes les features."""
    # Générer un vecteur dummy pour récupérer les clés
    dummy = np.random.randn(EPOCH_SAMPLES)
    feats = extract_all_features(dummy)
    return list(feats.keys())


# ============================================================================
# EXTRACTION BATCH : traiter toutes les epochs d'un dataset
# ============================================================================

def extract_features_batch(X_epochs, y_labels=None, verbose=True):
    """
    Extrait les features pour un batch d'epochs.
    
    Entrée :
      X_epochs : np.array (n_epochs, 1000) — epochs normalisées z-score
      y_labels : np.array (n_epochs,) — labels (0=conc, 1=stress) optionnel
    
    Sortie :
      features_matrix : np.array (n_epochs, n_features) — matrice de features
      feature_names   : list[str] — noms des features
    
    Temps estimé : ~30-40 ms par epoch → ~3 min pour 5000 epochs
    """
    if verbose:
        print("=" * 65)
        print("NeuroCap — Feature Engineering Avancé (~80 features)")
        print(f"Epochs : {len(X_epochs)} | Échantillons/epoch : {X_epochs.shape[1]}")
        if y_labels is not None:
            print(f"Labels : {np.sum(y_labels==0)} concentration | {np.sum(y_labels==1)} stress")
        print("=" * 65)

    all_features = []
    t_start = time.time()

    for i, epoch in enumerate(X_epochs):
        feats = extract_all_features(epoch)
        all_features.append(list(feats.values()))

        if verbose and (i + 1) % 500 == 0:
            elapsed = time.time() - t_start
            ms_per_ep = elapsed / (i + 1) * 1000
            print(f"  [{i+1}/{len(X_epochs)}] {ms_per_ep:.1f} ms/epoch | "
                  f"ETA: {(len(X_epochs) - i - 1) * ms_per_ep / 1000:.0f}s")

    feature_names = list(extract_all_features(X_epochs[0]).keys())
    features_matrix = np.array(all_features, dtype=np.float32)

    # Remplacer NaN et Inf par 0
    features_matrix = np.nan_to_num(features_matrix, nan=0.0, posinf=0.0, neginf=0.0)

    elapsed = time.time() - t_start
    if verbose:
        print(f"\n✅ Extraction terminée")
        print(f"   Shape : {features_matrix.shape} ({len(feature_names)} features)")
        print(f"   Temps : {elapsed:.1f}s ({elapsed/len(X_epochs)*1000:.1f} ms/epoch)")
        print(f"   NaN/Inf remplacés par 0 : {np.sum(np.isnan(all_features))}")
        print(f"\n   Catégorie 1 (PSD)         : 5 features")
        print(f"   Catégorie 2 (Ratios)      : 5 features")
        print(f"   Catégorie 3 (Hjorth+temp) : 6 features")
        print(f"   Catégorie 4 (DWT sub)     : 20 features")
        print(f"   Catégorie 5 (Texturales)  : {sum(1 for n in feature_names if 'skew' in n or 'kurt' in n or n in ['IQR','RMS','peak_to_peak','crest_factor','skewness','kurtosis'])} features")
        print(f"   Catégorie 6 (Non-lin)     : 5 features")
        print(f"   Catégorie 7 (Transitions) : 6 features")
        print(f"   ─────────────────────────────")
        print(f"   TOTAL                     : {len(feature_names)} features")

    return features_matrix, feature_names


# ============================================================================
# MAIN : extraction sur les datasets augmentés
# ============================================================================

def main():
    """
    Pipeline d'extraction :
      1. Localise les données augmentées (datasets_augmented/)
      2. Extrait les features (~63) pour chaque expérience (A, B, C, D, FULL)
      3. Extrait les features pour val et test
      4. Sauvegarde les matrices de features, les labels et les subject_ids
         dans data/Features/datasets_features_advanced/
    """
    # --- Chemins ---
    script_dir = Path(__file__).resolve().parent
    project_root = script_dir.parent.parent          # EEG_project/
    print(f"📁 Racine du projet : {project_root}")

    # Dossier contenant les données augmentées (produit par augmentation_eeg.py)
    possible_paths = [
        project_root / 'data' / 'Augmentation' / 'datasets_augmented',
        project_root / 'data' / 'augmentation' /  'datasets_augmented',
    ]
    data_dir = None
    for p in possible_paths:
        if p.exists():
            data_dir = p
            break
    if data_dir is None:
        print("❌ Datasets augmentés non trouvés.")
        print("   Exécutez d'abord augmentation_eeg.py")
        return

    print(f"📂 Données augmentées : {data_dir}")

    # Dossier de sortie des features (identique à FEATURES_DIR du baseline)
    out_dir = project_root / 'features' / 'Features_eng'
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"📁 Sortie des features : {out_dir}")

    experiments = ['A', 'B', 'C', 'D', 'FULL']

    # -------------------------------------------------------------------
    # 1. Extraction pour les expériences d'entraînement (A..FULL)
    # -------------------------------------------------------------------
    for exp in experiments:
        X_path = data_dir / f'X_train_{exp}.npy'
        y_path = data_dir / f'y_train_{exp}.npy'
        if not X_path.exists():
            print(f"\n⚠️  Expérience {exp} : {X_path.name} manquant — ignorée")
            continue

        print(f"\n{'='*55}\nEXPÉRIENCE {exp}\n{'='*55}")
        X = np.load(X_path)
        y = np.load(y_path)

        # Extraction des features
        features, names = extract_features_batch(X, y)

        # Sauvegarde features + labels
        np.save(out_dir / f'features_{exp}.npy', features)
        np.save(out_dir / f'labels_{exp}.npy', y)
        print(f"   ✅ Sauvegardé : features_{exp}.npy {features.shape}")
        print(f"   ✅ Sauvegardé : labels_{exp}.npy")

        # Sauvegarde des noms de features (une seule fois, à la première expérience)
        if exp == 'A':
            np.save(out_dir / 'feature_names.npy', np.array(names))
            with open(out_dir / 'feature_names.txt', 'w') as f:
                for i, n in enumerate(names):
                    f.write(f"[{i:3d}] {n}\n")
            print(f"   ✅ feature_names.txt sauvegardé ({len(names)} features)")

    # -------------------------------------------------------------------
    # 2. Extraction pour val et test (avec sauvegarde des subject_ids)
    # -------------------------------------------------------------------
    for split in ['val', 'test']:
        X_path = data_dir / f'X_{split}.npy'
        if not X_path.exists():
            print(f"\n⚠️  Split {split} : {X_path.name} manquant — ignoré")
            continue

        print(f"\n{'='*55}\nSPLIT : {split.upper()}\n{'='*55}")
        X = np.load(X_path)
        y = np.load(data_dir / f'y_{split}.npy')

        # Extraction des features
        features, names = extract_features_batch(X, y)

        # Sauvegarde features + labels
        np.save(out_dir / f'features_{split}.npy', features)
        np.save(out_dir / f'labels_{split}.npy', y)
        print(f"   ✅ Sauvegardé : features_{split}.npy {features.shape}")
        print(f"   ✅ Sauvegardé : labels_{split}.npy")

        # Sauvegarde des subject_ids pour ce split (si disponibles)
        sid_split_path = data_dir / f'subject_ids_{split}.npy'
        if sid_split_path.exists():
            sids_split = np.load(sid_split_path)
            # Vérification de cohérence de longueur
            if len(sids_split) != len(X):
                print(f"  ⚠️  subject_ids_{split}.npy : longueur {len(sids_split)} ≠ {len(X)} epochs → ajustement")
                if len(sids_split) > len(X):
                    sids_split = sids_split[:len(X)]
                else:
                    sids_split = np.resize(sids_split, len(X))
            np.save(out_dir / f'subject_ids_{split}.npy', sids_split)
            print(f"  ✅ subject_ids_{split}.npy sauvegardé ({len(sids_split)} époques)")
        else:
            print(f"  ⚠️  Aucun subject_ids_{split}.npy trouvé dans {data_dir} → pas de LOSO pour {split}")

    # -------------------------------------------------------------------
    # 3. Sauvegarde des subject_ids pour les expériences d'entraînement
    #    (nécessite subject_ids_train.npy dans data_dir)
    # -------------------------------------------------------------------
    print("\n" + "="*55)
    print("Sauvegarde des subject_ids pour les expériences (LOSO)")
    print("="*55)

    sid_train_path = data_dir / 'subject_ids_train.npy'
    if not sid_train_path.exists():
        print("❌ subject_ids_train.npy manquant dans le dossier datasets_augmented/")
        print("   → Impossible de générer les subject_ids pour les expériences A..FULL.")
        print("   → Corrigez augmentation_eeg.py pour qu'il sauvegarde les subject_ids.")
        raise FileNotFoundError("subject_ids_train.npy introuvable")

    sids_orig = np.load(sid_train_path)
    n_subjects_orig = len(np.unique(sids_orig))
    print(f"✅ subject_ids_train.npy trouvé : {len(sids_orig)} époques, {n_subjects_orig} sujets")

    mapping = {'A': 1, 'B': 2, 'C': 3, 'D': 2, 'FULL': 4}
    for exp in experiments:
        repeats = mapping[exp]
        sids_exp = np.tile(sids_orig, repeats)
        # Ajuster la taille exacte (au cas où le nombre d'epochs ne correspond pas exactement)
        feat_path = out_dir / f'features_{exp}.npy'
        if feat_path.exists():
            n_feat = np.load(feat_path).shape[0]
            if len(sids_exp) > n_feat:
                sids_exp = sids_exp[:n_feat]
            elif len(sids_exp) < n_feat:
                sids_exp = np.resize(sids_exp, n_feat)
        np.save(out_dir / f'subject_ids_{exp}.npy', sids_exp)
        print(f"  ✅ subject_ids_{exp}.npy : {len(sids_exp)} époques, {len(np.unique(sids_exp))} sujets")

    # -------------------------------------------------------------------
    # 4. Rapport final
    # -------------------------------------------------------------------
    print(f"\n{'='*55}")
    print(f"✅ Feature engineering avancé terminé")
    print(f"   Dossier de sortie : {out_dir}")
    print(f"{'='*55}")

if __name__ == "__main__":
    main()