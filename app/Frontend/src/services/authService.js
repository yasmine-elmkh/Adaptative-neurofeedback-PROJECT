const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001';

export const authService = {
  // Inscription
  register: async (email, password, firstName, lastName) => {
    // Construire un nom d'utilisateur (username) à partir du prénom et nom
    const username = `${firstName.toLowerCase()}.${lastName.toLowerCase()}`;

    const response = await fetch(`${API_BASE_URL}/api/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        email,
        password,
        username   // ← on envoie username au lieu de first_name/last_name
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Erreur d'inscription");
    }
    return response.json();
  },

  // Connexion
  login: async (email, password) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/login?email=${email}&password=${password}`, {
      method: 'POST'
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Échec de connexion");
    }
    return response.json();
  },

  // Récupérer l'utilisateur courant
  getCurrentUser: async (token) => {
    const response = await fetch(`${API_BASE_URL}/api/auth/me`, {
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (!response.ok) throw new Error('Impossible de récupérer l’utilisateur');
    return response.json();
  }
};