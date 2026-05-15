<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()

const user = ref({
  firstName: '',
  email: '',
})

const loading = ref(true)
const error = ref('')

// Modal state
const modal = ref({ type: null }) // 'name' | 'email' | 'password'
const modalData = ref({})
const modalError = ref('')
const modalLoading = ref(false)
const modalSuccess = ref('')

const BASE_URL = import.meta.env.VITE_API_URL || ''

async function apiFetch(path, options = {}) {
  const res = await fetch(`${BASE_URL}/api${path}`, {
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    ...options,
  })
  return res.json()
}

onMounted(async () => {
  try {
    const userId = authStore.user?.id
    if (!userId) {
      router.push('/login')
      return
    }
    const data = await apiFetch(`/user/${userId}`)
    if (data.success) {
      user.value.firstName = data.data.username
      user.value.email = data.data.email
    } else {
      error.value = data.error || 'Failed to load user data.'
    }
  } catch (e) {
    error.value = 'Network error.'
  } finally {
    loading.value = false
  }
})

function openModal(type) {
  modal.value = { type }
  modalError.value = ''
  modalSuccess.value = ''
  if (type === 'name') {
    modalData.value = { username: user.value.firstName }
  } else if (type === 'email') {
    modalData.value = { new_email: '', code: '', step: 'request' }
  } else if (type === 'password') {
    modalData.value = { code: '', password: '', confirm: '', step: 'request' }
  }
}

function closeModal() {
  modal.value = { type: null }
  modalError.value = ''
  modalSuccess.value = ''
  modalData.value = {}
  modalLoading.value = false
}

async function saveName() {
  modalLoading.value = true
  modalError.value = ''
  try {
    const data = await apiFetch(`/user/${authStore.user?.id}`, {
      method: 'PUT',
      body: JSON.stringify({ username: modalData.value.username }),
    })
    if (data.success) {
      user.value.firstName = data.data.username
      if (authStore.user) authStore.user.username = data.data.username
      modalSuccess.value = 'Name updated!'
      setTimeout(closeModal, 1000)
    } else {
      modalError.value = data.error
    }
  } catch {
    modalError.value = 'Network error.'
  } finally {
    modalLoading.value = false
  }
}

async function requestEmailCode() {
  modalLoading.value = true
  modalError.value = ''
  try {
    const data = await apiFetch(`/user/${authStore.user?.id}/email/request-change`, {
      method: 'POST',
      body: JSON.stringify({ new_email: modalData.value.new_email }),
    })
    if (data.success) {
      modalData.value.step = 'verify'
      modalSuccess.value = 'Code sent to new email.'
    } else {
      modalError.value = data.error
    }
  } catch {
    modalError.value = 'Network error.'
  } finally {
    modalLoading.value = false
  }
}

async function confirmEmail() {
  modalLoading.value = true
  modalError.value = ''
  try {
    const data = await apiFetch(`/user/${authStore.user?.id}/email/confirm-change`, {
      method: 'POST',
      body: JSON.stringify({ code: modalData.value.code, new_email: modalData.value.new_email }),
    })
    if (data.success) {
      user.value.email = data.data.email
      modalSuccess.value = 'Email updated!'
      setTimeout(closeModal, 1000)
    } else {
      modalError.value = data.error
    }
  } catch {
    modalError.value = 'Network error.'
  } finally {
    modalLoading.value = false
  }
}

async function requestPasswordCode() {
  modalLoading.value = true
  modalError.value = ''
  try {
    const data = await apiFetch(`/user/${authStore.user?.id}/send-change-password-code`, {
      method: 'POST',
    })
    if (data.success) {
      modalData.value.step = 'verify'
      modalSuccess.value = 'Code sent to your email.'
    } else {
      modalError.value = data.error
    }
  } catch {
    modalError.value = 'Network error.'
  } finally {
    modalLoading.value = false
  }
}

async function confirmPassword() {
  modalError.value = ''
  if (modalData.value.password !== modalData.value.confirm) {
    modalError.value = 'Passwords do not match.'
    return
  }
  modalLoading.value = true
  try {
    const data = await apiFetch(`/user/${authStore.user?.id}/change-password`, {
      method: 'POST',
      body: JSON.stringify({ code: modalData.value.code, password: modalData.value.password }),
    })
    if (data.success) {
      modalSuccess.value = 'Password changed!'
      setTimeout(closeModal, 1000)
    } else {
      modalError.value = data.error
    }
  } catch {
    modalError.value = 'Network error.'
  } finally {
    modalLoading.value = false
  }
}

