# NeuroCap — Neurofeedback Adaptatif : Base de Rédaction PFE
**Chapitre V (ou section du Chap. III/IV selon plan) — Système de feedback adaptatif**
*Oumama SENDADI — ENSAM Rabat — PFE Ingénierie Biomédicale 2026*

---

## Plan suggéré pour ce chapitre

1. Introduction et positionnement du neurofeedback adaptatif
2. Architecture globale du système de feedback
3. Constitution du dataset multimédia
4. Moteur de recommandation : filtrage contenu + Thompson Sampling
5. Moteur d'adaptation dynamique (trois niveaux)
6. Guide de préparation et interface utilisateur
7. Rapport de séance et recommandations
8. Conclusion

---

## 1. Introduction et positionnement

### Problématique

Le neurofeedback classique souffre de trois limitations majeures identifiées dans la littérature :

- **Contenu fixe** : le même stimulus visuel ou sonore est présenté à tous les patients, indépendamment de leur état cérébral instantané — ce qui réduit l'efficacité thérapeutique (Sitaram et al., 2017).
- **Difficulté statique** : le seuil de succès reste constant tout au long du protocole, laissant certains utilisateurs en frustration ou en ennui — deux états qui bloquent l'apprentissage neuroplastique (Mou et al., 2024).
- **Absence de personnalisation** : aucune adaptation au profil individuel du patient, alors que la variabilité inter-sujets est considérable même pour un signal EEG monocanal frontal Fp2.

### Solution NeuroCap

NEUROCAP répond à ces trois limitations par une **boucle de feedback fermée à trois niveaux temporels** :

1. **Temps réel (500 ms)** : lissage EWMA du signal cognitif classifié
2. **Intra-session (blocs de 3 min)** : ajustement dynamique du seuil selon la règle 40-60 % (Mou et al., 2024)
3. **Inter-sessions (nuitée)** : recalibration du seuil et fine-tuning personnalisé du modèle EEG

Ce chapitre décrit en détail chacun de ces niveaux, ainsi que le moteur de sélection multimédia qui choisit le contenu feedback le plus approprié en fonction de l'état EEG classifié.

---

## 2. Architecture globale du système de feedback

### Schéma de la boucle fermée

```
┌───────────────────────────────────────────────────────────────┐
│                    BOUCLE DE NEUROFEEDBACK FERMÉE             │
│                                                               │
│  EEG Fp2 (250 Hz)                                             │
│       │                                                       │
│       ▼                                                       │
│  Prétraitement DSP                                            │
│  Notch 50/100 Hz · BP [1–45 Hz] · débruitage ondelettes db4  │
│       │                                                       │
│       ▼                                                       │
│  Extraction 63 features                                       │
│  (Welch, Hjorth, HFD, ratios TBR/EI, DWT, stats)            │
│       │                                                       │
│       ▼                                                       │
│  Classifieur LightGBM (LOSO, accuracy 89,4 %)                │
│  → concentration_rate, stress_rate, confidence               │
│       │                                                       │
│       ▼                                                       │
│  Moteur Adaptatif (EWMA · seuil · palier)                    │
│       │                                                       │
│       ├─── état EEG → Moteur de Recommandation ──┐           │
│       │              (Thompson Sampling)          │           │
│       │                                           ▼           │
│       │                              Contenu sélectionné      │
│       │                              (audio / image /         │
│       │                               vidéo / jeu cognitif)  │
│       │                                           │           │
│       │                              Rendu Frontend React     │
│       │                                           │           │
│       └───────── retour utilisateur ──────────────┘           │
│                  (SAM, like/skip)                             │
│                                                               │
│  Post-séance : rapport IA (Claude API) + mise à jour poids   │
└───────────────────────────────────────────────────────────────┘
```

### Composants principaux (fichiers source)

| Composant | Fichier | Rôle |
|---|---|---|
| Moteur adaptatif | `app/Backend/app/services/adaptative_engine.py` | EWMA, seuils, paliers |
| Moteur de recommandation | `Feedback_METADATA/recommender.py` | Thompson Sampling + filtrage contenu |
| Routes feedback | `app/Backend/app/routes/feedback.py` | API REST + WebSocket |
| Séance neurofeedback | `app/Frontend/src/pages/FeedbackSession.jsx` | Orchestrateur 6 phases |
| Guide électrodes | `app/Frontend/src/pages/ElectrodeGuide.jsx` + `EEGSelector.jsx` | Checklist préparation |
| Rapport de séance | `app/Frontend/src/components/feedback/FeedbackReport.jsx` | Affichage rapport IA |
| **[v2] Serveur WebSocket EEG** | `2-Preprocessing/eeg_server_v2.py` | Pipeline DSP complet + broadcast |
| **[v2] Pipeline de prétraitement** | `PreprocessingPipeline` (dans eeg_server_v2) | Gate qualité, notch, BP, dB norm |
| **[v2] Filtres temporels** | `TemporalFilters` (dans eeg_server_v2) | Morlet CWT, STFT, Hilbert |
| **[v2] Transformées spatiales** | `SpatialTransforms` (dans eeg_server_v2) | CAR, Laplacien, Z-score, PAC |
| **[v2] Extracteur d'époques** | `EpochExtractor` (dans eeg_server_v2) | Fenêtre glissante + vecteur features |
| **[v2] Flux session** | `SessionSetup.jsx` + `NeurofeedbackSession.jsx` | Sélection mode → préparation → séance |
| **[v2] Email rapport** | `app/Backend/app/services/email_service.py` | Rapport séance envoyé au patient |

