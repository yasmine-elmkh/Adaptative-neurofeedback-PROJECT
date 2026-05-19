import { useState, useCallback, useRef } from 'react'

export function useToast() {
  const [toastState, setToastState] = useState({ message:'', show:false })
  const timerRef = useRef(null)

  const toast = useCallback((message) => {
    if (timerRef.current) clearTimeout(timerRef.current)
    setToastState({ message, show:true })
    timerRef.current = setTimeout(() => setToastState(s => ({ ...s, show:false })), 3000)
  }, [])

  return { toast, toastState }
}

export default function Toast({ message, show }) {
  return (
    <div style={{
      position:'fixed', bottom:24, right:24, zIndex:9999,
      background:'#0e1420', border:'1px solid rgba(0,229,176,.25)',
      borderRadius:10, padding:'10px 18px',
      fontFamily:"'DM Sans',sans-serif", fontSize:13, color:'#c9d8e8',
      boxShadow:'0 4px 24px rgba(0,0,0,.4)',
      opacity: show ? 1 : 0,
      transform: show ? 'translateY(0)' : 'translateY(8px)',
      transition:'opacity .25s ease, transform .25s ease',
      pointerEvents: 'none',
    }}>
      {message}
    </div>
  )
}