const handleDeleteAccount = () => {
  const confirmText = prompt('Delete your account? All your decks, cards and progress will be permanently deleted. Type DELETE to confirm')
  if (confirmText === 'DELETE') {
    apiFetch(`/user/${authStore.user?.id}`, { method: 'DELETE' }).then(() => {
      authStore.logout()
      router.push('/')
    })
  }
}
</script>

<template>
  <div class="page-container">
    <header class="page-header">
      <router-link to="/cabinet" class="cabinet-logo">
        <div class="mascot-placeholder cabinet-mascot">
          <span class="owl-icon cabinet-owl">🎓</span>
          <span class="back-arrow">
            <img src="/src/assets/LeftArrow.png" alt="Back" class="arrow-img" />
          </span>
        </div>
        <div class="logo-text">
          <h1 class="logo-title">STEP BY STEP</h1>
          <span class="logo-subtitle">Learn with Flashcards</span>
        </div>
      </router-link>
    </header>

    <main class="content-box">
      <h1 class="page-title">Personal Information</h1>

      <div v-if="loading" class="loading-text">Loading...</div>
      <div v-else-if="error" class="error-text">{{ error }}</div>

      <div v-else class="info-form">

        <div class="field-group">
          <label>First Name</label>
          <div class="input-row">
            <input type="text" :value="user.firstName" class="input-base" readonly />
            <button class="edit-link" @click="openModal('name')">Edit</button>
          </div>
        </div>

        <div class="field-group">
          <label>Email</label>
          <div class="input-row">
            <input type="email" :value="user.email" class="input-base" readonly />
            <button class="edit-link" @click="openModal('email')">Edit email</button>
          </div>
        </div>

        <div class="field-group">
          <label>Password</label>
          <div class="input-row">
            <input type="password" value="••••••••" class="input-base" readonly />
            <button class="edit-link" @click="openModal('password')">Edit password</button>
          </div>
        </div>

      </div>

      <div class="danger-zone">
        <button @click="handleDeleteAccount" class="btn btn-outline delete-btn">Delete account</button>
      </div>
    </main>

    <!-- Modal overlay -->
    <div v-if="modal.type" class="modal-overlay" @click.self="closeModal">
      <div class="modal-box">
        <button class="modal-close" @click="closeModal">✕</button>

        <!-- Edit Name -->
        <template v-if="modal.type === 'name'">
          <h2 class="modal-title">Edit Name</h2>
          <div class="modal-field">
            <label>First Name</label>
            <input v-model="modalData.username" class="input-base" type="text" placeholder="Your name" />
          </div>
          <p v-if="modalError" class="modal-error">{{ modalError }}</p>
          <p v-if="modalSuccess" class="modal-success">{{ modalSuccess }}</p>
          <button class="btn btn-primary modal-btn" @click="saveName" :disabled="modalLoading">
            {{ modalLoading ? 'Saving...' : 'Save' }}
          </button>
        </template>

        <!-- Edit Email -->
        <template v-if="modal.type === 'email'">
          <h2 class="modal-title">Edit Email</h2>
          <template v-if="modalData.step === 'request'">
            <div class="modal-field">
              <label>New Email</label>
              <input v-model="modalData.new_email" class="input-base" type="email" placeholder="new@email.com" />
            </div>
            <p v-if="modalError" class="modal-error">{{ modalError }}</p>
            <p v-if="modalSuccess" class="modal-success">{{ modalSuccess }}</p>
            <button class="btn btn-primary modal-btn" @click="requestEmailCode" :disabled="modalLoading">
              {{ modalLoading ? 'Sending...' : 'Send verification code' }}
            </button>
          </template>
          <template v-else>
            <p class="modal-hint">Enter the code sent to <strong>{{ modalData.new_email }}</strong></p>
            <div class="modal-field">
              <label>Verification Code</label>
              <input v-model="modalData.code" class="input-base" type="text" placeholder="123456" />
            </div>
            <p v-if="modalError" class="modal-error">{{ modalError }}</p>
            <p v-if="modalSuccess" class="modal-success">{{ modalSuccess }}</p>
            <button class="btn btn-primary modal-btn" @click="confirmEmail" :disabled="modalLoading">
              {{ modalLoading ? 'Verifying...' : 'Confirm' }}
            </button>
          </template>
        </template>

        <!-- Edit Password -->
        <template v-if="modal.type === 'password'">
          <h2 class="modal-title">Edit Password</h2>
          <template v-if="modalData.step === 'request'">
            <p class="modal-hint">We'll send a verification code to your email.</p>
            <p v-if="modalError" class="modal-error">{{ modalError }}</p>
            <p v-if="modalSuccess" class="modal-success">{{ modalSuccess }}</p>
            <button class="btn btn-primary modal-btn" @click="requestPasswordCode" :disabled="modalLoading">
              {{ modalLoading ? 'Sending...' : 'Send code' }}
            </button>
          </template>
          <template v-else>
            <div class="modal-field">
              <label>Verification Code</label>
              <input v-model="modalData.code" class="input-base" type="text" placeholder="123456" />
            </div>
            <div class="modal-field">
              <label>New Password</label>
              <input v-model="modalData.password" class="input-base" type="password" placeholder="New password" />
            </div>
            <div class="modal-field">
              <label>Confirm Password</label>
              <input v-model="modalData.confirm" class="input-base" type="password" placeholder="Repeat password" />
            </div>
            <p v-if="modalError" class="modal-error">{{ modalError }}</p>
            <p v-if="modalSuccess" class="modal-success">{{ modalSuccess }}</p>
            <button class="btn btn-primary modal-btn" @click="confirmPassword" :disabled="modalLoading">
              {{ modalLoading ? 'Saving...' : 'Change password' }}
            </button>
          </template>
        </template>

      </div>
    </div>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  padding: 3rem 2rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-header {
  width: 100%;
  max-width: 1200px;
  margin-bottom: 2rem;
}

