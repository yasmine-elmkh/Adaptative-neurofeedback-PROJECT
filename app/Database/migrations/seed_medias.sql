-- ═══════════════════════════════════════════════════════════════════
-- Seed médias NeuroCap — Supabase Storage
-- ═══════════════════════════════════════════════════════════════════
--
-- ÉTAPES PRÉALABLES (Supabase Dashboard) :
--   1. Storage → Create bucket → nom : "neurofeedback-media" → Public ✓
--   2. Uploader vos fichiers (audio, image, video) dans ce bucket
--   3. Remplacer YOUR_PROJECT_ID par votre Project Reference
--      (Settings → General → Reference ID, ex: abcdefghijklmnop)
--
-- Format URL Supabase Storage public :
--   https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/<fichier>
--
-- ═══════════════════════════════════════════════════════════════════

-- Nettoyer les anciennes entrées seed si besoin
DELETE FROM medias WHERE url LIKE '%supabase.co/storage%' OR url LIKE '%seed_%' OR url LIKE '%soundhelix%' OR url LIKE '%picsum%' OR url LIKE '%googleapis%';

-- ── AUDIO ─────────────────────────────────────────────────────────────────────

-- Relaxation / Stress
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'audio', 'pluie_douce.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/pluie_douce.mp3',
 'stress', 1, 180, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'vagues_ocean.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/vagues_ocean.mp3',
 'stress', 1, 210, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'foret_oiseaux.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/foret_oiseaux.mp3',
 'stress', 1, 240, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'binaural_alpha.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/binaural_alpha.mp3',
 'stress', 2, 300, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'bol_tibetain.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/bol_tibetain.mp3',
 'stress', 1, 180, 1.0, 1.0);

-- Concentration / Focus
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'audio', 'musique_focus.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/musique_focus.mp3',
 'focus', 1, 300, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'bruit_blanc.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/bruit_blanc.mp3',
 'focus', 1, 600, 1.0, 1.0),

(gen_random_uuid(), 'audio', 'binaural_beta.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/binaural_beta.mp3',
 'focus', 2, 300, 1.0, 1.0);

-- Neutre (tous états)
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'audio', 'silence_guide.mp3',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/audio/silence_guide.mp3',
 'all', 1, 120, 1.0, 1.0);

-- ── IMAGES ────────────────────────────────────────────────────────────────────

-- Relaxation / Stress
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'image', 'lac_montagne.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/lac_montagne.jpg',
 'stress', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'image', 'foret_verte.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/foret_verte.jpg',
 'stress', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'image', 'coucher_soleil.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/coucher_soleil.jpg',
 'stress', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'image', 'plage_tropicale.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/plage_tropicale.jpg',
 'stress', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'image', 'prairie_fleurs.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/prairie_fleurs.jpg',
 'stress', 1, 120, 1.0, 1.0);

-- Concentration / Focus
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'image', 'mandala_bleu.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/mandala_bleu.jpg',
 'focus', 2, 180, 1.0, 1.0),

(gen_random_uuid(), 'image', 'mandala_rouge.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/mandala_rouge.jpg',
 'focus', 2, 180, 1.0, 1.0),

(gen_random_uuid(), 'image', 'geometrie_sacree.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/geometrie_sacree.jpg',
 'focus', 2, 180, 1.0, 1.0),

(gen_random_uuid(), 'image', 'ciel_etoile.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/ciel_etoile.jpg',
 'focus', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'image', 'fractal_cosmique.jpg',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/images/fractal_cosmique.jpg',
 'focus', 3, 180, 1.0, 1.0);

-- ── VIDÉOS ────────────────────────────────────────────────────────────────────

-- Relaxation / Stress
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'video', 'riviere_foret.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/riviere_foret.mp4',
 'stress', 1, 180, 1.0, 1.0),

(gen_random_uuid(), 'video', 'vagues_mer.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/vagues_mer.mp4',
 'stress', 1, 150, 1.0, 1.0),

(gen_random_uuid(), 'video', 'pluie_fenetre.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/pluie_fenetre.mp4',
 'stress', 1, 120, 1.0, 1.0),

(gen_random_uuid(), 'video', 'feu_cheminee.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/feu_cheminee.mp4',
 'stress', 1, 300, 1.0, 1.0);

-- Concentration / Focus
INSERT INTO medias (id, type, filename, url, eeg_target_state, difficulty_level, duration_seconds, item_weights_alpha, item_weights_beta) VALUES
(gen_random_uuid(), 'video', 'espace_timelapse.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/espace_timelapse.mp4',
 'focus', 2, 180, 1.0, 1.0),

(gen_random_uuid(), 'video', 'respiration_guide.mp4',
 'https://YOUR_PROJECT_ID.supabase.co/storage/v1/object/public/neurofeedback-media/videos/respiration_guide.mp4',
 'focus', 1, 120, 1.0, 1.0);

-- ── Vérification ─────────────────────────────────────────────────────────────
SELECT type, eeg_target_state, COUNT(*) as nb
FROM medias
GROUP BY type, eeg_target_state
ORDER BY type, eeg_target_state;
