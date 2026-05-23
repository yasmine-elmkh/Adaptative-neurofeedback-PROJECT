import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { useFeedbackEngine } from "../../hooks/useFeedbackEngine";
import AudioFeedback from "./AudioFeedback";
import ImageFeedback from "./ImageFeedback";
import VideoFeedback from "./VideoFeedback";
import GameFeedback from "./GameFeedback";
import FeedbackSelector from "./FeedbackSelector";
import FeedbackJustification from "./FeedbackJustification";
import BrainStateIndicator from "./BrainStateIndicator";

// ── Palette Bleu Mauve ────────────────────────────────────────────────────────
const P = {
  bg: '#C5D3E8', card: 'rgba(247,243,250,0.45)',
  accent: '#B87B9E', accent2: '#9A6B8E',
  text: '#2B2A4A', text2: '#9A8BAE',
  shadow: 'rgba(180,169,196,0.45)',
};

const STATE_LABELS = { stress: 'STRESS', focus: 'FOCUS', relax: 'RELAX', distracted: 'DISTRAIT', neutral: 'NEUTRE' };
const STATE_OPTIONS = ['stress', 'focus', 'relax', 'distracted', 'neutral'];

export default function FeedbackSession() {
  const location = useLocation();
  const navigate = useNavigate();
  const { eegState: initState, features, confidence } = location.state || {};
  const [sessionId, setSessionId] = useState(null);
  const [currentMedia, setCurrentMedia] = useState(null);
  const [phase, setPhase] = useState("setup");
  const [loading, setLoading] = useState(false);
  const [rapport, setRapport] = useState(null);
  const [showForm, setShowForm] = useState(false);
  const [selectedState, setSelectedState] = useState(initState || "neutral");

  const { startSession, recommend, submitFeedback, endSession } = useFeedbackEngine();

  useEffect(() => {
    if (phase === "session" && !currentMedia && sessionId) {
      loadRecommendation();
    }
  }, [phase, sessionId, currentMedia]);

  const loadRecommendation = async () => {
    const media = await recommend(sessionId, selectedState, features || {});
    setCurrentMedia(media);
  };

  const handleStart = async () => {
    setLoading(true);
    const sid = await startSession("demo", "stress_reduction");
    setSessionId(sid);
    setPhase("session");
    setLoading(false);
  };

  const handleFeedback = async (liked, ressenti, noteC, noteS) => {
    await submitFeedback(sessionId, currentMedia.id, liked, ressenti, noteC, noteS);
    setShowForm(false);
    await loadRecommendation();
  };

  const handleEnd = async () => {
    const report = await endSession(sessionId);
    setRapport(report);
    setPhase("rapport");
  };

  if (phase === "setup") {
    return (
      <div style={{ background: P.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', fontFamily: "'Outfit',sans-serif" }}>
        <div style={{ width: '100%', maxWidth: 480, background: P.card, borderRadius: 24, padding: '40px', border: '1px solid rgba(255,255,255,0.6)', backdropFilter: 'blur(20px)', boxShadow: `0 20px 60px ${P.shadow}` }}>
          <div style={{ fontSize: 28, fontWeight: 700, textAlign: 'center', marginBottom: 6, background: `linear-gradient(135deg, ${P.text}, ${P.accent})`, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent' }}>
            NeuroCap EEG
          </div>
          <div style={{ fontSize: 13, color: P.text2, textAlign: 'center', marginBottom: 28 }}>
            Neurofeedback adaptatif — ENSAM Rabat · PFE 2026
          </div>

          <label style={{ display: 'block', fontSize: 11, color: P.text2, fontFamily: "'DM Mono',monospace", letterSpacing: 1.5, textTransform: 'uppercase', marginBottom: 6 }}>
            État EEG de départ
          </label>
          <select
            value={selectedState}
            onChange={e => setSelectedState(e.target.value)}
            style={{ width: '100%', padding: '12px 16px', borderRadius: 12, fontSize: 14, border: '1.5px solid rgba(255,255,255,0.5)', background: 'rgba(255,255,255,0.4)', color: P.text, fontFamily: "'Outfit',sans-serif", outline: 'none', marginBottom: 20 }}
          >
            {STATE_OPTIONS.map(s => <option key={s} value={s}>{STATE_LABELS[s]}</option>)}
          </select>

          <button
            onClick={handleStart}
            disabled={loading}
            style={{ width: '100%', padding: 16, borderRadius: 18, border: 'none', background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`, color: 'white', fontSize: 15, fontWeight: 700, cursor: 'pointer', boxShadow: '0 6px 24px rgba(184,123,158,0.45)' }}
          >
            {loading ? 'Chargement…' : '→ Démarrer la session'}
          </button>
        </div>
      </div>
    );
  }

  if (phase === "rapport") {
    return (
      <div style={{ background: P.bg, minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', padding: '2rem', fontFamily: "'Outfit',sans-serif" }}>
        <div style={{ width: '100%', maxWidth: 600, background: P.card, borderRadius: 24, padding: '32px', border: '1px solid rgba(255,255,255,0.6)', backdropFilter: 'blur(20px)', boxShadow: `0 20px 60px ${P.shadow}` }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: P.text2, letterSpacing: 2.5, textTransform: 'uppercase', fontFamily: "'DM Mono',monospace", marginBottom: 16 }}>
            📊 Rapport de session
          </div>
          <pre style={{ fontSize: 11, color: P.text, background: 'rgba(255,255,255,0.3)', padding: 16, borderRadius: 12, overflowX: 'auto', lineHeight: 1.6 }}>
            {JSON.stringify(rapport, null, 2)}
          </pre>
          <button
            onClick={() => navigate('/')}
            style={{ marginTop: 16, width: '100%', padding: 13, borderRadius: 18, border: 'none', background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`, color: 'white', fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
          >
            ← Fermer
          </button>
        </div>
      </div>
    );
  }

  return (
    <div style={{ background: P.bg, minHeight: '100vh', padding: '1rem', fontFamily: "'Outfit',sans-serif" }}>
      <BrainStateIndicator state={selectedState} confidence={confidence} />
      {currentMedia && (
        <div style={{ background: P.card, borderRadius: 18, padding: '1rem', marginTop: '0.5rem', border: '1px solid rgba(255,255,255,0.6)', backdropFilter: 'blur(10px)', boxShadow: `0 4px 20px ${P.shadow}` }}>
          <div style={{ fontSize: 15, fontWeight: 600, color: P.text, marginBottom: 12 }}>{currentMedia.filename}</div>
          {currentMedia.type === "audio" && <AudioFeedback src={currentMedia.url_cloudinary} />}
          {currentMedia.type === "image" && <ImageFeedback src={currentMedia.url_cloudinary} />}
          {currentMedia.type === "video" && <VideoFeedback src={currentMedia.url_cloudinary} />}
          {currentMedia.type === "game"  && <GameFeedback  game={currentMedia} eegState={selectedState} onWin={(r) => console.log("[Game] win", r)} />}
          <div style={{ marginTop: 12 }}>
            <FeedbackJustification type={currentMedia.type} state={selectedState} />
          </div>
          {!showForm ? (
            <button
              onClick={() => setShowForm(true)}
              style={{ width: '100%', padding: 12, borderRadius: 18, border: 'none', background: `linear-gradient(135deg, ${P.accent}, ${P.accent2})`, color: 'white', marginTop: 12, fontSize: 14, fontWeight: 600, cursor: 'pointer' }}
            >
              Évaluer ce stimulus
            </button>
          ) : (
            <div style={{ marginTop: 12 }}>
              <FeedbackSelector onSubmit={handleFeedback} onSkip={loadRecommendation} />
            </div>
          )}
          <button
            onClick={handleEnd}
            style={{ width: '100%', marginTop: 10, padding: 12, borderRadius: 18, background: 'rgba(232,123,158,0.15)', border: '1.5px solid rgba(232,123,158,0.4)', color: '#8c4a6a', fontSize: 13, fontWeight: 600, cursor: 'pointer' }}
          >
            ⏹ Terminer la session
          </button>
        </div>
      )}
    </div>
  );
}
