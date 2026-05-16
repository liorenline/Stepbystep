<script setup>
import { ref, onMounted } from 'vue'
import { userApi } from '@/api/index.js'

// ── User state ────────────────────────────────────────────────────────
const userId = ref(null)
const user = ref({ nickname: '', email: '' })
const loading = ref(true)
const globalError = ref(null)

onMounted(async () => {
  try {
    const { data } = await userApi.getMe()
    userId.value = data.data.id
    user.value.nickname = data.data.username
    user.value.email = data.data.email
  } catch (err) {
    globalError.value = 'Не вдалося завантажити дані користувача'
    console.error(err)
  } finally {
    loading.value = false
  }
})

// ── Edit state machine ────────────────────────────────────────────────
// field: null | 'nickname' | 'email' | 'password'
// step:  'input' | 'verify'
const editingField = ref(null)
const editStep = ref('input')

const saving = ref(false)
const fieldError = ref('')
const fieldSuccess = ref('')

// Temp values
const tempNickname = ref('')
const tempEmail = ref('')
const tempNewPassword = ref('')
const tempConfirmPassword = ref('')
const verifyCode = ref(['', '', '', '', '', ''])

function startEdit(field) {
  editingField.value = field
  editStep.value = 'input'
  fieldError.value = ''
  fieldSuccess.value = ''
  verifyCode.value = ['', '', '', '', '', '']

  if (field === 'nickname') tempNickname.value = user.value.nickname
  if (field === 'email') tempEmail.value = ''
  if (field === 'password') { tempNewPassword.value = ''; tempConfirmPassword.value = '' }
}

function cancelEdit() {
  editingField.value = null
  editStep.value = 'input'
  fieldError.value = ''
  fieldSuccess.value = ''
  verifyCode.value = ['', '', '', '', '', '']
}

function getCodeString() {
  return verifyCode.value.join('')
}

// ── Code input helpers ────────────────────────────────────────────────
function handleCodeInput(index, event) {
  const val = event.target.value.replace(/\D/g, '')
  verifyCode.value[index] = val.slice(-1)
  if (val && index < 5) {
    document.getElementById(`code-input-${index + 1}`)?.focus()
  }
}

function handleCodeKeydown(index, event) {
  if (event.key === 'Backspace' && !verifyCode.value[index] && index > 0) {
    document.getElementById(`code-input-${index - 1}`)?.focus()
  }
}

// ── NICKNAME ─────────────────────────────────────────────────────────
async function saveNickname() {
  const val = tempNickname.value.trim()
  if (!val) { fieldError.value = 'Нікнейм не може бути порожнім'; return }
  if (val.length < 3) { fieldError.value = 'Мінімум 3 символи'; return }
  if (val === user.value.nickname) { cancelEdit(); return }

  saving.value = true; fieldError.value = ''
  try {
    await userApi.updateUsername(userId.value, val)
    user.value.nickname = val
    fieldSuccess.value = 'Нікнейм змінено!'
    setTimeout(cancelEdit, 1500)
  } catch (err) {
    fieldError.value = err?.response?.data?.error || 'Помилка при збереженні'
  } finally {
    saving.value = false
  }
}

// ── EMAIL ─────────────────────────────────────────────────────────────
async function requestEmailChange() {
  const val = tempEmail.value.trim()
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  if (!val) { fieldError.value = 'Введіть нову пошту'; return }
  if (!emailRegex.test(val)) { fieldError.value = 'Некоректний email'; return }
  if (val === user.value.email) { fieldError.value = 'Це вже ваша поточна пошта'; return }

  saving.value = true; fieldError.value = ''
  try {
    await userApi.requestEmailChange(userId.value, val)
    editStep.value = 'verify'
    verifyCode.value = ['', '', '', '', '', '']
    setTimeout(() => document.getElementById('code-input-0')?.focus(), 100)
  } catch (err) {
    fieldError.value = err?.response?.data?.error || 'Помилка при відправці коду'
  } finally {
    saving.value = false
  }
}

