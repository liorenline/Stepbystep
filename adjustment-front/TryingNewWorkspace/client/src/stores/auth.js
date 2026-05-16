import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi, userApi } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const user = ref(null)
  const loading = ref(false)
  const error = ref(null)
  const pendingUserId = ref(null)
  const needsEmailVerification = ref(false)
  const needs2fa = ref(false)
  const sessionChecked = ref(false)

  const isAuthenticated = computed(() => !!user.value)
  const username = computed(() => user.value?.username ?? '')
  const is2faEnabled = computed(() => !!user.value?.two_fa_enabled)

  async function fetchMe() {
    if (sessionChecked.value) return
    try {
      const { data } = await userApi.getMe()
      user.value = data.data
    } catch (_) {
      user.value = null
    } finally {
      sessionChecked.value = true
    }
  }

  async function login(email, password) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.login({ email, password })
      const payload = data.data
      if (payload?.requires_2fa) {
        needs2fa.value = true
        pendingUserId.value = payload.user_id
        return '2fa'
      }
      user.value = payload
      sessionChecked.value = true
      return 'ok'
    } catch (e) {
      error.value = e.response?.data?.error ?? e.response?.data?.message ?? 'Login failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function register(username, email, password, confirmPassword) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.register({ username, email, password, confirm_password: confirmPassword })
      pendingUserId.value = data.data?.user_id
      needsEmailVerification.value = true
      return 'verify'
    } catch (e) {
      error.value = e.response?.data?.error ?? e.response?.data?.message ?? 'Registration failed'
      return false
    } finally {
      loading.value = false
    }
  }

  async function verifyEmail(code) {
    loading.value = true
    error.value = null
    try {
      await authApi.verifyEmail(pendingUserId.value, code)
      needsEmailVerification.value = false
      pendingUserId.value = null
      return true
    } catch (e) {
      error.value = e.response?.data?.error ?? 'Invalid code'
      return false
    } finally {
      loading.value = false
    }
  }

  async function verify2fa(code) {
    loading.value = true
    error.value = null
    try {
      const { data } = await authApi.verify2fa(pendingUserId.value, code)
      user.value = data.data ?? data.user ?? data
      needs2fa.value = false
      pendingUserId.value = null
      sessionChecked.value = true
      return true
    } catch (e) {
      error.value = e.response?.data?.error ?? 'Invalid 2FA code'
      return false
    } finally {
      loading.value = false
    }
  }

  async function logout() {
    user.value = null
    sessionChecked.value = true
    needs2fa.value = false
    needsEmailVerification.value = false
    pendingUserId.value = null
  }

  return {
    user, loading, error,
    pendingUserId, needsEmailVerification, needs2fa,
    isAuthenticated, username, sessionChecked, is2faEnabled,
    fetchMe, login, register, verifyEmail, verify2fa, logout
  }
})