---

### 2.3 Pipeline DSP v2 — `eeg_server_v2.py`

Le fichier `eeg_server_v2.py` implémente un pipeline DSP complet intégré au serveur WebSocket, organisé en quatre classes indépendantes et empilées. Il cohabite avec le `RealTimeProcessor` d'origine et y injecte ses résultats via `EpochExtractor.push()`.

#### 2.3.1 Chaîne de prétraitement — `PreprocessingPipeline`

Chaque époque brute de 4 s (1 000 échantillons à 250 Hz) traverse trois étapes :

| Étape | Mécanisme | Paramètres |
|---|---|---|
| **Gate qualité** | Rejet si pic-à-pic > 150 µV, std < 0,5 µV (signal plat), énergie HF > 60 % | Cohen ch. 27 |
| **Filtre notch** | `iirnotch(50 Hz, Q=30)` + `filtfilt` (zéro-phase) | Supprime 50 Hz réseau |
| **Passe-bande** | `butter(4, [0,5–40 Hz])` + `filtfilt` | Élimine dérive DC et EMG |
| **Normalisation dB** | $10 \log_{10}(P_{bande}/P_{baseline})$ par bande | Cohen ch. 26 |

La **baseline** est collectée automatiquement pendant les 30 premières secondes de session (ou déclenchée explicitement via la commande WebSocket `FINALISE_BASELINE`).

#### 2.3.2 Filtres temporels — `TemporalFilters`

Trois analyses temps-fréquence appliquées sur l'époque propre et fenêtrée Hann :

**Ondelette de Morlet (CWT)**
- Fréquences : [4, 6, 8, 10, 12, 15, 20, 25, 30] Hz
- $n_{cycles} = 6$ (compromis résolution temporelle / fréquentielle, Cohen ch. 14–17)
- Convolution via FFT pour efficacité
- Décimation × 10 avant broadcast WebSocket

**Spectrogramme STFT**
- Fenêtre Hann, $N_{seg} = 250$, $N_{overlap} = 125$
- Résultat clip à [0–40 Hz], converti en dB : $10 \log_{10}(|Z|^2 + \varepsilon)$
- Transmis à chaque époque

**Signal analytique de Hilbert (par bande)**
- Enveloppe instantanée $A(t) = |x_a(t)|$ + phase $\phi(t) = \angle x_a(t)$
- Fréquence instantanée : $f_{inst} = \frac{\Delta\phi}{2\pi} \cdot f_s$
- Statistiques (mean, std, max) par bande + enveloppe décimée × 25

**Budget CPU** : Morlet (lourd) exécuté 1 époque sur 4 ; STFT et Hilbert à chaque époque.

#### 2.3.3 Transformées spatiales — `SpatialTransforms`

Adaptées à la configuration monocanal Fp2 (AD8232) :

| Transformée | Formule | Rôle |
|---|---|---|
| **CAR** | $x - \bar{x}_{epoch}$ | Suppression DC résiduelle |
| **Laplacien (fini)** | $x[n+1] - 2x[n] + x[n-1]$ + scale RMS | Atténuation volume conductance |
| **Z-score session** | $(x - \mu_{hist}) / \sigma_{hist}$ sur fenêtre glissante 30 s | Non-stationnarité intra-session |
| **PAC (Modulation Index)** | MI Tort 2010 : phase θ (4–8 Hz) × amplitude γ (30–40 Hz), 18 bins | Couplage cross-fréquentiel |

L'historique glissant de 30 s alimente le Z-score ; les transformées CAR et Laplacien sont incluses dans le paquet WebSocket `epoch_summary` (signal décimé × 10).

#### 2.3.4 Extracteur d'époques — `EpochExtractor`

Fenêtrage glissant 75 % de chevauchement :

| Paramètre | Valeur |
|---|---|
| Durée époque | 4 s → 1 000 échantillons |
| Pas de glissement | 250 échantillons (75 % overlap) |
| Taper | Fenêtre Hann (réduit fuites spectrales, Cohen ch. 12) |
| Résolution temporelle | Nouvelle époque toutes les ~1 s |

**Vecteur de features par époque (29+ éléments) :**

| Catégorie | Features |
|---|---|
| Spectrales | θ, α, β, γ absolues + relatives, α/β, θ/β (TBR), engagement = β/(α+θ), stress\_idx = β/α |
| dB baseline | db\_theta, db\_alpha, db\_beta |
| Statistiques | RMS, skewness, kurtosis, ZCR, SEF95, entropie spectrale |
| Non-linéaires | Hjorth (activité, mobilité, complexité), ApEn sur 256 échantillons |

Le broadcast WebSocket émet deux messages distincts par époque : `eeg` (flux temps réel ~62 Hz) et `epoch` (paquet enrichi ~1 Hz). Les tableaux de signal bruts sont allégés (décimation) pour préserver la bande passante.

---

## 3. Dataset multimédia de feedback

### 3.1 Corpus global (merged_features.csv)

