# backend-signal/feedback/media_analyzer.py
import numpy as np
from supabase_client import supabase

def get_user_preferences(user_id: str):
    """Récupère les préférences agrégées de l'utilisateur (depuis user_media_preferences)."""
    resp = supabase.table('user_media_preferences').select('*').eq('user_id', user_id).execute()
    if resp.data:
        return resp.data[0]
    return None

def get_media_features(media_id: int):
    """Récupère les features du média depuis la table medias."""
    resp = supabase.table('medias').select('type, categorie, features').eq('id', media_id).execute()
    if resp.data:
        return resp.data[0]
    return None

def explain_image(features, user_pref=None, eeg_state=None):
    """Génère une justification pour une image basée sur ses caractéristiques."""
    brightness = features.get('brightness_global', 0.5)
    saturation = features.get('saturation_mean', 0.5)
    contrast = features.get('contrast_rms', 0.5)
    hue = features.get('hue_mean', 0.5)
    homogeneity = features.get('glcm_homogeneity', 0.5)
    symmetry = features.get('symmetry_h', 0.5)

    # Détection de la teinte dominante
    if hue < 0.1 or hue > 0.9:
        hue_desc = "rouge/chaude"
        calm = False
    elif 0.2 < hue < 0.4:
        hue_desc = "verte"
        calm = True
    elif 0.5 < hue < 0.7:
        hue_desc = "bleue"
        calm = True
    else:
        hue_desc = "neutre"
        calm = False

    # Justification selon état EEG
    if eeg_state == 'stress':
        if calm:
            reason = f"Les teintes {hue_desc} (saturation {saturation:.2f}, luminosité {brightness:.2f}) favorisent la relaxation."
        else:
            reason = f"Bien que les couleurs soient {hue_desc}, la saturation modérée ({saturation:.2f}) atténue la stimulation."
    elif eeg_state == 'focus':
        if contrast > 0.6:
            reason = f"Le contraste élevé ({contrast:.2f}) et la symétrie ({symmetry:.2f}) aident à maintenir l'attention."
        else:
            reason = f"Une composition douce (homogénéité {homogeneity:.2f}) pour ne pas distraire."
    else:
        reason = f"Une harmonie visuelle (homogénéité {homogeneity:.2f}) adaptée à un état neutre."

    # Comparaison avec les préférences utilisateur (si disponibles)
    user_note = ""
    if user_pref and 'avg_brightness' in user_pref:
        if abs(brightness - user_pref['avg_brightness']) < 0.1:
            user_note = " Cette luminosité correspond à vos préférences habituelles."
        elif brightness > user_pref['avg_brightness']:
            user_note = " Cette image est plus lumineuse que ce que vous appréciez généralement."
        else:
            user_note = " Cette image est plus douce que vos choix récents."

    return reason + user_note

def explain_audio(features, user_pref=None, eeg_state=None):
    tempo = features.get('tempo_bpm', 0)
    rms = features.get('rms_mean', 0.2)
    flux = features.get('spectral_flux', 0.1)
    harm_ratio = features.get('harm_perc_ratio', 0.5)
    stationarity = features.get('spectral_stationarity', 0.5)

    if eeg_state == 'stress':
        if tempo < 70:
            reason = f"Tempo bas ({tempo:.0f} BPM) et énergie faible (RMS {rms:.2f}) → apaisant."
        else:
            reason = f"Même si le tempo est modéré ({tempo:.0f} BPM), l'harmonie (ratio {harm_ratio:.2f}) reste relaxante."
    elif eeg_state == 'focus':
        if 70 < tempo < 100:
            reason = f"Tempo optimal ({tempo:.0f} BPM) pour la concentration, avec une stabilité spectrale élevée ({stationarity:.2f})."
        else:
            reason = f"Le flux spectral modéré ({flux:.2f}) évite les distractions."
    else:
        reason = f"Une ambiance neutre (harmonie {harm_ratio:.2f}) pour ne pas perturber."

    return reason

