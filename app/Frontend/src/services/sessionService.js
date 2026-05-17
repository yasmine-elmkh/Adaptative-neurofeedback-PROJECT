/**
 * Service API pour les sessions de neurofeedback
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const sessionService = {
  // POST /sessions/ - Créer une nouvelle session
  createSession: async (token, objective) => {
    const response = await fetch(`${API_BASE_URL}/sessions/`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({ objective })
    });
    if (!response.ok) throw new Error('Failed to create session');
    return response.json();
  },

  // WebSocket pour streaming EEG
  connectWebSocket: (sessionId, token) => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/api/sessions/ws/${sessionId}?token=${token}`;
    return new WebSocket(wsUrl);
  }
};