import { useState, useRef, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { assistant as assistantApi, profile as profileApi, sessions as sessionsApi } from '../utils/api'
import {
  MessageSquareText, Send, Sparkles, User, Bot, RefreshCw,
  ThumbsUp, ThumbsDown, Download, AlertCircle, BarChart2,
  Brain, ChevronRight, Info,
} from 'lucide-react'

let _msgId = 0
const mkMsg = (role, text, extra = {}) => ({ id: ++_msgId, role, text, feedback: null, ...extra })

// ── Typing dots ───────────────────────────────────────────────────────────────
function TypingDots() {
  return (
    <div className="flex gap-1 items-center py-1">
      {[0, 1, 2].map(i => (
        <span
          key={i}
          className="w-2 h-2 rounded-full bg-nc-accent/70 animate-bounce"
          style={{ animationDelay: `${i * 0.15}s` }}
        />
      ))}
    </div>
  )
}

// ── Source chip ───────────────────────────────────────────────────────────────
function SourceChip({ label }) {
  return (
    <span className="inline-flex items-center gap-1 text-[10px] px-2 py-0.5 rounded-full
                     bg-nc-surface2 border border-nc-border text-nc-muted">
      <Info className="w-2.5 h-2.5 shrink-0" />
      {label}
    </span>
  )
}

// ── Message bubble ────────────────────────────────────────────────────────────
function Message({ msg, onFeedback }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div
        className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5
                    ${isUser ? 'bg-nc-accent/20 text-nc-accent' : 'text-white'}`}
        style={!isUser ? { background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' } : {}}
      >
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className={`flex flex-col gap-1.5 ${isUser ? 'items-end' : 'items-start'} max-w-[78%]`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed whitespace-pre-wrap
                         ${isUser
                           ? 'bg-nc-accent text-white rounded-tr-sm'
                           : 'card rounded-tl-sm text-nc-text'}`}>
          {msg.text}
        </div>

        {/* Sources */}
        {!isUser && msg.sources && msg.sources.length > 0 && (
          <div className="flex flex-wrap gap-1 px-1">
            {msg.sources.map(s => <SourceChip key={s} label={s} />)}
          </div>
        )}

        {/* Thumbs feedback — assistant only */}
        {!isUser && onFeedback && (
          <div className="flex items-center gap-1 px-1">
            <button
              onClick={() => onFeedback(msg.id, 'up')}
              className={`p-1 rounded transition-colors
                          ${msg.feedback === 'up' ? 'text-nc-success' : 'text-nc-muted hover:text-nc-success'}`}
              title="Réponse utile"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onFeedback(msg.id, 'down')}
              className={`p-1 rounded transition-colors
                          ${msg.feedback === 'down' ? 'text-nc-danger' : 'text-nc-muted hover:text-nc-danger'}`}
              title="Réponse non utile"
            >
              <ThumbsDown className="w-3.5 h-3.5" />
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

// ── Suggested chip ────────────────────────────────────────────────────────────
function SuggestedChip({ label, onClick }) {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 rounded-full bg-nc-surface2 border border-nc-border
                 text-sm text-nc-muted hover:text-nc-accent hover:border-nc-accent/40
                 transition-all text-start"
    >
      {label}
    </button>
  )
}

// ── Proactive banner ──────────────────────────────────────────────────────────
function ProactiveBubble({ text, onAsk, onDismiss }) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-xl border border-nc-warning/30
                    bg-nc-warning/5 animate-fade-in shrink-0">
      <AlertCircle className="w-4 h-4 text-nc-warning shrink-0 mt-0.5" />
      <p className="flex-1 text-sm text-nc-text">{text}</p>
      <div className="flex items-center gap-2 shrink-0">
        <button onClick={onAsk}     className="text-xs text-nc-accent underline underline-offset-2">Demander</button>
        <button onClick={onDismiss} className="text-xs text-nc-muted hover:text-nc-text">✕</button>
      </div>
    </div>
  )
}

// ── Context badge ─────────────────────────────────────────────────────────────
function ContextBadge({ info }) {
  if (!info) return null
  return (
    <div className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-nc-surface2
                    border border-nc-border text-[11px] text-nc-muted shrink-0">
      <Brain className="w-3 h-3 text-nc-accent shrink-0" />
      <span>{info}</span>
    </div>
  )
}

