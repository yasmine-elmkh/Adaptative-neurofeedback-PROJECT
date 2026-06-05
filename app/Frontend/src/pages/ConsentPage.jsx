import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  Shield, CheckCircle, Download, ChevronRight,
  AlertCircle, Eye, Users, Database, Lock,
  FileText, Activity,
} from 'lucide-react'
import { useAuthStore } from '../stores'
import API from '../utils/api'

// ─── Sections du texte de consentement ────────────────────────────────────────

const SECTIONS = [
  {
    icon: FileText,
    title: '1. Présentation de l\'étude',
    body: `Vous êtes invité(e) à participer à une étude portant sur l'utilisation d'un
système de neurofeedback EEG portable (NeuroCap) destiné à la régulation du stress
et à l'amélioration de la concentration. Ce système acquiert et analyse votre signal
électroencéphalographique (EEG) en temps réel à l'aide d'une électrode frontale non
invasive.`,
  },
  {
    icon: Activity,
    title: '2. Objectifs',
    body: `L'objectif est d'évaluer l'efficacité d'un protocole de neurofeedback monocanal pour :
(a) réduire les niveaux de stress subjectif et physiologique mesurés par EEG,
(b) améliorer la concentration soutenue lors de tâches cognitives, et
(c) valider les algorithmes de classification des états mentaux développés dans le
cadre du projet NeuroCap.`,
  },
  {
    icon: CheckCircle,
    title: '3. Déroulement de l\'étude',
    items: [
      '<strong>Séance de calibration (S1)</strong> — 30 min. Mesure du profil EEG de référence (fréquence alpha individuelle, seuils de base).',
      '<strong>Séances de neurofeedback (S2 à S15)</strong> — 20 à 30 min chacune, à raison de 1 à 2 séances/semaine sur 7 à 8 semaines.',
      '<strong>Questionnaires</strong> — Évaluation subjective avant et après chaque séance (stress perçu, concentration, qualité du feedback).',
    ],
  },
  {
    icon: Database,
    title: '4. Données collectées',
    items: [
      'Signal EEG brut et filtré (électrode Fp2, 250 Hz, canal unique)',
      'Indicateurs spectraux dérivés (puissances alpha, bêta, thêta ; ratio TBR)',
      'Scores de sessions et résultats de classification (état mental prédit)',
      'Réponses aux questionnaires de suivi',
    ],
  },
  {
    icon: Lock,
    title: '5. Confidentialité et protection des données',
    body: `Toutes les données collectées sont strictement confidentielles. Elles sont anonymisées
avant tout traitement statistique ou publication. Aucune donnée permettant votre identification
ne sera divulguée à des tiers. Les données sont stockées sur des serveurs sécurisés et seront
supprimées à l'issue de l'étude, conformément à la réglementation en vigueur sur la protection
des données personnelles.`,
  },
  {
    icon: Shield,
    title: '6. Risques et bénéfices',
    body: `Le dispositif NeuroCap est non invasif. L'acquisition EEG ne présente aucun risque connu
pour la santé. Les seuls inconforts possibles sont une légère pression mécanique des électrodes sur
le cuir chevelu et une sensibilité au gel conducteur chez certaines personnes. Les bénéfices
potentiels incluent une meilleure gestion du stress et un entraînement à la concentration.`,
  },
  {
    icon: Users,
    title: '7. Participation volontaire',
    body: `Votre participation est entièrement volontaire. Vous pouvez vous retirer de l'étude à tout
moment, sans justification et sans aucune conséquence. Le retrait de votre consentement entraînera
la suppression immédiate de toutes les données vous concernant.`,
  },
]

// ─── Composant principal ───────────────────────────────────────────────────────