.cabinet-logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  text-decoration: none;
  transition: transform 0.2s ease;
}
.cabinet-logo:hover { transform: scale(1.02); }

.cabinet-mascot {
  position: relative;
  overflow: hidden;
}

.cabinet-owl,
.back-arrow {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  transition: opacity 0.25s ease, transform 0.25s ease;
  line-height: 1;
}
.back-arrow {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.6);
  display: flex;
  align-items: center;
  justify-content: center;
}
.arrow-img {
  width: 26px;
  height: 26px;
  filter: brightness(0) invert(1);
  display: block;
}
.cabinet-logo:hover .cabinet-mascot { transform: rotate(0deg) scale(1.08); }
.cabinet-logo:hover .cabinet-owl { opacity: 0; transform: translate(-50%, -50%) scale(0.6); }
.cabinet-logo:hover .back-arrow { opacity: 1; transform: translate(-50%, -50%) scale(1); }

.content-box {
  width: 100%;
  max-width: 600px;
  background-color: transparent;
  animation: fadeIn 0.4s ease-out;
  text-align: center;
}

.page-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 2.2rem;
  color: var(--color-text);
  margin-bottom: 2.5rem;
  text-align: center;
}

.loading-text, .error-text {
  text-align: center;
  color: var(--color-text);
  margin-bottom: 2rem;
}
.error-text { color: var(--color-error); }

.info-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3rem;
}

.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-group label {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text);
  margin-left: 0.5rem;
}

.input-row {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.input-base:read-only {
  background-color: #FAFAFA;
}

.edit-link {
  background: none;
  border: none;
  color: var(--color-primary);
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  cursor: pointer;
  white-space: nowrap;
}
.edit-link:hover { text-decoration: underline; }

.danger-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
}

.delete-btn {
  border-color: var(--color-error);
  color: var(--color-error);
}
.delete-btn:hover { background-color: rgba(255, 0, 0, 0.05); }

/* Modal */
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
}

.modal-box {
  background: #fff;
  border-radius: 16px;
  padding: 2rem;
  width: 100%;
  max-width: 420px;
  position: relative;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.modal-close {
  position: absolute;
  top: 1rem;
  right: 1rem;
  background: none;
  border: none;
  font-size: 1rem;
  cursor: pointer;
  color: #888;
}
.modal-close:hover { color: #333; }

.modal-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 1.4rem;
  color: var(--color-text);
  margin: 0;
}

.modal-hint {
  font-size: 0.9rem;
  color: #666;
  margin: 0;
}

.modal-field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  text-align: left;
}

.modal-field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text);
}

.modal-error {
  color: var(--color-error);
  font-size: 0.85rem;
  margin: 0;
}

.modal-success {
  color: green;
  font-size: 0.85rem;
  margin: 0;
}

.modal-btn {
  width: 100%;
  margin-top: 0.5rem;
}
</style>