def explain_video(features, user_pref=None, eeg_state=None):
    motion = features.get('optical_flow_mean', 0)
    changes = features.get('scene_change_rate', 0)
    regularity = features.get('motion_regularity', 1.0)

    if eeg_state == 'stress':
        if motion < 0.1:
            reason = f"Mouvement très faible (flux optique {motion:.3f}) → apaisant."
        else:
            reason = f"Bien que le mouvement soit modéré, la régularité ({regularity:.2f}) évite la sur-stimulation."
    elif eeg_state == 'focus':
        if changes < 0.1:
            reason = f"Peu de changements de scène ({changes:.2f}) → maintien de l'attention."
        else:
            reason = f"Un rythme de changement modéré pour rester alerte."
    else:
        reason = f"Un mouvement équilibré (régularité {regularity:.2f}) pour un état neutre."

    return reason

def explain_game(features, user_pref=None, eeg_state=None):
    # Les jeux n'ont pas de features audio/vidéo complexes dans le CSV,
    # mais on peut utiliser le mapping ou le niveau adaptatif.
    return "Ce jeu ajuste sa difficulté à votre état pour maintenir un engagement optimal."

def generate_justification(media_id: int, user_id: str = None, eeg_state: str = 'neutral'):
    """
    Retourne un dict avec:
        - justification (str)
        - guide (list of str) - dynamique basé sur les features
        - type (str)
    """
    media = get_media_features(media_id)
    if not media:
        return {"error": "Media not found"}

    media_type = media['type']
    features = media.get('features', {})
    user_pref = get_user_preferences(user_id) if user_id else None

    if media_type == 'image':
        justification = explain_image(features, user_pref, eeg_state)
        # Guide dynamique pour image
        brightness = features.get('brightness_global', 0.5)
        contrast = features.get('contrast_rms', 0.5)
        guide = [
            "👁️ Regardez les détails, les nuances de couleurs.",
            f"🔆 Luminosité : {'élevée' if brightness > 0.6 else 'modérée' if brightness > 0.3 else 'basse'} → {'stimule' if brightness > 0.6 else 'apaise'}.",
            f"🎨 Contraste : {'fort' if contrast > 0.6 else 'doux'} → {'capte l’attention' if contrast > 0.6 else 'détend'}.",
            "🧘 Laissez votre regard se promener sans forcer."
        ]
    elif media_type == 'audio':
        justification = explain_audio(features, user_pref, eeg_state)
        tempo = features.get('tempo_bpm', 0)
        guide = [
            "🎧 Fermez les yeux si possible.",
            f"🎵 Tempo : {'lent' if tempo < 70 else 'modéré' if tempo < 100 else 'rapide'} → {'relaxant' if tempo < 70 else 'dynamisant'}.",
            "🧘 Concentrez-vous sur votre respiration en écoutant.",
            "🌿 Laissez les vibrations vous imprégner."
        ]
    elif media_type == 'video':
        justification = explain_video(features, user_pref, eeg_state)
        motion = features.get('optical_flow_mean', 0)
        guide = [
            "🎬 Suivez le mouvement sans tension.",
            f"🚶 Mouvement : {'très doux' if motion < 0.1 else 'modéré' if motion < 0.3 else 'rapide'} → {'apaise' if motion < 0.1 else 'stimule l’attention'}.",
            "👀 Observez les transitions, les couleurs.",
            "💨 Laissez-vous porter par l'ambiance."
        ]
    else:  # game
        justification = explain_game(features, user_pref, eeg_state)
        guide = [
            "🎮 Jouez à votre rythme.",
            "🧠 Le jeu s'adapte à votre état.",
            "⚖️ Ne cherchez pas la perfection, restez détendu.",
            "✨ Amusez-vous, c'est l'essentiel."
        ]

    return {
        "justification": justification,
        "guide": guide,
        "type": media_type
    }