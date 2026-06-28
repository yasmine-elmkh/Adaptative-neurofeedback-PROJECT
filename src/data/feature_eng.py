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
           for Epileptic Seizure Detection" (2018) — FE-2
    Justification : DWT-db4 + SVM surpasse toutes les combinaisons.
                    Les features statistiques des sous-bandes capturent
                    la distribution de l'énergie à chaque résolution.

  Catégorie 5 — Features statistiques texturales (~20 features)  ★ ENRICHI
    Skewness, kurtosis par sous-bande + signal global
    IQR, RMS, crest factor, peak-to-peak
    + median, max_val, min_val, MAD  ← ajoutés depuis FE-4
    Ref : "NeuroFeat: An adaptive neurological EEG feature engineering
           approach for improved classification of MDD" (2026) — FE-4
    23 features statistiques : mean, std, variance, médiane, max, min,
    range, RMS, énergie, AM, entropies Shannon/Log, kurtosis, skewness,
    MAD, MSD (FE-4 Section 2).

  Catégorie 6 — Features non-linéaires & entropies (~7 features)  ★ ENRICHI
    ApEn, SampEn, PermEn, SpectralEn, HFD
    + Renyi entropy (α=2)  ← ajouté depuis FE-1
    + Log energy entropy    ← ajouté depuis FE-4
    Ref FE-1 : Vishal A S et al. (2025) — entropies Shannon + Renyi sur PSD
    Ref FE-4 : NeuroFeat (2026) — entropies Shannon/Log par niveau DWT

  Catégorie 7 — Transition Patterns simplifiés (~6 features)  ★ NOUVEAU
    Inspiré de QuadTPat (Cambay et al. 2024) — FE-3
    Histogramme des transitions : up, down, flat sur fenêtres glissantes
    Ref : Sci Rep 2024 — 92.95% (10-fold) et 73.63% (LOSO)
    Simplification : triplets au lieu des 4-tuples (latence < 40 ms)

  Catégorie 8 — NeuroFeat Kernels Texturaux Binaires (~9 features)  ★ NOUVEAU
    3 noyaux de seuillage statistique sur fenêtres glissantes :
      φ₁(ρ, M) = 1 si ρ ≥ μ  (mean threshold)
      φ₂(ρ, M) = 1 si ρ ≥ M̃  (median threshold)
      φ₃(ρ, M) = 1 si ρ ≥ σ  (std threshold)
    Fenêtre ω = ⌈√fs⌉ = 16 samples @ 250 Hz → matrice 4×4
    Par fenêtre : séquence binaire 16 bits → décimal (1 valeur/kernel)
    Features : mean, std, entropy de la distribution des décimaux × 3 kernels
    Ref : NeuroFeat (2026) — FE-4 Section 2
    Ablation study : features texturales seules → 86.5% accuracy

=== PIPELINE ===
  Epoch (1000 éch. @ 250 Hz)
    → Catégorie 1 : PSD Welch → 5 puissances de bande
    → Catégorie 2 : Ratios cognitifs → 5 ratios
    → Catégorie 3 : Hjorth + temporelles → 6 features
    → Catégorie 4 : DWT db4 → 5 sous-bandes × 4 stats = 20 features
    → Catégorie 5 : Statistiques texturales → 20 features  (FE-4 enrichi)
    → Catégorie 6 : Entropies + non-linéaire → 7 features  (FE-1 enrichi)
    → Catégorie 7 : Transition patterns → 6 features       (FE-3)
    → Catégorie 8 : NeuroFeat kernels binaires → 9 features (FE-4 nouveau)
    ─────────────────────────────────────────────────────
    TOTAL : ~78 features par epoch
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
    from scipy.integrate import trapezoid as _trapz
    return float(_trapz(psd[idx], freqs[idx]))

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
# CATÉGORIE 5 — Features statistiques texturales (20 features)
# Référence : "NeuroFeat: An adaptive neurological EEG feature engineering
#              approach for improved classification of MDD" (2026) — FE-4
#
# FE-4 Section 2 liste 23 features statistiques :
#   mean, std, variance, médiane, max, min, range, RMS, énergie, AM,
#   entropies Shannon/Log, kurtosis, skewness, MAD, MSD
#
# Ce qu'on calcule ici (les stats pures — entropies en Cat 6) :
#   Global (10) : skewness, kurtosis, IQR, RMS, peak_to_peak, crest_factor
#                 + median, max_val, min_val, MAD  ← ajoutés FE-4
#   Par sous-bande DWT (10) : skewness + kurtosis × 5 bandes
#   Total : 20 features
# ============================================================================

