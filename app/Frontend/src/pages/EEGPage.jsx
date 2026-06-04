import { useNavigate, useLocation } from 'react-router-dom'
import { Activity, Upload } from 'lucide-react'
import EEGLive from './EEGLive'
import EEGFile from './EEGFile'

const TABS = [
  { key: 'live',   Icon: Activity, label: 'EEG Temps Réel', path: '/eeg/live'   },
  { key: 'upload', Icon: Upload,   label: 'Téléverser Fichier', path: '/eeg/upload' },
]

export default function EEGPage({ tab = 'live' }) {
  const navigate = useNavigate()
  const activeTab = tab

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 py-4 space-y-0">
      {/* ── Tabs ── */}
      <div className="flex gap-0 border-b border-nc-border mb-0">
        {TABS.map(({ key, Icon, label, path }) => (
          <button
            key={key}
            onClick={() => navigate(path)}
            className={`flex items-center gap-2 px-5 py-3 text-sm font-medium border-b-2 transition-all -mb-px
              ${activeTab === key
                ? 'border-nc-accent text-nc-accent'
                : 'border-transparent text-nc-muted hover:text-nc-text hover:bg-nc-surface2/40'}`}
          >
            <Icon className="w-4 h-4" />
            {label}
          </button>
        ))}
      </div>

      {/* ── Content ── */}
      {activeTab === 'live'   && <EEGLive   embedded />}
      {activeTab === 'upload' && <EEGFile   embedded />}
    </div>
  )
}
