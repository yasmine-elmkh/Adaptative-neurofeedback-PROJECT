import { useState } from 'react'
import { admin as adminApi } from '../utils/api'
import { X, Eye, EyeOff, AlertTriangle, Loader2 } from 'lucide-react'

const ROLES = ['patient', 'therapist', 'admin']

const ROLE_BADGE = {
  admin:     'bg-purple-500/15 text-purple-400',
  therapist: 'bg-green-500/15  text-green-400',
  patient:   'bg-nc-accent/15  text-nc-accent',
}

export default function UserFormModal({ user = null, therapists = [], onClose, onSave }) {
  const isEdit = !!user

  const [form, setForm] = useState({
    email:        user?.email        ?? '',
    password:     '',
    first_name:   user?.first_name   ?? '',
    last_name:    user?.last_name    ?? '',
    role:         user?.role         ?? 'patient',
    therapist_id: user?.therapist_id ?? '',
    is_active:    user?.is_active    ?? true,
  })
  const [showPw,  setShowPw]  = useState(false)
  const [loading, setLoading] = useState(false)
  const [error,   setError]   = useState('')

  const set = (k, v) => setForm(f => ({ ...f, [k]: v }))

  const submit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      let saved
      if (isEdit) {
        saved = await adminApi.updateUser(user.id, {
          role:         form.role,
          is_active:    form.is_active,
          therapist_id: form.therapist_id || null,
        })
      } else {
        saved = await adminApi.createUser({
          email:        form.email,
          password:     form.password,
          first_name:   form.first_name || undefined,
          last_name:    form.last_name  || undefined,
          role:         form.role,
          therapist_id: form.therapist_id || null,
        })
      }
      onSave(saved)
      onClose()
    } catch (err) {
      const detail = err?.response?.data?.detail
      setError(Array.isArray(detail) ? detail[0]?.msg : (detail || 'Erreur lors de l\'opération'))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={onClose}
    >
      <div
        className="bg-nc-surface border border-nc-border rounded-2xl shadow-glass-lg w-full max-w-md mx-4 p-6 animate-fade-in"
        onClick={e => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-center justify-between mb-5">
          <h3 className="text-lg font-bold text-nc-text">
            {isEdit ? 'Modifier l\'utilisateur' : 'Créer un utilisateur'}
          </h3>
          <button onClick={onClose} className="text-nc-muted hover:text-nc-text transition-colors">
            <X className="w-5 h-5" />
          </button>
        </div>

        {error && (
          <div className="flex items-start gap-2 px-3 py-2.5 rounded-xl bg-nc-danger/10 border border-nc-danger/20 text-nc-danger text-sm mb-4">
            <AlertTriangle className="w-4 h-4 shrink-0 mt-0.5" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={submit} className="space-y-4">
          {/* Name */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block text-xs font-medium text-nc-muted mb-1">Prénom</label>
              <input
                className="input w-full"
                placeholder="Alice"
                value={form.first_name}
                onChange={e => set('first_name', e.target.value)}
                disabled={isEdit}
              />
            </div>
            <div>
              <label className="block text-xs font-medium text-nc-muted mb-1">Nom</label>
              <input
                className="input w-full"
                placeholder="Dupont"
                value={form.last_name}
                onChange={e => set('last_name', e.target.value)}
                disabled={isEdit}
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-xs font-medium text-nc-muted mb-1">Email *</label>
            <input
              required
              type="email"
              className="input w-full"
              placeholder="alice@example.com"
              value={form.email}
              onChange={e => set('email', e.target.value)}
              disabled={isEdit}
            />
          </div>

          {/* Password — only for create */}
          {!isEdit && (
            <div>
              <label className="block text-xs font-medium text-nc-muted mb-1">Mot de passe *</label>
              <div className="relative">
                <input
                  required
                  type={showPw ? 'text' : 'password'}
                  className="input w-full pe-10"
                  placeholder="Minimum 6 caractères"
                  value={form.password}
                  onChange={e => set('password', e.target.value)}
                  minLength={6}
                />
                <button
                  type="button"
                  className="absolute end-3 top-1/2 -translate-y-1/2 text-nc-muted hover:text-nc-text"
                  onClick={() => setShowPw(s => !s)}
                >
                  {showPw ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          )}

          {/* Role */}
          <div>
            <label className="block text-xs font-medium text-nc-muted mb-1">Rôle</label>
            <div className="flex gap-2">
              {ROLES.map(r => (
                <button
                  key={r}
                  type="button"
                  onClick={() => set('role', r)}
                  className={`flex-1 py-2 rounded-xl text-xs font-semibold border transition-all
                              ${form.role === r
                                ? `${ROLE_BADGE[r]} border-current`
                                : 'text-nc-muted border-nc-border hover:border-nc-accent/40'}`}
                >
                  {r}
                </button>
              ))}
            </div>
          </div>

          {/* Active toggle — only for edit */}
          {isEdit && (
            <label className="flex items-center gap-3 cursor-pointer select-none">
              <div
                onClick={() => set('is_active', !form.is_active)}
                className={`relative w-10 h-5 rounded-full transition-colors ${form.is_active ? 'bg-nc-accent' : 'bg-nc-surface2 border border-nc-border'}`}
              >
                <span className={`absolute top-0.5 w-4 h-4 rounded-full bg-white shadow transition-transform ${form.is_active ? 'translate-x-5' : 'translate-x-0.5'}`} />
              </div>
              <span className="text-sm text-nc-text">Compte {form.is_active ? 'actif' : 'désactivé'}</span>
            </label>
          )}

          {/* Therapist assignment — only for patient role */}
          {form.role === 'patient' && (
            <div>
              <label className="block text-xs font-medium text-nc-muted mb-1">Thérapeute assigné (optionnel)</label>
              <select
                className="input w-full"
                value={form.therapist_id}
                onChange={e => set('therapist_id', e.target.value)}
              >
                <option value="">— Aucun —</option>
                {therapists.map(t => (
                  <option key={t.id} value={t.id}>
                    {t.first_name} {t.last_name} ({t.email})
                  </option>
                ))}
              </select>
            </div>
          )}

          {/* Actions */}
          <div className="flex gap-3 pt-2">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 py-2.5 rounded-xl text-sm text-nc-muted hover:bg-nc-surface2 border border-nc-border transition-colors"
            >
              Annuler
            </button>
            <button
              type="submit"
              disabled={loading}
              className="btn-primary flex-1 py-2.5 rounded-xl text-sm flex items-center justify-center gap-2 disabled:opacity-60"
            >
              {loading && <Loader2 className="w-4 h-4 animate-spin" />}
              {loading
                ? (isEdit ? 'Mise à jour…' : 'Création…')
                : (isEdit ? 'Enregistrer' : 'Créer')}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
