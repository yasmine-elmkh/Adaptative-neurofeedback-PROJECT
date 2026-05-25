// GameFeedback.jsx — Routeur intelligent : Cloudinary JSON → composant spécialisé
// Préfixes détectés : CAL_ ENI_ MEM_ SDK_ PUZ_  (fetch JSON + gameData prop)
// COL_ / *.svg → coloriage  |  ILL_ / *.html → iframe  |  sans URL → sélecteur intégré
import { useEffect, useState } from "react";
import SudokuGame from "./games/SudokuGame";
import MemoryGame from "./games/MemoryGame";
import PuzzleGame from "./games/PuzzleGame";
import EnigmeGame from "./games/EnigmeGame";
import CalculGame from "./games/CalculGame";

const COLORS = ["#C5D3E8","#B87B9E","#2B2A4A","#F0C3D7","#A8D5C2","#F7E8B0","#D4A5C9","#8EC5FC","#F9A8D4","#6EE7B7"];

const BUILTIN_GAMES = [
  { key: "sudoku",  label: "🔢 Sudoku",          Component: SudokuGame },
  { key: "memoire", label: "🃏 Mémoire",          Component: MemoryGame },
  { key: "puzzle",  label: "🧩 Taquin 3×3",       Component: PuzzleGame },
  { key: "enigme",  label: "🦉 Énigmes",          Component: EnigmeGame },
  { key: "calcul",  label: "🧮 Calcul Mental",    Component: CalculGame },
];

// Détecte le type de jeu depuis le nom de fichier
// Priorité 1 : préfixes CSV (CAL_, SDK_, ENI_, MEM_, PUZ_)
// Priorité 2 : mots-clés génériques
function detectGameType(filename) {
  const upper = (filename || "").toUpperCase();
  const lower = (filename || "").toLowerCase();
  const prefix = upper.slice(0, 4);

  if (prefix === "CAL_") return "calcul";
  if (prefix === "ENI_") return "enigme";
  if (prefix === "MEM_") return "memoire";
  if (prefix === "SDK_") return "sudoku";
  if (prefix === "PUZ_") return "puzzle";
  if (prefix === "COL_") return "coloriage";
  if (prefix === "ILL_") return "illusion";

  if (lower.includes("sudoku"))                                                 return "sudoku";
  if (lower.includes("memory") || lower.includes("memoire") || lower.includes("mémoire")) return "memoire";
  if (lower.includes("puzzle") || lower.includes("taquin"))                     return "puzzle";
  if (lower.includes("enigme") || lower.includes("énigme"))                     return "enigme";
  if (lower.includes("calcul") || lower.includes("math") || lower.includes("arithm")) return "calcul";

  return null;
}

const GAME_COMPONENT = { sudoku: SudokuGame, memoire: MemoryGame, puzzle: PuzzleGame, enigme: EnigmeGame, calcul: CalculGame };

export default function GameFeedback({ game, eegState = "neutral", onWin }) {
  const [gameData,      setGameData]      = useState(null);
  const [fetching,      setFetching]      = useState(false);
  const [svgContent,    setSvgContent]    = useState(null);
  const [selectedColor, setSelectedColor] = useState(COLORS[0]);
  const [manualGame,    setManualGame]    = useState(null);

  const url      = game?.url_cloudinary || game?.url || null;
  const filename = game?.filename || game?.name || "";
  const gameType = detectGameType(filename);

  // ── Fetch JSON pour les jeux Cloudinary (CAL, ENI, MEM, SDK, PUZ) ─────────
  useEffect(() => {
    setGameData(null);
    setSvgContent(null);
    if (!url) return;

    if (url.endsWith(".svg") || gameType === "coloriage") {
      fetch(url).then(r => r.text()).then(setSvgContent).catch(console.error);
    } else if (url.endsWith(".json") && GAME_COMPONENT[gameType]) {
      setFetching(true);
      fetch(url)
        .then(r => r.json())
        .then(data => { setGameData(data); setFetching(false); })
        .catch(() => setFetching(false));
    }
  }, [url]);

  // ── 1. Jeu Cloudinary JSON (SDK_, CAL_, ENI_, MEM_, PUZ_) ─────────────────
  if (gameType && GAME_COMPONENT[gameType]) {
    if (url?.endsWith(".json")) {
      if (fetching) return (
        <div style={{ textAlign: "center", padding: "2rem", color: "#9A8BAE", fontFamily: "'Outfit',sans-serif" }}>
          <div style={{ fontSize: 20, marginBottom: 8 }}>⏳</div>
          Chargement du jeu…
        </div>
      );
      const Comp = GAME_COMPONENT[gameType];
      return <Comp eegState={eegState} onWin={onWin} gameData={gameData || undefined} />;
    }
    // Pas d'URL mais type connu → mode intégré sans données
    const Comp = GAME_COMPONENT[gameType];
    return <Comp eegState={eegState} onWin={onWin} />;
  }

  // ── 2. SVG coloriage (COL_*.svg) ─────────────────────────────────────────
  if (url?.endsWith(".svg") && svgContent) {
    return (
      <div style={{ borderRadius: 12, overflow: "hidden", background: "#F7F3FA" }}>
        <div style={{ display: "flex", gap: 6, flexWrap: "wrap", padding: "0.5rem", background: "#D9C9E5" }}>
          {COLORS.map(c => (
            <div key={c} onClick={() => setSelectedColor(c)} style={{
              width: 24, height: 24, borderRadius: "50%", background: c, cursor: "pointer",
              border: selectedColor === c ? "2px solid white" : "1px solid #ccc",
              boxShadow: "0 1px 3px rgba(0,0,0,0.2)"
            }} />
          ))}
        </div>
        <div
          dangerouslySetInnerHTML={{ __html: svgContent }}
          style={{ width: "100%", padding: "1rem", cursor: "pointer" }}
          onClick={e => {
            const t = e.target;
            if (["path","circle","rect","ellipse","polygon"].includes(t.tagName.toLowerCase()))
              t.style.fill = selectedColor;
          }}
        />
      </div>
    );
  }

  // ── 3. HTML illusion ou autre URL (iframe) ────────────────────────────────
  if (url) {
    return (
      <iframe src={url} sandbox="allow-scripts allow-same-origin"
        style={{ width: "100%", height: 420, border: "none", borderRadius: 12 }}
        title={filename} />
    );
  }

  // ── 4. Aucun média — sélecteur manuel des jeux intégrés ──────────────────
  if (manualGame) {
    const Comp = GAME_COMPONENT[manualGame];
    if (Comp) return (
      <div>
        <button onClick={() => setManualGame(null)} style={{
          fontSize: 11, color: "#9A8BAE", background: "none", border: "none",
          cursor: "pointer", marginBottom: 8, padding: 0,
        }}>← Choisir un autre jeu</button>
        <Comp eegState={eegState} onWin={onWin} />
      </div>
    );
  }

  return (
    <div style={{ fontFamily: "'Outfit',sans-serif", padding: "1rem" }}>
      <div style={{ fontSize: 12, color: "#9A8BAE", marginBottom: 12, textAlign: "center" }}>
        Choisir un jeu :
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(2,1fr)", gap: 8 }}>
        {BUILTIN_GAMES.map(({ key, label }) => (
          <button key={key} onClick={() => setManualGame(key)} style={{
            padding: "12px 8px", borderRadius: 12,
            border: "1.5px solid rgba(184,123,158,0.25)",
            background: "rgba(255,255,255,0.4)",
            color: "#2B2A4A", fontSize: 13, fontWeight: 600, cursor: "pointer",
          }}>
            {label}
          </button>
        ))}
      </div>
    </div>
  );
}
