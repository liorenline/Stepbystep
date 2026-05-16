import api from './axios'

// ── AUTH ─────────────────────────────────────────────────────────────
export const authApi = {
  register: (data) => api.post('/register', data),
  verifyEmail: (userId, code) => api.post('/verify-email', { user_id: userId, code }),
  login: (data) => api.post('/login', data),
  verify2fa: (userId, code) => api.post('/verify-2fa', { user_id: userId, code }),
  logout: () => api.post('/logout'),
  resendVerification: (email) => api.post('/resend-verification', { email }),
}

// ── DECKS ─────────────────────────────────────────────────────────────
export const decksApi = {
  getAll: () => api.get('/decks'),
  getOne: (id) => api.get(`/decks/${id}`),
  create: (data) => api.post('/decks', data),
  update: (id, data) => api.put(`/decks/${id}`, data),
  remove: (id) => api.delete(`/decks/${id}`),
}

// ── CARDS ─────────────────────────────────────────────────────────────
export const cardsApi = {
  getAll: (deckId) => api.get(`/decks/${deckId}/cards`),
  create: (deckId, data) => api.post(`/decks/${deckId}/cards`, data),
  update: (deckId, cardId, data) => api.put(`/decks/${deckId}/cards/${cardId}`, data),
  remove: (deckId, cardId) => api.delete(`/decks/${deckId}/cards/${cardId}`),
}

// ── USER ─────────────────────────────────────────────────────────────
export const userApi = {
  /** GET /api/me */
  getMe: () => api.get('/me'),

  /** PUT /api/user/:id — оновити нікнейм (без підтвердження) */
  updateUsername: (userId, username) =>
    api.put(`/user/${userId}`, { username }),

  // ── EMAIL CHANGE (з підтвердженням кодом на нову пошту) ──
  /** POST /api/user/:id/email/request-change — надіслати код на нову пошту */
  requestEmailChange: (userId, newEmail) =>
    api.post(`/user/${userId}/email/request-change`, { new_email: newEmail }),

  /** POST /api/user/:id/email/confirm-change — підтвердити код і змінити пошту */
  confirmEmailChange: (userId, newEmail, code) =>
    api.post(`/user/${userId}/email/confirm-change`, { new_email: newEmail, code }),

  // ── PASSWORD CHANGE (з підтвердженням кодом на поточну пошту) ──
  /** POST /api/user/:id/send-change-password-code — надіслати код на поточну пошту */
  sendPasswordCode: (userId) =>
    api.post(`/user/${userId}/send-change-password-code`),

  /** POST /api/user/:id/change-password — підтвердити код і змінити пароль */
  changePassword: (userId, code, newPassword) =>
    api.post(`/user/${userId}/change-password`, { code, password: newPassword }),

  // ── 2FA ──
  send2faCode: (userId) => api.post(`/user/${userId}/2fa/send-code`),
  enable2fa: (userId, code) => api.post(`/user/${userId}/2fa/enable`, { code }),
  sendDisable2faCode: (userId) => api.post(`/user/${userId}/2fa/send-disable-code`),
  disable2fa: (userId, code) => api.post(`/user/${userId}/2fa/disable`, { code }),

  // ── DELETE ──
  deleteAccount: (userId) => api.delete(`/user/${userId}`),
}