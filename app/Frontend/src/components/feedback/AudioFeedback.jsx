export default function AudioFeedback({ src }) {
  return (
    <div style={{ padding: '1.5rem', textAlign: 'center', background: 'rgba(255,255,255,0.3)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.5)' }}>
      <div style={{ fontSize: 36, marginBottom: 12 }}>🎵</div>
      <audio controls src={src} style={{ width: '100%', accentColor: '#B87B9E' }} />
    </div>
  )
}
