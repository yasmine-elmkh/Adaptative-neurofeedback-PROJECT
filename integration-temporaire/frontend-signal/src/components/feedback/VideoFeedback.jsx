// VideoFeedback.jsx
export default function VideoFeedback({ src, title }) {
  return (
    <div style={{ margin: "1rem 0" }}>
      <video controls src={src} style={{ width: "100%", borderRadius: 12, maxHeight: 400 }} title={title} />
    </div>
  );
}