const STATE_THEME = {
  stress:     { color: '#E87B9E', label: 'STRESS',   icon: '😰' },
  relax:      { color: '#7BC4A0', label: 'RELAX',    icon: '🌿' },
  focus:      { color: '#7BA8C4', label: 'FOCUS',    icon: '🎯' },
  distracted: { color: '#C4A87B', label: 'DISTRAIT', icon: '😶' },
  neutral:    { color: '#9A8BAE', label: 'NEUTRE',   icon: '😌' },
}

export default function BrainStateIndicator({ state, confidence }) {
  const theme = STATE_THEME[state] || STATE_THEME.neutral
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        padding: '8px 16px', borderRadius: 40,
        border: `1.5px solid ${theme.color}60`,
        background: `${theme.color}18`,
        color: theme.color,
        fontWeight: 600, fontSize: 13, letterSpacing: 0.5,
      }}>
        <div style={{
          width: 8, height: 8, borderRadius: '50%',
          background: theme.color,
          animation: 'nc-blink-dot 1.5s ease-in-out infinite',
        }} />
        <style>{`@keyframes nc-blink-dot{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.6;transform:scale(.8)}}`}</style>
        <span style={{ fontSize: 15 }}>{theme.icon}</span>
        {theme.label}
      </div>
      {confidence != null && (
        <span style={{ fontSize: 10, color: '#9A8BAE', fontFamily: 'monospace' }}>
          {Math.round(confidence * 100)}%
        </span>
      )}
    </div>
  )
}
