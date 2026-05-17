import { useState, useRef, useEffect, useCallback } from 'react'
import { useTranslation } from 'react-i18next'
import { assistant as assistantApi, profile as profileApi, sessions as sessionsApi } from '../utils/api'
import {
  MessageSquareText, Send, Sparkles, User, Bot, RefreshCw,
  ThumbsUp, ThumbsDown, Download, AlertCircle,
} from 'lucide-react'

let _msgId = 0
const mkMsg = (role, text, extra = {}) => ({ id: ++_msgId, role, text, feedback: null, ...extra })

// ── Message bubble ────────────────────────────────────────────────────────────
function Message({ msg, onFeedback }) {
  const isUser = msg.role === 'user'
  return (
    <div className={`flex gap-3 animate-fade-in ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 mt-0.5
                       ${isUser ? 'bg-nc-accent/20 text-nc-accent' : 'text-white'}`}
           style={!isUser ? { background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' } : {}}>
        {isUser ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
      </div>

      <div className={`flex flex-col gap-1 ${isUser ? 'items-end' : 'items-start'} max-w-[75%]`}>
        <div className={`px-4 py-3 rounded-2xl text-sm leading-relaxed
                         ${isUser
                           ? 'bg-nc-accent text-white rounded-tr-sm'
                           : 'card rounded-tl-sm text-nc-text'}`}>
          {msg.text}
        </div>

        {/* Thumbs feedback — assistant only */}
        {!isUser && onFeedback && (
          <div className="flex items-center gap-1 px-1">
            <button
              onClick={() => onFeedback(msg.id, 'up')}
              className={`p-1 rounded transition-colors
                          ${msg.feedback === 'up'
                            ? 'text-nc-success'
                            : 'text-nc-muted hover:text-nc-success'}`}
              title="Réponse utile"
            >
              <ThumbsUp className="w-3.5 h-3.5" />
            </button>
            <button
              onClick={() => onFeedback(msg.id, 'down')}
              className={`p-1 rounded transition-colors
                          ${msg.feedback === 'down'
                            ? 'text-nc-danger'
                            : 'text-nc-muted hover:text-nc-danger'}`}
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

// ── Proactive suggestion banner ───────────────────────────────────────────────
function ProactiveBubble({ text, onAsk, onDismiss }) {
  return (
    <div className="flex items-start gap-3 p-3 rounded-xl border border-nc-warning/30
                    bg-nc-warning/5 animate-fade-in shrink-0">
      <AlertCircle className="w-4 h-4 text-nc-warning shrink-0 mt-0.5" />
      <p className="flex-1 text-sm text-nc-text">{text}</p>
      <div className="flex items-center gap-2 shrink-0">
        <button onClick={onAsk}    className="text-xs text-nc-accent underline underline-offset-2">Demander</button>
        <button onClick={onDismiss} className="text-xs text-nc-muted hover:text-nc-text">✕</button>
      </div>
    </div>
  )
}

// ── Main page ─────────────────────────────────────────────────────────────────
export default function Assistant() {
  const { t } = useTranslation()
  const [messages, setMessages]   = useState([])
  const [input, setInput]         = useState('')
  const [loading, setLoading]     = useState(false)
  const [eegCtx, setEegCtx]       = useState(null)
  const [proactive, setProactive] = useState(null)
  const bottomRef   = useRef()
  const textareaRef = useRef()

  /* Load EEG context + set proactive suggestion */
  useEffect(() => {
    setMessages([mkMsg('assistant', t('assistant.welcome'))])

    Promise.all([
      profileApi.get().catch(() => null),
      sessionsApi.list().catch(() => []),
    ]).then(([prof, sess]) => {
      const ctx = {}

      if (prof) {
        if (prof.profile_type) ctx.profile_type   = prof.profile_type
        if (prof.iapf != null) ctx.iapf           = prof.iapf
        if (prof.baseline_tbr != null) ctx.baseline_tbr = prof.baseline_tbr
        if (prof.palier)       ctx.palier          = prof.palier
      }

      if (Array.isArray(sess) && sess.length > 0) {
        const scores = sess.slice(0, 5).map(s => s.score).filter(Boolean)
        if (scores.length) ctx.avg_score_last5 = (scores.reduce((a, b) => a + b, 0) / scores.length).toFixed(1)

        const lastTbr      = sess[0]?.avg_tbr
        const baselineTbr  = prof?.baseline_tbr
        if (lastTbr && baselineTbr && lastTbr > baselineTbr * 1.3) {
          setProactive(
            `Votre TBR lors de la dernière session (${lastTbr.toFixed(2)}) est élevé par rapport à votre baseline (${baselineTbr.toFixed(2)}). Voulez-vous des conseils pour réduire le stress ?`
          )
        }
      }

      if (Object.keys(ctx).length) setEegCtx(ctx)
    })
  }, [t])

  /* Auto-scroll */
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const send = async (question = input.trim()) => {
    if (!question || loading) return
    const userMsg = mkMsg('user', question)
    setMessages((m) => [...m, userMsg])
    setInput('')
    setLoading(true)
    setProactive(null)
    try {
      const res    = await assistantApi.ask(question, null, eegCtx)
      const answer = res.response ?? res.answer ?? t('assistant.error')
      setMessages((m) => [...m, mkMsg('assistant', answer, { _question: question })])
    } catch {
      setMessages((m) => [...m, mkMsg('assistant', t('assistant.error'))])
    } finally {
      setLoading(false)
    }
  }

  const handleFeedback = useCallback((msgId, value) => {
    setMessages((m) => m.map((msg) => {
      if (msg.id !== msgId) return msg
      // Fire-and-forget feedback to backend
      assistantApi.feedback(msgId, value, msg._question, msg.text).catch(() => {})
      return { ...msg, feedback: value }
    }))
  }, [])

  const handleExport = () => {
    const lines = messages.map((m) => {
      const who = m.role === 'user' ? '**Vous**' : '**Assistant**'
      return `${who}: ${m.text}`
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

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); send() }
  }

  const suggestedQuestions = [
    t('assistant.suggested.q1'),
    t('assistant.suggested.q2'),
    t('assistant.suggested.q3'),
    t('assistant.suggested.q4'),
  ]

  const hasConversation = messages.length > 1

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 py-8 h-[calc(100vh-120px)] flex flex-col gap-4">

      {/* Header */}
      <div className="flex items-center justify-between animate-slide-up shrink-0">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-2xl flex items-center justify-center text-white"
               style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h1 className="text-2xl font-bold text-nc-text">{t('assistant.title')}</h1>
            <p className="text-sm text-nc-muted">{t('assistant.subtitle')}</p>
          </div>
        </div>
        {hasConversation && (
          <button onClick={handleExport} className="btn-ghost flex items-center gap-2 text-sm">
            <Download className="w-4 h-4" />
            Exporter
          </button>
        )}
      </div>

      {/* Proactive suggestion */}
      {proactive && (
        <ProactiveBubble
          text={proactive}
          onAsk={() => send(proactive)}
          onDismiss={() => setProactive(null)}
        />
      )}

      {/* Suggested chips */}
      {!hasConversation && (
        <div className="animate-fade-in shrink-0">
          <p className="section-title mb-3">
            <MessageSquareText className="w-3.5 h-3.5" />
            {t('assistant.suggested.title')}
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestions.map((q) => (
              <SuggestedChip key={q} label={q} onClick={() => send(q)} />
            ))}
          </div>
        </div>
      )}

      {/* Messages area */}
      <div className="card flex-1 min-h-0 overflow-y-auto p-4 sm:p-6 space-y-4">
        {messages.map((m) => (
          <Message
            key={m.id}
            msg={m}
            onFeedback={m.role === 'assistant' ? handleFeedback : null}
          />
        ))}

        {loading && (
          <div className="flex gap-3 animate-fade-in">
            <div className="w-8 h-8 rounded-full flex items-center justify-center shrink-0 text-white"
                 style={{ background: 'linear-gradient(135deg, rgb(var(--nc-accent)), rgb(var(--nc-accent)/0.6))' }}>
              <Bot className="w-4 h-4" />
            </div>
            <div className="card px-4 py-3 rounded-2xl rounded-tl-sm flex items-center gap-2">
              <RefreshCw className="w-4 h-4 text-nc-accent animate-spin" />
              <span className="text-sm text-nc-muted">{t('assistant.thinking')}</span>
            </div>
          </div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input bar */}
      <div className="card p-2 flex gap-2 items-end shrink-0 animate-fade-in">
        <textarea
          ref={textareaRef}
          rows={1}
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={t('assistant.placeholder')}
          className="flex-1 bg-transparent px-3 py-2 text-sm text-nc-text placeholder:text-nc-muted resize-none outline-none max-h-32"
          style={{ fieldSizing: 'content' }}
        />
        <button
          onClick={() => send()}
          disabled={!input.trim() || loading}
          className="btn-primary rounded-xl px-3 py-2.5 shrink-0"
        >
          <Send className="w-4 h-4" />
        </button>
      </div>
    </div>
  )
}
