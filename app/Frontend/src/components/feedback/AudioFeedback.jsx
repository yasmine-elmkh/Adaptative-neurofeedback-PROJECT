export default function AudioFeedback({ src, filename }) {
  return (
    <div style={{ padding: '1rem', textAlign: 'center', background: 'rgba(255,255,255,0.3)', borderRadius: 12, border: '1px solid rgba(255,255,255,0.5)' }}>
      <p style={{ marginBottom: '0.5rem', fontSize: 13, color: '#9A8BAE' }}>{filename || 'Fichier audio'}</p>
      <audio controls src={src} style={{ width: '100%', accentColor: '#B87B9E' }} />
    </div>
  )
}