export default function ConsentPage() {
  const navigate = useNavigate()
  const user     = useAuthStore((s) => s.user)

  const [checked,   setChecked]   = useState(false)
  const [loading,   setLoading]   = useState(false)
  const [error,     setError]     = useState(null)

  // Rediriger admin/thérapeute et patients ayant déjà consenti
  useEffect(() => {
    if (!user) return
    const role = user.role
    if (role === 'admin' || role === 'therapist' || user.consent_accepted) {
      navigate('/dashboard', { replace: true })
    }
  }, [user, navigate])

  const handleConfirm = async () => {
    if (!checked) return
    setLoading(true)
    setError(null)
    try {
      await API.post('/consent/accept', { accepted: true })
      // Mettre à jour le store localement ET re-fetcher le profil depuis le serveur
      // pour garantir que consent_accepted est bien à true avant la navigation,
      // évitant une boucle ConsentGuard → /consent → /dashboard.
      useAuthStore.setState((s) => ({
        user: s.user ? { ...s.user, consent_accepted: true } : s.user,
      }))
      await useAuthStore.getState().fetchUser()
      navigate('/dashboard', { replace: true })
    } catch (err) {
      const msg = err?.response?.data?.detail || 'Erreur lors de l\'enregistrement du consentement.'
      setError(msg)
    } finally {
      setLoading(false)
    }
  }

  const handleDownload = async () => {
    try {
      const res = await API.get('/consent/pdf', { responseType: 'blob' })
      const url  = URL.createObjectURL(res.data)
      const link = document.createElement('a')
      link.href     = url
      link.download = 'NeuroCap_Consentement.pdf'
      link.click()
      URL.revokeObjectURL(url)
    } catch {
      // Silencieux — le PDF sera de toute façon envoyé par email à la confirmation
    }
  }

  const firstName = user?.first_name || ''

  return (
    <div className="min-h-screen bg-nc-bg text-nc-text font-sans">

      {/* ── En-tête ── */}
      <div className="bg-gradient-to-r from-[#00b4d8] to-[#0077b6] py-8 px-6 text-center">
        <div className="text-3xl font-extrabold tracking-tight text-white">NeuroCap</div>
        <div className="text-sm text-white/70 mt-1">Easy Medical Device</div>
        <div className="mt-4 text-lg font-semibold text-white">
          {firstName ? `Bienvenue, ${firstName} !` : 'Avant de commencer'}
        </div>
        <div className="text-white/80 text-sm mt-1">
          Veuillez lire et accepter le formulaire de consentement éclairé pour accéder à votre espace NeuroCap.
        </div>
      </div>

      <div className="max-w-3xl mx-auto px-4 py-10 space-y-10">

        {/* ── Formulaire de consentement ── */}
        <section>
          <div className="flex items-center gap-3 mb-6">
            <Shield className="text-nc-accent" size={22} />
            <h2 className="text-xl font-bold text-nc-text">Consentement Éclairé</h2>
          </div>

          {/* Zone scrollable */}
          <div className="bg-nc-surface border border-nc-border rounded-2xl overflow-hidden">
            <div
              className="overflow-y-auto p-6 space-y-6"
              style={{ maxHeight: '480px' }}
            >
              {SECTIONS.map(({ icon: Icon, title, body, items }) => (
                <div key={title}>
                  <div className="flex items-center gap-2 mb-2">
                    <Icon size={15} className="text-nc-accent flex-shrink-0" />
                    <h3 className="text-sm font-bold text-nc-accent">{title}</h3>
                  </div>
                  {body && (
                    <p className="text-nc-muted text-sm leading-relaxed whitespace-pre-line">
                      {body}
                    </p>
                  )}
                  {items && (
                    <ul className="space-y-2 mt-1">
                      {items.map((item, i) => (
                        <li key={i} className="flex gap-2 text-sm text-nc-muted leading-relaxed">
                          <span className="text-nc-accent mt-0.5">•</span>
                          <span dangerouslySetInnerHTML={{ __html: item }} />
                        </li>
                      ))}
                    </ul>
                  )}
                </div>
              ))}

              {/* Clause de consentement final */}
              <div className="border-t border-nc-border pt-5">
                <div className="flex items-center gap-2 mb-2">
                  <Eye size={15} className="text-[#a78bfa] flex-shrink-0" />
                  <h3 className="text-sm font-bold text-[#a78bfa]">8. Déclaration de consentement</h3>
                </div>
                <p className="text-nc-muted text-sm leading-relaxed">
                  Je déclare avoir pris connaissance des informations ci-dessus concernant l'étude
                  NeuroCap. J'ai eu la possibilité de poser toutes mes questions et j'ai reçu des
                  réponses satisfaisantes. Je consens librement et volontairement à participer à
                  cette étude dans les conditions décrites.
                </p>
              </div>
            </div>
          </div>

          {/* Checkbox */}
          <label className="flex items-start gap-3 mt-5 cursor-pointer group">
            <div
              onClick={() => setChecked((v) => !v)}
              className={`w-5 h-5 mt-0.5 rounded border-2 flex items-center justify-center flex-shrink-0 transition-all
                ${checked
                  ? 'bg-nc-accent border-nc-accent'
                  : 'border-nc-border group-hover:border-nc-accent'}`}
            >
              {checked && <CheckCircle size={13} className="text-white" strokeWidth={3} />}
            </div>
            <span
              className="text-sm text-nc-text/80 select-none"
              onClick={() => setChecked((v) => !v)}
            >
              J'ai lu et compris les conditions ci-dessus. Je consens librement à participer
              au programme NeuroCap.
            </span>
          </label>

          {/* Erreur */}
          {error && (
            <div className="flex items-center gap-2 mt-4 bg-nc-danger/10 border border-nc-danger/30
                            text-nc-danger rounded-xl px-4 py-3 text-sm">
              <AlertCircle size={16} className="flex-shrink-0" />
              {error}
            </div>
          )}

          {/* Boutons */}
          <div className="flex flex-col sm:flex-row gap-3 mt-6">
            <button
              onClick={handleDownload}
              className="flex items-center justify-center gap-2 px-5 py-3 rounded-xl
                         border border-nc-border text-nc-muted hover:text-nc-text
                         hover:border-nc-accent transition-all text-sm font-medium"
            >
              <Download size={16} />
              Télécharger le PDF
            </button>

            <button
              onClick={handleConfirm}
              disabled={!checked || loading}
              className={`flex-1 flex items-center justify-center gap-2 px-6 py-3 rounded-xl
                          font-semibold text-sm transition-all
                          ${checked && !loading
                            ? 'bg-gradient-to-r from-[#00b4d8] to-[#0077b6] text-white hover:opacity-90'
                            : 'bg-nc-surface2 text-nc-muted cursor-not-allowed'}`}
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  Enregistrement…
                </>
              ) : (
                <>
                  Confirmer mon consentement
                  <ChevronRight size={16} />
                </>
              )}
            </button>
          </div>

          <p className="text-nc-muted/60 text-xs mt-3 text-center">
            Un email de confirmation avec le document PDF vous sera envoyé automatiquement.
          </p>
        </section>

      </div>
    </div>
  )
}
