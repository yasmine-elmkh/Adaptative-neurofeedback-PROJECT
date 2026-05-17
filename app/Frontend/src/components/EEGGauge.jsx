export default function EEGGauge({ value = 0, label = 'Concentration', color = '#00d4ff', size = 140 }) {
  const radius = (size - 10) / 2
  const circumference = 2 * Math.PI * radius
  const percent = Math.min(1, Math.max(0, value))
  const offset = circumference * (1 - percent)
  return (
    <div className="flex flex-col items-center gap-2">
      <svg width={size} height={size} className="transform -rotate-90">
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke="#2a3654" strokeWidth="10"/>
        <circle cx={size/2} cy={size/2} r={radius} fill="none" stroke={color} strokeWidth="10" strokeLinecap="round" strokeDasharray={circumference} strokeDashoffset={offset} style={{transition:'stroke-dashoffset 0.4s ease'}}/>
      </svg>
      <div className="absolute flex flex-col items-center justify-center" style={{width:size,height:size}}><span className="text-3xl font-bold">{(percent*100).toFixed(0)}</span><span className="text-xs text-neuro-muted">%</span></div>
      <span className="text-xs font-medium text-neuro-muted uppercase tracking-wider">{label}</span>
    </div>
  )
}

export function DualGauge({ concentration, stress }) {
  return (
    <div className="flex gap-8">
      <EEGGauge value={concentration} label="Concentration" color="#00d4ff" />
      <EEGGauge value={stress} label="Stress" color="#ef4444" />
    </div>
  )
}