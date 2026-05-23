// AudioFeedback.jsx
export default function AudioFeedback({ src, filename }) {
  return (
    <div style={{ padding: "1rem", textAlign: "center", background: "var(--color-background-secondary)", borderRadius: 12 }}>
      <p style={{ marginBottom: "0.5rem", fontSize: 14, color: "var(--color-text-secondary)" }}>
        {filename || "Fichier audio"}
      </p>
      <audio controls src={src} style={{ width: "100%", accentColor: "#B87B9E" }} />
    </div>
  );
}