def extract_textural_features(epoch):
    """
    Catégorie 5 : Features statistiques texturales — NeuroFeat 2026 (FE-4).

    Features sur le signal GLOBAL (10) :
      skewness, kurtosis, IQR, RMS, crest_factor, peak_to_peak,
      median, max_val, min_val, MAD

    Features sur les SOUS-BANDES DWT (10) :
      dwt_{band}_skew + dwt_{band}_kurt pour 5 sous-bandes

    Total : 10 (global) + 10 (sous-bandes) = 20 features

    FE-4 ablation : features statistiques seules → 68 % accuracy
                    features texturales (Cat 5+8) → 86.5 %
                    combinaison tout → 91.5 % (sans L-SBWOA)
    """
    features = {}

    # --- Features globales (6 historiques) ---
    features['skewness']     = float(skew(epoch))
    features['kurtosis']     = float(kurtosis(epoch))
    features['IQR']          = float(iqr(epoch))
    features['RMS']          = float(np.sqrt(np.mean(epoch**2)))
    features['peak_to_peak'] = float(np.max(epoch) - np.min(epoch))
    rms = features['RMS'] + 1e-12
    features['crest_factor'] = float(np.max(np.abs(epoch)) / rms)

    # --- Features globales ajoutées depuis FE-4 (4 nouvelles) ---
    # median : robuste aux outliers, complémente la mean
    features['median']   = float(np.median(epoch))
    # max_val / min_val : bornes du signal, indicateurs d'artefacts
    features['max_val']  = float(np.max(epoch))
    features['min_val']  = float(np.min(epoch))
    # MAD = Mean Absolute Deviation : dispersion robuste (alternative à std)
    # MAD(x) = mean(|xᵢ − mean(x)|)
    features['MAD']      = float(np.mean(np.abs(epoch - np.mean(epoch))))

    # --- Skewness et kurtosis par sous-bande DWT (10 features) ---
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
    Spectral Entropy (Shannon) — sur la PSD normalisée.
    Mesure l'uniformité de la distribution spectrale.
    """
    f, psd = _psd_welch(epoch)
    psd_norm = psd / (np.sum(psd) + 1e-12)
    psd_norm = psd_norm[psd_norm > 0]
    return float(-np.sum(psd_norm * np.log2(psd_norm)))


def _renyi_entropy(epoch, alpha=2):
    """
    Entropie de Renyi (ordre α=2) sur la PSD normalisée — FE-1.

    Ref : Vishal A S et al. (2025) — entropie de Renyi α=2 utilisée
          en complément de Shannon sur le dataset DREAMER (valence 98.6%).

    Formule : H_α(X) = 1/(1-α) × log₂(Σ pᵢ^α)
    Pour α=2 : H₂ = -log₂(Σ pᵢ²)  (collision entropy)

    Interprétation :
      Renyi α=2 est plus sensible que Shannon aux distributions à queue
      épaisse → détecte mieux les pics de stress (puissance concentrée
      sur quelques fréquences).
    """
    f, psd = _psd_welch(epoch)
    psd_norm = psd / (np.sum(psd) + 1e-12)
    psd_norm = psd_norm[psd_norm > 0]
    sum_sq = np.sum(psd_norm ** alpha)
    if sum_sq <= 0:
        return 0.0
    return float((1.0 / (1.0 - alpha)) * np.log2(sum_sq + 1e-12))


def _log_energy_entropy(epoch):
    """
    Log Energy Entropy — FE-4 (NeuroFeat).

    Ref : Choudhury et al. (2026) — 23 features statistiques incluant
          entropies Shannon et Log sur le signal et ses composantes DWT.

    Formule : LogE = Σ log₂(xᵢ²) pour |xᵢ| > ε

    Interprétation :
      Mesure l'énergie logarithmique du signal.
      Signal faible (repos) → LogE très négatif.
      Signal fort (stress, concentration active) → LogE moins négatif.
      Complémentaire à Shannon car elle ne normalise pas.
    """
    x = epoch[np.abs(epoch) > 1e-10]
    if len(x) == 0:
        return 0.0
    return float(np.sum(np.log2(x ** 2)))


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
    Catégorie 6 : Features non-linéaires et entropies (7 features).

    Existant (5) — Age prediction hybrid 2025 :
      ApEn, SampEn, PermEn, SpectralEn (Shannon), HFD

    Ajouté (2) :
      RenyiEn (α=2) — FE-1 Vishal A S et al. (2025)
        Sensible aux distributions à queue épaisse (pics de stress)
      LogEnergyEn   — FE-4 NeuroFeat Choudhury et al. (2026)
        Énergie logarithmique du signal, complémentaire à Shannon
    """
    epoch_sub = epoch[::2] if len(epoch) > 500 else epoch

    return {
        'ApEn':         _approximate_entropy(epoch_sub, m=2, r_factor=0.2),
        'SampEn':       _sample_entropy(epoch_sub, m=2, r_factor=0.2),
        'PermEn':       _permutation_entropy(epoch, order=3, delay=1),
        'SpectralEn':   _spectral_entropy(epoch),
        'HFD':          _higuchi_fractal_dimension(epoch, kmax=10),
        'RenyiEn':      _renyi_entropy(epoch, alpha=2),
        'LogEnergyEn':  _log_energy_entropy(epoch),
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
# CATÉGORIE 8 — NeuroFeat Kernels Texturaux Binaires (9 features)
# Référence : "NeuroFeat: An adaptive neurological EEG feature engineering
#              approach for improved classification of MDD" (2026) — FE-4
#
# Principe (FE-4 Section 2) :
#   1. Découper le signal en fenêtres de ω = ⌈√fs⌉ = 16 samples @ 250 Hz
#      → chaque fenêtre est une matrice 4×4.
#   2. Appliquer 3 noyaux de seuillage statistique :
#        φ₁(ρ, M) = 1 si ρ ≥ μ   (mean threshold)
#        φ₂(ρ, M) = 1 si ρ ≥ M̃   (median threshold)
#        φ₃(ρ, M) = 1 si ρ ≥ σ   (std threshold)
#      → 3 séquences binaires 16-bit → 3 entiers décimaux par fenêtre.
#   3. Sur l'ensemble des fenêtres, extraire :
#        mean, std, entropy de la distribution des décimaux
#      → 3 stats × 3 kernels = 9 features.
#
# Fenêtre adaptative :
#   Pour fs ≥ 4 Hz : ω = ⌈√fs⌉²... mais le paper donne fs=256→16 frames
#   Donc on interprète : ω = ⌈√fs⌉ = 16 pour fs=250 Hz.
#   Reshape 16→4×4 (côté = √ω = 4).
#
# Ablation study (FE-4) :
#   Features texturales seules → 86.5 % accuracy (sans optimisation)
#   Features statistiques seules → 68 %
#   Combinaison + L-SBWOA → 99.22 %
# ============================================================================

def extract_neurofeat_features(epoch):
    """
    Catégorie 8 : NeuroFeat kernels texturaux binaires — FE-4 (2026).

    3 kernels × 3 stats (mean, std, entropy) = 9 features.

    nf_mean_thr_mean   : valeur décimale moyenne (kernel φ₁ = mean)
    nf_mean_thr_std    : dispersion des décimaux (kernel φ₁)
    nf_mean_thr_ent    : entropie de la distribution (kernel φ₁)
    nf_med_thr_*       : idem pour kernel φ₂ (median threshold)
    nf_std_thr_*       : idem pour kernel φ₃ (std threshold)
    """
    # ω = ⌈√fs⌉ = ⌈√250⌉ = 16 samples → matrice 4×4
    omega  = int(np.ceil(np.sqrt(FS)))          # 16
    side   = int(np.sqrt(omega))                # 4
    omega  = side * side                        # 16 (carré parfait)

    n_windows = len(epoch) // omega
    if n_windows == 0:
        zero = {f'nf_{k}_{s}': 0.0
                for k in ['mean_thr', 'med_thr', 'std_thr']
                for s in ['mean', 'std', 'ent']}
        return zero

    dec_vals = {'mean_thr': [], 'med_thr': [], 'std_thr': []}

    for w in range(n_windows):
        seg = epoch[w * omega: (w + 1) * omega]
        mat = seg.reshape(side, side)

        mu  = np.mean(mat)
        med = np.median(mat)
        sig = np.std(mat)

        for key, thr in [('mean_thr', mu), ('med_thr', med), ('std_thr', sig)]:
            bits = (mat.flatten() >= thr).astype(np.uint8)
            # Convertir la séquence binaire 16-bit en entier décimal
            decimal = int(np.packbits(bits, bitorder='big').view(np.uint16)[0])
            dec_vals[key].append(decimal)

    features = {}
    for key, vals_list in dec_vals.items():
        vals = np.array(vals_list, dtype=float)
        # Entropie de Shannon sur l'histogramme des valeurs décimales
        hist, _ = np.histogram(vals, bins=min(20, len(vals)), density=False)
        hist    = hist[hist > 0].astype(float)
        hist   /= hist.sum() + 1e-12
        ent     = float(-np.sum(hist * np.log2(hist + 1e-12)))

        features[f'nf_{key}_mean'] = float(np.mean(vals))
        features[f'nf_{key}_std']  = float(np.std(vals))
        features[f'nf_{key}_ent']  = ent

    return features  # 9 features


# ============================================================================
# FONCTION PRINCIPALE : extraction de TOUTES les features pour une epoch
# ============================================================================

def extract_all_features(epoch):
    """
    Extrait les 78 features complètes pour une epoch EEG.

    Entrée : epoch (np.array, 1000 échantillons, normalisé z-score)
    Sortie : dict ordonné avec toutes les features

    Catégories et articles sources :
      1. PSD Welch (5)          — FE-1 (Vishal 2025), FE-2 (Martin 2018)
      2. Ratios cognitifs (5)   — CdC NeuroCap + Salam 2026
      3. Hjorth + temporel (6)  — Samsa 2026
      4. DWT sous-bandes (20)   — FE-2 (Martin 2018) : db4, 4 niveaux
      5. Texturales (20)        — FE-4 (NeuroFeat 2026) enrichi
      6. Non-linéaires (7)      — Age prediction 2025 + FE-1 + FE-4
      7. Transitions (6)        — FE-3 (QuadTPat 2024) simplifié
      8. NeuroFeat kernels (9)  — FE-4 (NeuroFeat 2026) : φ₁/φ₂/φ₃
      ────────────────────────
      TOTAL : 78 features
    """
    features = {}

    # Cat 1 : PSD Welch
    psd_feats = extract_psd_features(epoch)
    features.update(psd_feats)

    # Cat 2 : Ratios cognitifs
    features.update(extract_ratio_features(psd_feats))

    # Cat 3 : Hjorth + temporel
    features.update(extract_temporal_features(epoch))

    # Cat 4 : DWT sous-bandes
    features.update(extract_dwt_subband_features(epoch))

    # Cat 5 : Texturales (enrichi FE-4)
    features.update(extract_textural_features(epoch))

    # Cat 6 : Non-linéaires + Renyi + LogEnergy (enrichi FE-1, FE-4)
    features.update(extract_nonlinear_features(epoch))

    # Cat 7 : Transitions (FE-3)
    features.update(extract_transition_features(epoch))

    # Cat 8 : NeuroFeat kernels binaires (FE-4 — NOUVEAU)
    features.update(extract_neurofeat_features(epoch))

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
        print(f"\n   Cat 1  PSD Welch              :  5 features  [FE-1, FE-2]")
        print(f"   Cat 2  Ratios cognitifs        :  5 features  [CdC]")
        print(f"   Cat 3  Hjorth + temporel       :  6 features  [Samsa 2026]")
        print(f"   Cat 4  DWT sous-bandes (db4)   : 20 features  [FE-2]")
        print(f"   Cat 5  Texturales enrichies    : 20 features  [FE-4]")
        print(f"   Cat 6  Non-linéaires + entrop. :  7 features  [FE-1, FE-4]")
        print(f"   Cat 7  Transitions (QuadTPat)  :  6 features  [FE-3]")
        print(f"   Cat 8  NeuroFeat kernels φ₁₂₃  :  9 features  [FE-4 NOUVEAU]")
        print(f"   ─────────────────────────────────────────────────────")
        print(f"   TOTAL                          : {len(feature_names)} features")

    return features_matrix, feature_names


# ============================================================================
# MAIN : extraction sur les datasets augmentés
# ============================================================================

def main():
    """
    Pipeline d'extraction :
      1. Localise les données augmentées (datasets_augmented/)
      2. Extrait les 78 features pour chaque expérience (A, B, C, D, FULL)
      3. Extrait les features pour val et test
      4. Sauvegarde les matrices de features, les labels et les subject_ids
         dans features/Features_eng/
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