async function confirmEmailChange() {
  const code = getCodeString()
  if (code.length < 6) { fieldError.value = 'Введіть повний 6-значний код'; return }

  saving.value = true; fieldError.value = ''
  try {
    await userApi.confirmEmailChange(userId.value, tempEmail.value.trim(), code)
    user.value.email = tempEmail.value.trim()
    fieldSuccess.value = 'Email успішно змінено!'
    setTimeout(cancelEdit, 1500)
  } catch (err) {
    fieldError.value = err?.response?.data?.error || 'Невірний або застарілий код'
  } finally {
    saving.value = false
  }
}

// ── PASSWORD ──────────────────────────────────────────────────────────
async function requestPasswordChange() {
  if (!tempNewPassword.value) { fieldError.value = 'Введіть новий пароль'; return }
  if (tempNewPassword.value.length < 8) { fieldError.value = 'Мінімум 8 символів'; return }
  if (tempNewPassword.value !== tempConfirmPassword.value) { fieldError.value = 'Паролі не збігаються'; return }

  saving.value = true; fieldError.value = ''
  try {
    await userApi.sendPasswordCode(userId.value)
    editStep.value = 'verify'
    verifyCode.value = ['', '', '', '', '', '']
    setTimeout(() => document.getElementById('code-input-0')?.focus(), 100)
  } catch (err) {
    fieldError.value = err?.response?.data?.error || 'Помилка при відправці коду'
  } finally {
    saving.value = false
  }
}

async function confirmPasswordChange() {
  const code = getCodeString()
  if (code.length < 6) { fieldError.value = 'Введіть повний 6-значний код'; return }

  saving.value = true; fieldError.value = ''
  try {
    await userApi.changePassword(userId.value, code, tempNewPassword.value)
    fieldSuccess.value = 'Пароль успішно змінено!'
    setTimeout(cancelEdit, 1500)
  } catch (err) {
    fieldError.value = err?.response?.data?.error || 'Невірний або застарілий код'
  } finally {
    saving.value = false
  }
}