Le système dispose d'une bibliothèque de **1 177 items multimédias** hébergés sur Cloudinary et caractérisés par **113 features** acoustiques, visuelles et temporelles. Ce fichier `merged_features.csv` est le pivot du moteur de recommandation.

| Type | Nombre d'items | Condition cible | Source |
|---|---|---|---|
| Audio | ~120 | Relaxation (`relax`) | Fichiers WAV annotés |
| Image | ~400 | Relaxation / Focus / Transition | Photographique, abstrait |
| Vidéo | ~150 | Relaxation / Focus | Clips annotés |
| Jeu cognitif | ~507 | Focus / Relaxation | Générés en interne |
| **Total** | **1 177** | — | `merged_features.csv` + Cloudinary |

### 3.2 Features par type de média

#### Audio (60 features extraites par librosa)

| Feature | Description | Pertinence neurofeedback |
|---|---|---|
| `tempo_bpm` | Tempo en BPM | 60-75 BPM → entraînement alpha (Thaut et al., 1999) |
| `rms_mean` | Énergie RMS | Corrélé au niveau d'éveil |
| `harm_perc_ratio` | Ratio harmonique/percussif | Haute harmonicité → relaxation (Sammler et al., 2007) |
| `spectral_stationarity` | Stationnarité spectrale | Sons stables → moins activants |
| `mfcc1–13_mean/std` | Coefficients MFCC | Timbre global |
| `spec_centroid_mean` | Centroïde spectral | Luminosité sonore |
| `zcr_mean` | Taux de passage par zéro | Rugosité perçue |
| `spectral_flux` | Flux spectral | Variabilité temporelle |

#### Image (30 features visuelles)

| Feature | Description | Pertinence |
|---|---|---|
| `brightness_global` | Luminosité globale | Haute luminosité → valence positive (Valdez & Mehrabian, 1994) |
| `saturation_mean` | Saturation colorimétrique | Saturation modérée → calme |
| `contrast_rms` | Contraste RMS | Fort contraste → arousal élevé |
| `glcm_homogeneity` | Homogénéité GLCM | Texture uniforme → relaxation |
| `symmetry_h` | Symétrie horizontale | Haute symétrie → harmonie perçue |
| `edge_density` | Densité de contours | Complexité visuelle → arousal (Berman et al., 2014) |
| `cnn_pca_01–20` | PCA features CNN | Représentation sémantique profonde |

#### Vidéo (20 features temporelles)

| Feature | Description | Pertinence |
|---|---|---|
| `optical_flow_mean` | Mouvement moyen | Mouvement faible → relaxation |
| `temporal_energy_var` | Variance énergie temporelle | Stabilité du contenu |
| `scene_change_rate` | Fréquence de coupures | Coupes rares → apaisement |
| `motion_regularity` | Régularité du mouvement | Régularité → confort visuel |
| `flicker_rate` | Clignotement | < 3 Hz : risque épileptique (exclu) |
| `color_temp_k` | Température couleur (Kelvin) | Tons chauds → relaxation |

#### Jeux cognitifs (games_features_clean.csv)

5 types de jeux répartis en **5 niveaux de difficulté (NIV1–5)** avec 4 phases de protocole (P1–P4) :

| Jeu | Fonction cognitive testée | Composant React |
|---|---|---|
| **Sudoku** | Raisonnement logique, flexibilité | `SudokuGame.jsx` |
| **Mémoire** | Mémoire de travail, encodage | `MemoryGame.jsx` |
| **Calcul** | Fonctions exécutives, attention | `CalculGame.jsx` |
| **Énigmes** | Flexibilité cognitive, créativité | `EnigmeGame.jsx` |
| **Puzzle** | Raisonnement visuospatial | `PuzzleGame.jsx` |

---

## 4. Moteur de recommandation

### 4.1 Architecture trois couches

Le moteur de recommandation (`recommender.py`) implémente une architecture à trois couches successives, inspirée des systèmes de recommandation hybrides (Adomavicius & Tuzhilin, 2005) :

```
Couche 1 : Content-Based Filtering
           Similarité cosinus entre vecteur EEG cible et features du média
                              │
                              ▼
Couche 2 : Thompson Sampling (bandit contextuel)
           Pondération probabiliste basée sur l'historique utilisateur
                              │
                              ▼
Couche 3 : Score combiné
           score_final = similarité_cosinus × échantillon_Beta(α, β)
```

### 4.2 Filtrage par similarité cosinus (Couche 1)

Pour chaque état EEG classifié (`stress`, `focus`, `neutral`), un **vecteur cible** basé sur la littérature scientifique définit le profil idéal du contenu à sélectionner.

**Exemple — État stress → audio cible :**
```
tempo_bpm          = 0.15  (très lent, < 60 BPM)
harm_perc_ratio    = 0.85  (très harmonique)
spectral_stationarity = 0.80  (stable)
rms_mean           = 0.25  (doux)
```
*Sources : Thaut et al. (1999) — entraînement neural ; Sammler et al. (2007) — harmonicité et relaxation*

**Exemple — État focus → image cible :**
```
brightness_global = 0.55  (luminosité modérée)
contrast_rms      = 0.55  (contraste moyen)
saturation_mean   = 0.60  (couleurs vives sans excès)
edge_density      = 0.55  (complexité stimulante)
```
*Sources : Valdez & Mehrabian (1994) ; Berman et al. (2014)*

