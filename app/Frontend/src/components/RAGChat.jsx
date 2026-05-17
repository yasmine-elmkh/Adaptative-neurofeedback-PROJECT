/**
 * NeuroCap – RAG Chat Component
 * Reusable chat interface for the AI assistant.
 */
import React, { useState, useRef, useEffect } from 'react'
import { assistant } from '../utils/api'
import { Send, Bot, User, LoaderCircle } from 'lucide-react'

export default function RAGChat({ sessionId = null, compact = false }) {
  const [messages, setMessages] = useState([
    { role: 'assistant', text: 'Bonjour ! Je suis votre assistant cognitif NeuroCap. Posez-moi vos questions sur vos séances, vos scores EEG ou des conseils de régulation.' }
  ])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const endRef = useRef(null)

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return
    const question = input.trim()
    setInput('')
    setMessages((prev) => [...prev, { role: 'user', text: question }])
    setLoading(true)

    try {
      const res = await assistant.ask(question, sessionId)
      setMessages((prev) => [...prev, { role: 'assistant', text: res.answer, sources: res.sources }])
    } catch (err) {
      setMessages((prev) => [...prev, { role: 'assistant', text: 'Désolé, une erreur est survenue. Réessayez.' }])
    } finally {
      setLoading(false)
    }
  }

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend() }
  }

  return (
    <div className={`flex flex-col ${compact ? 'h-80' : 'h-full'}`}>
      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, i) => (
          <div key={i} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-full flex items-center justify-center flex-shrink-0 ${
              msg.role === 'user' ? 'bg-neuro-accent/20' : 'bg-neuro-surface'
            }`}>
              {msg.role === 'user'
                ? <User className="w-4 h-4 text-neuro-accent" />
                : <Bot className="w-4 h-4 text-neuro-success" />
              }
            </div>
            <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed ${
              msg.role === 'user'
                ? 'bg-neuro-accent/10 text-neuro-text rounded-tr-sm'
                : 'bg-neuro-surface text-neuro-text rounded-tl-sm'
            }`}>
              {msg.text}
              {msg.sources?.length > 0 && (
                <div className="mt-2 pt-2 border-t border-neuro-border/50">
                  <span className="text-[10px] text-neuro-muted uppercase tracking-wider">
                    Sources : {msg.sources.join(', ')}
                  </span>
                </div>
              )}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-neuro-surface flex items-center justify-center">
              <LoaderCircle className="w-4 h-4 text-neuro-accent animate-spin" />
            </div>
            <div className="px-4 py-3 rounded-2xl bg-neuro-surface rounded-tl-sm">
              <span className="text-sm text-neuro-muted">Réflexion en cours…</span>
            </div>
          </div>
        )}
        <div ref={endRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-neuro-border">
        <div className="flex gap-3">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Posez votre question…"
            className="input-field flex-1"
            disabled={loading}
          />
          <button onClick={handleSend} disabled={loading || !input.trim()} className="btn-primary px-4">
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  )
}