function handleDeleteAccount() {
  // TODO: your existing delete logic
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

      <div v-if="loading" class="loading-state">Завантаження...</div>
      <div v-else-if="globalError" class="error-banner">{{ globalError }}</div>

      <div v-else class="info-form">

        <!-- ── NICKNAME ── -->
        <div class="field-group">
          <label>Nickname</label>

          <template v-if="editingField !== 'nickname'">
            <div class="input-row">
              <input type="text" :value="user.nickname" class="input-base" readonly />
              <button class="edit-link" @click="startEdit('nickname')">Edit</button>
            </div>
          </template>

          <template v-else>
            <div class="edit-block">
              <div class="input-row">
                <input
                  type="text"
                  v-model="tempNickname"
                  class="input-base input-active"
                  placeholder="Новий нікнейм"
                  autofocus
                  @keydown.enter="saveNickname"
                  @keydown.esc="cancelEdit"
                />
              </div>
              <p v-if="fieldError" class="field-error">{{ fieldError }}</p>
              <p v-if="fieldSuccess" class="field-success">{{ fieldSuccess }}</p>
              <div class="action-row">
                <button class="btn-save" @click="saveNickname" :disabled="saving">
                  {{ saving ? 'Збереження...' : 'Зберегти' }}
                </button>
                <button class="btn-cancel" @click="cancelEdit">Скасувати</button>
              </div>
            </div>
          </template>
        </div>

        <!-- ── EMAIL ── -->
        <div class="field-group">
          <label>Email</label>

          <template v-if="editingField !== 'email'">
            <div class="input-row">
              <input type="email" :value="user.email" class="input-base" readonly />
              <button class="edit-link" @click="startEdit('email')">Edit email</button>
            </div>
          </template>

          <!-- Step 1: ввести нову пошту -->
          <template v-else-if="editStep === 'input'">
            <div class="edit-block">
              <p class="edit-hint">Enter a new address — we'll send a verification code to it</p>
              <div class="input-row">
                <input
                  type="email"
                  v-model="tempEmail"
                  class="input-base input-active"
                  placeholder="New email"
                  autofocus
                  @keydown.enter="requestEmailChange"
                  @keydown.esc="cancelEdit"
                />
              </div>
              <p v-if="fieldError" class="field-error">{{ fieldError }}</p>
              <div class="action-row">
                <button class="btn-save" @click="requestEmailChange" :disabled="saving">
                  {{ saving ? 'Sending...' : 'Send code' }}
                </button>
                <button class="btn-cancel" @click="cancelEdit">Cancel</button>
              </div>
            </div>
          </template>

          <!-- Step 2: ввести код -->
          <template v-else>
            <div class="edit-block verify-block">
              <p class="edit-hint">
                Code send to <strong>{{ tempEmail }}</strong>
              </p>
              <div class="code-inputs">
                <input
                  v-for="(digit, idx) in verifyCode"
                  :key="idx"
                  :id="'code-input-' + idx"
                  type="text"
                  inputmode="numeric"
                  maxlength="1"
                  :value="verifyCode[idx]"
                  @input="handleCodeInput(idx, $event)"
                  @keydown="handleCodeKeydown(idx, $event)"
                  class="digit-box"
                />
              </div>
              <p v-if="fieldError" class="field-error">{{ fieldError }}</p>
              <p v-if="fieldSuccess" class="field-success">{{ fieldSuccess }}</p>
              <div class="action-row">
                <button class="btn-save" @click="confirmEmailChange" :disabled="saving">
                  {{ saving ? 'Checking' : 'Confirm' }}
                </button>
                <button class="btn-cancel" @click="() => { editStep = 'input'; fieldError = '' }">
                  Назад
                </button>
              </div>
            </div>
          </template>
        </div>

        <!-- ── PASSWORD ── -->
        <div class="field-group">
          <label>Password</label>

          <template v-if="editingField !== 'password'">
            <div class="input-row">
              <input type="password" value="••••••••" class="input-base" readonly />
              <button class="edit-link" @click="startEdit('password')">Edit password</button>
            </div>
          </template>

          <!-- Step 1: ввести новий пароль -->
          <template v-else-if="editStep === 'input'">
            <div class="edit-block">
              <p class="edit-hint">Code was sent to email</p>
              <div class="input-row">
                <input
                  type="password"
                  v-model="tempNewPassword"
                  class="input-base input-active"
                  placeholder="New password"
                  autofocus
                  @keydown.esc="cancelEdit"
                />
              </div>
              <div class="input-row" style="margin-top: 0.75rem;">
                <input
                  type="password"
                  v-model="tempConfirmPassword"
                  class="input-base input-active"
                  placeholder="Confirm new password"
                  @keydown.enter="requestPasswordChange"
                  @keydown.esc="cancelEdit"
                />
              </div>
              <p v-if="fieldError" class="field-error">{{ fieldError }}</p>
              <div class="action-row">
                <button class="btn-save" @click="requestPasswordChange" :disabled="saving">
                  {{ saving ? 'Sending' : 'Send code' }}
                </button>
                <button class="btn-cancel" @click="cancelEdit">Cancel</button>
              </div>
            </div>
          </template>

          <!-- Step 2: ввести код -->
          <template v-else>
            <div class="edit-block verify-block">
              <p class="edit-hint">
                Code was sent to <strong>{{ user.email }}</strong>
              </p>
              <div class="code-inputs">
                <input
                  v-for="(digit, idx) in verifyCode"
                  :key="idx"
                  :id="'code-input-' + idx"
                  type="text"
                  inputmode="numeric"
                  maxlength="1"
                  :value="verifyCode[idx]"
                  @input="handleCodeInput(idx, $event)"
                  @keydown="handleCodeKeydown(idx, $event)"
                  class="digit-box"
                />
              </div>
              <p v-if="fieldError" class="field-error">{{ fieldError }}</p>
              <p v-if="fieldSuccess" class="field-success">{{ fieldSuccess }}</p>
              <div class="action-row">
                <button class="btn-save" @click="confirmPasswordChange" :disabled="saving">
                  {{ saving ? 'Checking...' : 'Confirm' }}
                </button>
                <button class="btn-cancel" @click="() => { editStep = 'input'; fieldError = '' }">
                  Назад
                </button>
              </div>
            </div>
          </template>
        </div>

      </div>

      <div class="danger-zone">
        <button @click="handleDeleteAccount" class="btn btn-outline delete-btn">Delete account</button>
      </div>
    </main>
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
.cabinet-mascot { position: relative; overflow: hidden; }
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
  display: flex;
  flex-direction: column;
  align-items: center;
}
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}