La similarité cosinus est calculée entre ce vecteur cible et les features normalisées de chaque média candidat :

$$\text{sim}(v_{\text{cible}}, v_{\text{item}}) = \frac{v_{\text{cible}} \cdot v_{\text{item}}}{\|v_{\text{cible}}\| \cdot \|v_{\text{item}}\|}$$

### 4.3 Thompson Sampling avec prior informé (Couche 2)

Le Thompson Sampling (Chapelle & Li, 2011) modélise la probabilité de succès de chaque média par une distribution Bêta $\text{Beta}(\alpha_i, \beta_i)$ :

$$\theta_i \sim \text{Beta}(\alpha_i, \beta_i)$$

- **α_i (succès)** : incrémenté de +1 si le média est jugé efficace
- **β_i (échecs)** : incrémenté de +1 si le média est skippé ou mal noté

**Prior informé par similarité cosinus (initialisation) :**
```python
α_initial = 1.0 + sim × 0.5   # médias proches du cible → prior favorisé
β_initial = 1.0 + (1 - sim) × 0.3
```

**Mise à jour des poids (à chaque retour utilisateur) :**

| Événement | Mise à jour |
|---|---|
| `liked = true` | α_i += 1 |
| `liked = false` | β_i += 1 |
| `skip` | β_i += 1 |
| `SAM ≥ 4` | α_i += (score − 3) × 0.5 |
| `SAM ≤ 2` | β_i += (3 − score) × 0.5 |
| `Δα > 0.05 AND Δβ < -0.05` | α_i += 1 (EEG confirme l'efficacité) |

**Score de sélection final :**
$$\text{score}_i = \text{sim}_i \times \theta_i$$

L'item avec le score maximal est sélectionné.

### 4.4 Gestion du cold start

Pour les **5 premières séances**, un mécanisme epsilon-greedy assure l'exploration du catalogue :

$$\epsilon = 1 - \frac{n_{\text{séances}}}{5}$$

- Séance 1 : ε = 0.8 → 80 % de sélections aléatoires (exploration)
- Séance 3 : ε = 0.4 → 40 % exploration / 60 % exploitation
- Séance 6+ : ε = 0 → exploitation pure (Thompson Sampling seul)

### 4.5 Prévention de l'habituation

Pour éviter la présentation répétitive du même type de contenu (Grill-Spector & Malach, 2001), un seuil d'habituation par type est appliqué :

| Type | Seuil d'habituation | Effet |
|---|---|---|
| Audio | 3 répétitions consécutives | Le type audio est supprimé temporairement |
| Image | 2 répétitions consécutives | Passage forcé vers autre type |
| Vidéo | 2 répétitions consécutives | Idem |
| Jeu | 1 répétition consécutive | Alternance systématique |

De plus, un **buffer d'état EEG de 28 secondes** (7 époques × 4 s) est requis avant tout changement de contenu (Makeig et al., 1999), garantissant que la transition n'est déclenchée que sur un état cognitif stable.

### 4.6 Sélection adaptative des jeux cognitifs

Pour les jeux (état `focus`), un mécanisme de **Zone Proximale de Développement** (Vygotsky, 1978 ; Clement et al., 2015) ajuste le niveau :

```
Si erreur_rate < 20 % AND Δβ > 0.05 → niveau += 1 (plus difficile)
Si erreur_rate > 60 % OR  Δβ < -0.10 → niveau -= 1 (plus facile)
Sinon → niveau maintenu
```

Les deltas EEG sont calculés sur une **fenêtre de 32 secondes** (8 époques × 4 s), conformément aux recommandations de Birbaumer et al. (1999) pour la stabilité des mesures de neuromodulation.

---

## 5. Moteur d'adaptation dynamique

### 5.1 Vue d'ensemble des trois niveaux

Le moteur d'adaptation (`adaptative_engine.py`) opère à trois échelles temporelles distinctes, ce qui constitue une différence fondamentale par rapport aux systèmes de neurofeedback conventionnels :

| Niveau | Échelle temporelle | Mécanisme | Référence |
|---|---|---|---|
| **1 — Temps réel** | 500 ms | Lissage EWMA (α = 0,3) | Mou et al., 2024 |
| **2 — Intra-session** | 3 min (bloc) | Ajustement seuil ±0,05 | Mou et al., 2024 |
| **3 — Inter-sessions** | 24 h | Recalibration + fine-tuning | CdC § 2.6 |

### 5.2 Niveau 1 — Lissage EWMA (temps réel)

Afin d'atténuer le bruit inhérent aux classifications EEG monocanal, chaque nouvelle prédiction est intégrée via une **Moyenne Mobile Exponentiellement Pondérée** (EWMA) :

$$\hat{x}(t) = \alpha \cdot x(t) + (1 - \alpha) \cdot \hat{x}(t-1), \quad \alpha = 0{,}3$$

Cette formule accorde 30 % de poids à la mesure instantanée et 70 % à l'historique lissé, ce qui correspond à une constante de temps d'environ 4 secondes — suffisante pour filtrer les fluctuations transitoires sans induire de retard perceptible dans le feedback (Mou et al., 2024).

Les quatre métriques lissées en temps réel sont :
- `ewma_concentration` : taux de concentration (0–100)
- `ewma_stress` : taux de stress (0–100)
- `ewma_tbr` : ratio Thêta/Bêta (indicateur de relaxation)
- `ewma_ei` : indice d'engagement $I_E = P_\beta / (P_\alpha + P_\theta)$

**Seuil de confiance** : si la confiance du classifieur est inférieure à 60 %, le feedback est suspendu (`feedback_active = false`) pour éviter de fournir un renforcement sur une classification incertaine.

### 5.3 Niveau 2 — Ajustement intra-session (règle 40-60 %)

À la fin de chaque **bloc de 3 minutes** (≈ 360 époques), le taux de succès du bloc est calculé :

$$\text{taux\_succès} = \frac{\text{epochs\_succès}}{\text{epochs\_total}}$$

Une **époque est un succès** si la concentration normalisée dépasse le seuil adaptatif courant θ :
$$\text{succès} = \frac{\text{concentration\_rate}}{100} > \theta$$

La règle d'ajustement (Mou et al., 2024) maintient l'utilisateur dans la **zone de flow** :

| Taux de succès | Action | Justification |
|---|---|---|
| > 60 % | θ += 0,05 (plus difficile) | Trop facile → ennui → sortie du flow |
| [40 %, 60 %] | θ inchangé | Zone optimale d'apprentissage |
| < 40 % | θ -= 0,05 (plus facile) | Trop difficile → frustration → abandon |

Le seuil est contraint globalement : θ ∈ [0,2 ; 0,9].

### 5.4 Progression par paliers

Chaque utilisateur est associé à un **palier de progression** (P1→P2→P3→P4), qui délimite la plage autorisée pour le seuil θ :

| Palier | Plage θ | Phase clinique | Objectif |
|---|---|---|---|
| **P1** | [0,20 ; 0,45] | Initiation | Prise de conscience |
| **P2** | [0,40 ; 0,60] | Apprentissage | Stabilisation |
| **P3** | [0,55 ; 0,75] | Maîtrise | Consolidation |
| **P4** | [0,70 ; 0,90] | Autonomie | Transfert extra-session |

Quand θ atteint la borne supérieure du palier courant, la progression au palier suivant est déclenchée automatiquement et θ est réinitialisé à la borne inférieure du nouveau palier.

### 5.5 Niveau 3 — Recalibration inter-sessions

La formule de recalibration inter-session pondère la tendance long terme et l'état mesuré le jour J :

$$\theta_{\text{jour}} = 0{,}70 \times \mu_{\text{long terme}} + 0{,}30 \times \theta_{\text{mesuré aujourd'hui}}$$

Cette pondération (70/30) privilégie la tendance établie sur plusieurs semaines tout en permettant l'adaptation à la variabilité intra-individuelle journalière (fatigue, stress externe, qualité de sommeil).

### 5.6 Fine-tuning nocturne du modèle (inter-sessions)

Un scheduler APScheduler s'exécute chaque nuit à 02h00 UTC pour identifier les patients éligibles à un fine-tuning de leur modèle EEG personnel :

**Conditions de déclenchement :**
- `v1` : première calibration (nouveau patient, suffisamment d'époques)
- `v2` : nouvelle batch d'époques haute confiance accumulée
- `drift` : précision sur les 20 dernières séances < seuil
- `maint` : maintenance programmée

**Processus :**
1. Collecte des époques haute confiance (confidence > 0,60) en base Supabase
2. Fine-tuning du modèle EEGNet sur les données du patient
3. Évaluation avant/après sur un jeu de validation
4. Sauvegarde du checkpoint : `models/personal/patient_{id}_v{n}.joblib`
5. Mise à jour du profil EEG (`eeg_profiles.finetuned_model_checkpoint`)

La séance suivante utilise le modèle personnalisé du patient (ou le modèle global LightGBM en cas d'échec du fine-tuning).

---

## 6. Interface utilisateur — Guide et séance

### 6.1 Flux d'entrée en séance — [v2] `SessionSetup` → `NeurofeedbackSession` → `FeedbackSession`

Le refactoring du flux de démarrage a introduit deux nouvelles pages et un stepper de préparation, remplaçant la modale directe du dashboard :

```
Dashboard "Démarrer" → /session/setup
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
         EEG Live         Fichier          Démo
              └───────────────┼───────────────┘
                              ▼
                   /neurofeedback?mode=[live|file|demo]
                              │
                   ┌──────────┴──────────┐
                   ▼                     ▼
            Fixation 30s          Breathing box
            (overlay noir,        (4s/4s/6s, 3 cycles,
             skippable)            skippable)
                   └──────────┬──────────┘
                              ▼
                     Calibration (skippable)
                     ← CalibrationSession.jsx
                        + EEGPipelineBar (si mode live)
                              ▼
                    /feedback/session → FeedbackSession.jsx
```

**Nouveaux fichiers créés (v2) :**

| Fichier | Rôle |
|---|---|
| `src/pages/SessionSetup.jsx` | Page de sélection du mode (3 cartes : live / fichier / démo) |
| `src/pages/NeurofeedbackSession.jsx` | Stepper : Fixation → Breathing → Calibration → navigate |
| `src/components/neurofeedback/FixationStep.jsx` | Point de fixation 30 s, fond noir plein écran, skippable |
| `src/components/neurofeedback/BreathingStep.jsx` | Cohérence cardiaque box 4/4/6 s, 3 cycles pour déverrouiller "Suivant" |
| `src/components/neurofeedback/CalibrationStep.jsx` | Wrapper mince autour de `CalibrationSession` |

**Mode démo** : `FeedbackSession.jsx` reçoit `isDemo=true` → classifie aléatoirement toutes les 5–10 s via `setTimeout` (aucun EEG requis).

**CalibrationSession avec barre pipeline EEG** : en mode live, un bandeau `EEGPipelineBar` s'affiche au-dessus des étapes de calibration. Il interroge `/api/eeg/status` toutes les 2 s et visualise les 4 étapes : ESP32 → Streaming → Traitement → Analyse.

---

### 6.2 Guide de préparation (ElectrodeGuide.jsx)

Avant chaque séance, l'utilisateur est guidé par un **protocole de préparation en 4 étapes** intégré dans l'interface (accessible depuis `EEGSelector.jsx`) :

1. **Nettoyage cutané** : tampon d'alcool à 70 % sur Fp2, M2, M1
2. **Application du gel conducteur** : sur chaque électrode Ag/AgCl
3. **Placement des électrodes** (Système 10-20 international) :
   - **Fp2** (active, frontale droite) — correspond à F8 dans certaines nomenclatures
   - **M2** (référence, mastoïde droite)
   - **M1** (masse, mastoïde gauche)
4. **Vérification du signal** : score CQE ≥ 60 requis pour démarrer

Un **diagramme SVG du système 10-20** intègre la localisation de Fp2 par rapport aux autres points de repère anatomiques (Fpz, Fp1, F7/F8, Cz, Pz, Oz).

La séance ne peut démarrer qu'après **validation complète de la checklist** et obtention d'un signal de qualité acceptable (score CQE ≥ 60, label `fair` ou `good`).

### 6.3 Protocole de séance (FeedbackSession.jsx) — 6 phases séquentielles

L'orchestrateur de séance enchaîne six phases automatiques :

| Phase | Durée | Composant | Description |
|---|---|---|---|
| `PRE_SESSION` | 3 s | Spinner | Initialisation, confirmation de l'état |
| `BASELINE_CLOSED` | 2 min | `BreathingGuide` | Yeux fermés, acquisition baseline individuelle |
| `FEEDBACK_BLOCK × 6` | 3 min × 6 = 18 min | `MediaZone` + `UserFeedbackBar` | Séance principale avec feedback adaptatif |
| `INTER_BLOCK_PAUSE` | 20 s | Overlay | Pause inter-bloc, message de récupération |
| `GUIDED_REST` | 3 min | Guide relaxation | Retour au calme, arrêt facultatif |
| `POST_SESSION` | — | `FeedbackReport` | Rapport IA + métriques |

**Durée totale d'une séance type : ≈ 25 minutes**

### 6.4 Affichage en temps réel durant les blocs feedback

Pendant chaque bloc de 3 minutes, l'interface affiche simultanément :

- **MiniEEGOscilloscope** : forme d'onde brute filtrée à ≈62 Hz, avec indicateur d'état ML (concentration / stress / incertain) et barre de confiance
- **BandBars** : puissances relatives δ, θ, α, β, γ actualisées chaque seconde
- **BrainStateIndicator** : visualisation colorée de l'état cognitif (vert = concentration, rouge = stress, gris = incertain)
- **BreathingGuide** (si stress\_rate > 50 %) : animation SVG guidant l'expiration 4s – apnée 4s – inspiration 4s
- **FocusPoint** (si concentration\_rate > 50 %) : point de fixation central avec pulsation douce
- **MediaZone** : rendu du contenu sélectionné (image plein écran / vidéo / jeu / lecteur audio)
- **UserFeedbackBar** : boutons Like/Dislike, curseur SAM (1–5), bouton Skip
- **SessionBlockTimer** : barre de progression + compte à rebours 3 min, numéro du bloc courant

### 6.5 Logique de changement de contenu

Un changement de contenu est déclenché automatiquement dans trois cas :

1. **Durée maximale atteinte** : audio (300 s), image (60 s), vidéo (120 s), jeu (600 s)
2. **Changement d'état EEG stable** : si l'état change et reste stable 28 s (7 époques × 4 s), le contenu est mis à jour pour correspondre au nouvel état
3. **Skip utilisateur** : changement immédiat + pénalité β_i += 1 pour l'item skippé

---

### 6.6 Corrections et améliorations du protocole [v2]

#### Cohérence du widget protocole (DashboardPage.jsx)

Le composant `ProtocolWidget` affichait 0/15 tandis que `SessionCalendar` indiquait 12/15, car ils lisaient deux sources différentes (`protocol_sessions` vs `feedback_sessions`). **Correction** : `ProtocolWidget` appelle désormais en parallèle `/api/protocol/status` ET `/api/sessions/calendar`, puis prend `Math.max(total_completed)` pour garantir la cohérence.

#### MediaZone avec sessionId et état EEG (ProtocolSession.jsx)

`<MediaZone>` ne recevait pas ses props `sessionId` et `eegState` — l'appel guide API était silencieusement ignoré. **Correction** : passage explicite de `sessionId={feedSessId}` et `eegState={navEegState}`.

#### Modal de fin de séance "Bravo !"

`SessionReport` affiche désormais : *"Bravo ! Séance X terminée avec succès"* + une carte montrant la date de la prochaine séance. Le backend `PUT /api/protocol/sessions/{n}/complete` retourne `next_session_date` et `next_interval_days` dans sa réponse.

#### Rapport de séance par email

`send_session_report_email()` ajoutée dans `email_service.py` et déclenchée depuis l'endpoint `complete_session`. Le contenu de l'email est personnalisé selon :
- `profile_type` (A/B/C)
- `session_number`
- `acquisition_type` (eeg\_live / manual / file\_upload)
- Scores SAM et questionnaires subjectifs
- Points forts/faibles calculés à partir des taux de succès par bloc

---

## 7. Rapport de séance et recommandations

### 7.1 Métriques de session (calcul côté backend)

À la fin de chaque séance, les métriques suivantes sont calculées :

| Métrique | Formule | Interprétation |
|---|---|---|
| **Items efficaces** | Δα > 0,05 ET Δβ < -0,05 | Média ayant provoqué une réponse EEG favorable |
| **Taux de succès** | items\_efficaces / items\_joués | Proportion globale d'efficacité |
| **Score de session** | (succès / total\_epochs) × 100 | Score 0-100, affiché au patient |
| **Δα global** | Moyenne alpha fin − moyenne alpha début | Augmentation de la relaxation |
| **Δβ global** | Moyenne beta fin − moyenne beta début | Réduction de l'activation |
| **Progression palier** | Nouveau palier si θ ≥ θ\_max\_palier | Avancement protocole |

### 7.2 Rapport narratif — Claude API (génération asynchrone)

Le rapport narratif est généré de manière **non bloquante** (`asyncio.create_task`) par l'API Claude après la fin de séance :

**Prompt envoyé à Claude (résumé) :**
```
Objectif : {stress_reduction / focus_training}
Durée    : {N} min
Δα global : {+0.07} (cible > +0.05)
Δβ global : {-0.09} (cible < -0.05)
Items efficaces : {M} / {N}
[liste des 6 premiers items avec Δα, Δβ, OK/--]

3 parties :
1) Résumé objectif EEG
2) Ce qui a fonctionné
3) Recommandation prochaine séance
(150 mots max, français, bienveillant, sans markdown)
```

**Diffusion via WebSocket** : dès que le rapport est généré, il est broadcasté vers le frontend via l'action `session_ended`.

### 7.3 Recommandations textuelles (AdaptiveEngine.get_recommendations())

En parallèle du rapport IA, le moteur adaptatif génère des **recommandations standardisées** basées sur le score de session :

| Score | Message de recommandation |
|---|---|
| ≥ 70 | "Excellente session ! Votre concentration est bien au-dessus de la moyenne. Continuez avec des sessions plus longues ou passez au palier suivant." |
| 50–69 | "Bonne session. Votre taux de réussite est dans la zone optimale. Votre cerveau s'adapte progressivement." |
| 30–49 | "Session correcte mais le taux de réussite est un peu bas. Essayez un environnement plus calme et vérifiez le positionnement du casque." |
| < 30 | "Session difficile. Vérifiez le placement des électrodes et essayez des sessions plus courtes (10–15 min)." |

### 7.4 Tableau de bord historique (History.jsx + DashboardPage.jsx)

L'historique des séances est accessible depuis deux vues :

**DashboardPage (patient) :**
- Résumé de la dernière séance (score, état, durée)
- Calendrier du protocole (15 séances, phases, bilans)
- Graphique sparkline des scores récents
- Recommandations du thérapeute (notes cliniques)

**TherapistDashboard (thérapeute) :**
- Liste de tous les patients assignés avec filtres (palier, activité)
- Type de profil EEG (A/B/C), IAPF individuelle
- Courbe des 5 dernières séances (sparkline)
- Contrôles d'ajustement de palier
- Export CSV des données patient

---

## 8. Validation et résultats (à compléter après expérimentations)

### 8.1 Métriques de performance du recommandeur

*[Section à compléter avec données expérimentales]*

- Nombre moyen d'items joués par séance : ~12
- Taux de skip moyen : [à mesurer]
- Convergence Thompson Sampling : convergence observée après [N] séances
- Distribution des types de médias sélectionnés : [graphique à ajouter]

### 8.2 Efficacité de l'adaptation dynamique

*[Section à compléter avec données expérimentales]*

- Évolution du seuil θ sur 15 séances : [courbe à tracer depuis DB Supabase]
- Distribution des taux de succès par bloc : [valider la concentration autour de 40-60 %]
- Progression palier : taux de patients atteignant P2, P3, P4 après [N] semaines

### 8.3 Comparaison seuil fixe vs adaptatif

*[Section à compléter]*

Comparer les métriques EEG (Δα, Δβ) entre :
- Groupe contrôle : seuil fixe θ = 0.5 pour toutes les séances
- Groupe expérimental : seuil adaptatif NEUROCAP (règle Mou et al.)

---

## 9. Conclusion

Le système de neurofeedback adaptatif de NEUROCAP se distingue des approches conventionnelles par la combinaison de trois mécanismes complémentaires :

1. **Sélection de contenu personnalisée** via un bandit contextuel Thompson Sampling couplé à un filtrage par similarité cosinus basé sur des vecteurs cibles issus de la littérature (Thaut 1999, Sammler 2007, Valdez & Mehrabian 1994). Les 843 items du catalogue couvrent l'ensemble du spectre émotionnel et cognitif requis par les protocoles de neurofeedback.

2. **Adaptation dynamique du seuil** à trois échelles temporelles — EWMA en temps réel, règle 40-60 % par blocs de 3 minutes, et recalibration quotidienne — garantissant que chaque utilisateur reste dans sa zone de flow optimale (ni frustration, ni ennui), condition nécessaire à l'apprentissage neuroplastique (Mou et al., 2024).

3. **Personnalisation progressive** via le fine-tuning nocturne du modèle EEG, qui améliore la précision de classification au fil des séances et réduit la variabilité inter-séances inhérente aux électrodes frontales sèches.

---

## Références bibliographiques (à intégrer dans la bibliographie globale)

- Adomavicius, G. & Tuzhilin, A. (2005). Toward the next generation of recommender systems. *IEEE TKDE*, 17(6), 734–749.
- Berman, M.G. et al. (2014). Dimensionality of visual complexity. *Cogn. Sci.*
- Birbaumer, N. et al. (1999). Slow cortical potentials and their role in neurofeedback. *Neuropsychobiol.*, 40(1), 52–60.
- Chapelle, O. & Li, L. (2011). Empirical evaluation of Thompson Sampling. *NeurIPS*.
- Clement, B. et al. (2015). Multi-armed bandits for intelligent tutoring systems. *JEDM*.
- Grill-Spector, K. & Malach, R. (2001). fMR-adaptation: a tool for studying functional properties of human cortical neurons. *Acta Psychol.*, 107(1-3), 293–321.
- Lops, P. et al. (2011). Content-based recommender systems: State of the art and trends. In *Recommender Systems Handbook*.
- Makeig, S. et al. (1999). Functionally independent components of the late positive event-related potential. *J. Neurosci.*, 19(7), 2665–2680.
- Mou, X. et al. (2024). Adaptive threshold neurofeedback for cognitive training. *J. Neural Eng.*
- Sammler, D. et al. (2007). Music and emotion: Electrophysiological correlates of the processing of pleasant and unpleasant music. *Psychophysiology*, 44(2), 293–304.
- Sitaram, R. et al. (2017). Closed-loop brain training: the science of neurofeedback. *Nat. Rev. Neurosci.*, 18(2), 86–100.
- Thaut, M.H. et al. (1999). Rhythm in human motor control and music. *Eur. J. Cognitive Psychol.*
- Valdez, P. & Mehrabian, A. (1994). Effects of color on emotions. *J. Exp. Psychol. Gen.*, 123(4), 394–409.
- Vygotsky, L.S. (1978). *Mind in Society*. Harvard University Press.
- Zander, T.O. & Kothe, C. (2011). Towards passive brain-computer interfaces: applying brain-computer interface technology to human-machine systems in general. *J. Neural Eng.*, 8(2), 025005.

---

## Notes de rédaction

### Figures à créer/insérer

1. **Figure N.1** — Schéma de la boucle de neurofeedback fermée (repris du diagramme ci-dessus)
2. **Figure N.2** — Architecture trois couches du moteur de recommandation
3. **Figure N.3** — Distribution des 843 items par type et condition (diagramme circulaire ou barres)
4. **Figure N.4** — Illustration du Thompson Sampling : évolution des distributions Beta(α,β) au fil des séances
5. **Figure N.5** — Règle d'adaptation 40-60 % (courbe de flow de Csikszentmihalyi avec zones)
6. **Figure N.6** — Progression des paliers P1→P4 (timeline avec exemple de trajectoire)
7. **Figure N.7** — Capture d'écran de FeedbackSession.jsx (interface en cours de séance)
8. **Figure N.8** — Exemple de rapport IA post-séance (FeedbackReport.jsx)

### Équations à formater en LaTeX

```latex
% EWMA
\hat{x}(t) = \alpha \cdot x(t) + (1-\alpha) \cdot \hat{x}(t-1), \quad \alpha = 0{,}3

% Similarité cosinus
\text{sim}(\mathbf{v}_c, \mathbf{v}_i) = \frac{\mathbf{v}_c \cdot \mathbf{v}_i}{\|\mathbf{v}_c\| \cdot \|\mathbf{v}_i\|}

% Thompson Sampling
\theta_i \sim \text{Beta}(\alpha_i, \beta_i)

% Score combiné
\text{score}_i = \text{sim}_i \times \theta_i

% Recalibration inter-session
\theta_{\text{jour}} = 0{,}70 \times \mu_{\text{LT}} + 0{,}30 \times \theta_{\text{mesuré}}

% Indice d'engagement
I_E = \frac{P_\beta}{P_\alpha + P_\theta}
```

### Points à développer lors de la rédaction finale

- [ ] Ajouter données expérimentales (sections 8.1, 8.2, 8.3)
- [ ] Insérer captures d'écran de l'interface
- [ ] Tracer courbes d'évolution θ sur 15 séances (exporter depuis Supabase)
- [ ] Ajouter comparaison avec état de l'art : BCI2000, OpenNFB, MindMaze
- [ ] Détailler le rôle du thérapeute dans l'ajustement des paliers
- [ ] Mentionner les aspects éthiques (données EEG patient, RGPD, anonymisation Supabase)
