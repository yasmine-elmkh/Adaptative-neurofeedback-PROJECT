import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from './useWebSocket'

/**
 * useEEGWebSocket - Spécialisé pour le flux EEG /ws/eeg
 * Utilise useWebSocket pour la connexion et ajoute la reconnexion automatique.
 *
 * @param {string} url - ws://host/ws/eeg
 * @param {Object} options - { autoReconnect, reconnectInterval }
 */
export function useEEGWebSocket(url, { autoReconnect = true, reconnectInterval = 3000 } = {}) {
  const [epoch, setEpoch] = useState(null)
  const [eegBands, setEegBands] = useState(null)
  const [isConnected, setIsConnected] = useState(false)
  const reconnectTimerRef = useRef(null)

  const handleOpen = useCallback(() => {
    setIsConnected(true)
    if (reconnectTimerRef.current) clearInterval(reconnectTimerRef.current)
  }, [])

  const handleClose = useCallback(() => {
    setIsConnected(false)
    if (autoReconnect && !reconnectTimerRef.current) {
      reconnectTimerRef.current = setInterval(() => {
        // reconnect déclenché par le hook useWebSocket via connect()
        connect()
      }, reconnectInterval)
    }
  }, [autoReconnect, reconnectInterval])

  const handleMessage = useCallback((data) => {
    if (data.type === 'epoch') {
      setEpoch(data)
    } else if (data.type === 'eeg' && data.bands) {
      setEegBands(data.bands)
    }
  }, [])

  const { connect, disconnect, send } = useWebSocket(url, {
    onOpen: handleOpen,
    onClose: handleClose,
    onMessage: handleMessage,
  })

  // Nettoyer le timer de reconnexion au démontage
  useEffect(() => {
    return () => {
      if (reconnectTimerRef.current) clearInterval(reconnectTimerRef.current)
    }
  }, [])

  // Fonction pour envoyer des commandes (baseline, enregistrement…)
  const sendCommand = useCallback((command, value) => {
    send({ command, ...(value && { value }) })
  }, [send])

  return { epoch, eegBands, isConnected, sendCommand, connect, disconnect }
}