// ── Explain Results card ──────────────────────────────────────────────────────
function ExplainCard({ onExplain, loading }) {
  return (
    <div className="card p-4 border border-nc-accent/20 bg-nc-accent/4 shrink-0 animate-fade-in">
      <div className="flex items-center gap-3">
        <div className="w-9 h-9 rounded-xl bg-nc-accent/15 flex items-center justify-center shrink-0">
          <BarChart2 className="w-4.5 h-4.5 text-nc-accent" />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold text-nc-text">Explication de vos résultats</p>
          <p className="text-xs text-nc-muted">
            Obtenez une analyse complète de votre dashboard : TBR, concentration, stress, profil EEG…
          </p>
        </div>
        <button
          onClick={onExplain}
          disabled={loading}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-xl btn-primary text-xs
                     font-semibold shrink-0 disabled:opacity-60"
        >
          {loading ? <RefreshCw className="w-3.5 h-3.5 animate-spin" /> : <ChevronRight className="w-3.5 h-3.5" />}
          {loading ? 'Analyse…' : 'Analyser'}
        </button>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function Assistant() {
  const { t } = useTranslation()
  const [messages, setMessages]       = useState([])
  const [input, setInput]             = useState('')
  const [loading, setLoading]         = useState(false)
  const [explainLoading, setExplain]  = useState(false)
  const [eegCtx, setEegCtx]           = useState(null)
  const [proactive, setProactive]     = useState(null)
  const [contextInfo, setContextInfo] = useState(null)
  const [dynamicChips, setChips]      = useState([])
  const bottomRef   = useRef()
  const textareaRef = useRef()

  /* ── Load patient context on mount ── */
  useEffect(() => {
    setMessages([mkMsg('assistant', t('assistant.welcome'))])

    Promise.all([
      profileApi.get().catch(() => null),
      sessionsApi.list().catch(() => []),
    ]).then(([prof, sess]) => {
      const ctx = {}

      if (prof) {
        if (prof.profile_type) ctx.profile_type   = prof.profile_type
        if (prof.iapf   != null) ctx.iapf          = prof.iapf
        if (prof.baseline_tbr != null) ctx.baseline_tbr = prof.baseline_tbr
        if (prof.palier)        ctx.palier          = prof.palier
      }

      // Build context info badge
      const infoParts = []
      if (prof?.profile_type) infoParts.push(`Profil ${prof.profile_type}`)
      if (Array.isArray(sess) && sess.length > 0) {
        infoParts.push(`${sess.length} séances`)
        const scores = sess.slice(0, 5).map(s => s.score).filter(Boolean)
        if (scores.length) {
          ctx.avg_score_last5 = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)
          infoParts.push(`Score moy. ${ctx.avg_score_last5} %`)
        }
      }
      if (infoParts.length) {
        setContextInfo(`Contexte : ${infoParts.join(' · ')}`)
      }

      // Proactive TBR alert
      if (Array.isArray(sess) && sess.length > 0) {
        const lastTbr     = sess[0]?.avg_tbr
        const baselineTbr = prof?.baseline_tbr
        if (lastTbr && baselineTbr && lastTbr > baselineTbr * 1.3) {
          setProactive(
            `Votre TBR lors de la dernière séance (${lastTbr.toFixed(2)}) est élevé vs. votre baseline (${baselineTbr.toFixed(2)}). Voulez-vous des conseils pour réduire le stress ?`
          )
        }
      }

      // Dynamic suggested chips based on patient state
      const chips = []
      if (prof?.profile_type) {
        chips.push(`Qu'est-ce que le profil ${prof.profile_type} signifie pour moi ?`)
      }
      if (prof?.palier) {
        chips.push(`Comment passer au palier suivant ?`)
      }
      if (prof?.baseline_tbr != null) {
        chips.push(`Comment interpréter mon TBR de ${prof.baseline_tbr?.toFixed(2)} ?`)
      }
      chips.push('Quels exercices faire entre les séances ?')
      chips.push('Comment améliorer ma concentration ?')
      setChips(chips.slice(0, 4))

      if (Object.keys(ctx).length) setEegCtx(ctx)
    })
  }, [t])

  /* ── Auto-scroll ── */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  /* ── Send a typed question ── */
  const send = async (question = input.trim()) => {
    if (!question || loading || explainLoading) return
    setMessages(m => [...m, mkMsg('user', question)])
    setInput('')
    setLoading(true)
    setProactive(null)
    try {
      const res    = await assistantApi.ask(question, null, eegCtx)
      const answer = res.answer ?? res.response ?? t('assistant.error')
      setMessages(m => [...m, mkMsg('assistant', answer, {
        sources:   res.sources || [],
        _question: question,
      })])
    } catch {
      setMessages(m => [...m, mkMsg('assistant', t('assistant.error'))])
    } finally {
      setLoading(false)
    }
  }

  /* ── Explain full dashboard ── */
  const handleExplain = async () => {
    if (loading || explainLoading) return
    const question = '📊 Explique-moi tous mes résultats du dashboard NeuroCap'
    setMessages(m => [...m, mkMsg('user', question)])
    setExplain(true)
    setProactive(null)
    try {
      const res    = await assistantApi.explain()
      const answer = res.answer ?? res.response ?? t('assistant.error')
      setMessages(m => [...m, mkMsg('assistant', answer, {
        sources:   res.sources || [],
        _question: question,
      })])
    } catch {
      setMessages(m => [...m, mkMsg('assistant', t('assistant.error'))])
    } finally {
      setExplain(false)
    }
  }

  /* ── Thumbs feedback ── */
  const handleFeedback = useCallback((msgId, value) => {
    setMessages(m => m.map(msg => {
      if (msg.id !== msgId) return msg
      assistantApi.feedback(msgId, value, msg._question, msg.text).catch(() => {})
      return { ...msg, feedback: value }
    }))
  }, [])

  /* ── Export conversation ── */
  const handleExport = () => {
    const lines = messages.map(m => {
      const who = m.role === 'user' ? '**Vous**' : '**NeuroCoach**'
      const src = m.sources?.length ? `\n_Sources : ${m.sources.join(', ')}_` : ''
      return `${who}: ${m.text}${src}`
    }).join('\n\n')
    const md   = `# Conversation NeuroCap\n_${new Date().toLocaleString()}_\n\n${lines}`
    const blob = new Blob([md], { type: 'text/markdown' })
    const url  = URL.createObjectURL(blob)
    const a    = document.createElement('a')
    a.href     = url
    a.download = `neurocap_chat_${Date.now()}.md`
    a.click()
    URL.revokeObjectURL(url)
  }

  const handleKeyDown = e => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  const hasConversation = messages.length > 1
  const isLoading       = loading || explainLoading

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 h-[calc(100vh-120px)] flex flex-col gap-4">

      {/* ── Header ── */}
      <div className="flex items-center justify-between animate-slide-up shrink-0">
        <div className="flex items-center gap-3">
          <div
            className="w-10 h-10 rounded-2xl flex items-center justify-center text-white"
            style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}
          >
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-nc-text">{t('assistant.title')}</h1>
            <p className="text-sm text-nc-muted">{t('assistant.subtitle')}</p>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <ContextBadge info={contextInfo} />
          {hasConversation && (
            <button onClick={handleExport} className="btn-ghost flex items-center gap-2 text-sm">
              <Download className="w-4 h-4" />
              Exporter
            </button>
          )}
        </div>
      </div>

      {/* ── Proactive alert ── */}
      {proactive && (
        <ProactiveBubble
          text={proactive}
          onAsk={() => send(proactive)}
          onDismiss={() => setProactive(null)}
        />
      )}

      {/* ── Explain results card (always visible until used) ── */}
      {!hasConversation && (
        <ExplainCard onExplain={handleExplain} loading={explainLoading} />
      )}

      {/* ── Suggested chips (before conversation starts) ── */}
      {!hasConversation && (
        <div className="animate-fade-in shrink-0">
          <p className="section-title mb-3">
            <MessageSquareText className="w-3.5 h-3.5" />
            {t('assistant.suggested.title')}
          </p>
          <div className="flex flex-wrap gap-2">
            {(dynamicChips.length > 0 ? dynamicChips : [
              t('assistant.suggested.q1'),
              t('assistant.suggested.q2'),
              t('assistant.suggested.q3'),
              t('assistant.suggested.q4'),
            ]).map(q => (
              <SuggestedChip key={q} label={q} onClick={() => send(q)} />
            ))}
          </div>
        </div>
      )}

      {/* ── Messages ── */}
      <div className="card flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map(m => (
          <Message
            key={m.id}
            msg={m}
            onFeedback={m.role === 'assistant' ? handleFeedback : null}
          />
        ))}

        {isLoading && (
          <div className="flex gap-3 animate-fade-in">
            <div
              className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white"
              style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}
            >
              <Bot className="w-4 h-4" />
            </div>
            <div className="card px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-3">
              <TypingDots />
              <span className="text-sm text-nc-muted">
                {explainLoading ? 'Analyse de vos données en cours…' : t('assistant.thinking')}
              </span>
            </div>
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* ── Input bar ── */}
      <div className="card p-2 flex gap-2 items-end shrink-0 animate-fade-in">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={e => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('assistant.placeholder')}
          className="flex-1 bg-transparent px-3 py-2 text-sm text-nc-text placeholder:text-nc-muted
                     resize-none outline-none max-h-32"
          style={{ fieldSizing: 'content' }}
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || isLoading}
          className="btn-primary rounded-xl px-3 py-2.5 shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>

    </div>
  )
}