.page-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 2.2rem;
  color: var(--color-text);
  margin-bottom: 2.5rem;
  text-align: center;
}
.info-form {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  margin-bottom: 3rem;
}
.field-group {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  align-items: center;
  width: 100%;
}
.field-group label {
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.9rem;
  color: var(--color-text);
  align-self: flex-start;
  margin-left: 0.5rem;
}
.input-row {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 100%;
  justify-content: center;
}
.input-base {
  flex: 1;
  text-align: center;
}
.input-base:read-only { background-color: #FAFAFA; }
.input-active {
  background-color: #fff;
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
  outline: none;
  transition: border-color 0.2s ease, box-shadow 0.2s ease;
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
  width: 110px;
  text-align: left;
}
.edit-link:hover { text-decoration: underline; }

/* Edit block */
.edit-block {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  animation: slideDown 0.2s ease-out;
}
@keyframes slideDown {
  from { opacity: 0; transform: translateY(-6px); }
  to   { opacity: 1; transform: translateY(0); }
}

.edit-hint {
  font-family: 'Inter', sans-serif;
  font-size: 0.82rem;
  color: var(--color-text-light, #888);
  margin: 0 0 0.25rem 0.25rem;
}

/* Code inputs */
.verify-block { align-items: center; }
.code-inputs {
  display: flex;
  gap: 0.6rem;
  margin: 0.5rem 0;
  justify-content: center;
}
.digit-box {
  width: 46px;
  height: 52px;
  text-align: center;
  font-size: 1.4rem;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  border: 1.5px solid #CCCCCC;
  border-radius: 8px;
  outline: none;
  transition: border-color 0.15s ease, box-shadow 0.15s ease;
  caret-color: var(--color-primary);
}
.digit-box:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.15);
}

/* Actions */
.action-row {
  display: flex;
  gap: 0.75rem;
  margin-top: 0.5rem;
  justify-content: flex-end;
}
.btn-save {
  background-color: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: 8px;
  padding: 0.45rem 1.2rem;
  font-family: 'Inter', sans-serif;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: opacity 0.2s ease, transform 0.15s ease;
}
.btn-save:hover:not(:disabled) { opacity: 0.88; transform: translateY(-1px); }
.btn-save:disabled { opacity: 0.5; cursor: not-allowed; }
.btn-cancel {
  background: none;
  border: 1px solid rgba(0,0,0,0.15);
  border-radius: 8px;
  padding: 0.45rem 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.875rem;
  color: var(--color-text);
  cursor: pointer;
  transition: background 0.15s ease;
}
.btn-cancel:hover { background-color: rgba(0,0,0,0.04); }

/* Messages */
.field-error {
  font-size: 0.82rem;
  color: var(--color-error, #e53e3e);
  margin: 0;
  padding-left: 0.25rem;
}
.field-success {
  font-size: 0.82rem;
  color: #38a169;
  margin: 0;
  padding-left: 0.25rem;
}
.loading-state {
  color: var(--color-text);
  font-family: 'Inter', sans-serif;
  padding: 2rem;
  opacity: 0.6;
}
.error-banner {
  color: var(--color-error, #e53e3e);
  font-family: 'Inter', sans-serif;
  padding: 1rem;
  background: rgba(229, 62, 62, 0.07);
  border-radius: 8px;
  width: 100%;
  text-align: center;
}

/* Danger zone */
.danger-zone {
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid rgba(0, 0, 0, 0.1);
  width: 100%;
}
.delete-btn {
  border-color: var(--color-error);
  color: var(--color-error);
}
.delete-btn:hover { background-color: rgba(255, 0, 0, 0.05); }
</style>