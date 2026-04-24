<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const step = ref('setup') // 'setup' | 'verify'
const contact = ref('')
const errorMsg = ref('')

const code = ref(['', '', '', '', '', ''])

const goBack = () => {
  if (step.value === 'verify') {
    step.value = 'setup'
  } else {
    router.push('/cabinet')
  }
}

const handleSendLetter = () => {
  if (!contact.value) {
    errorMsg.value = 'Invalid email address'
    return
  }
  errorMsg.value = ''
  step.value = 'verify'
}

const handleCodeInput = (index, event) => {
  const value = event.target.value
  if (value && index < 5) {
    // move focus to next
    const nextInput = document.getElementById(`code-input-${index + 1}`)
    if (nextInput) nextInput.focus()
  }
}

const handleVerify = () => {
  // Logic to verify
  alert('Verified successfully!')
  router.push('/cabinet')
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
      <!-- SETUP STEP -->
      <div v-if="step === 'setup'" class="step-container">
        <!-- Re-use logo block from Home/Cabinet if desired, or just title -->
        <h1 class="page-title">Set up your Two-Factor Authentication</h1>
        
        <div class="input-group">
          <input 
            type="email" 
            v-model="contact" 
            placeholder="Email address" 
            class="input-base"
            :class="{ 'input-error': errorMsg }"
          />
          <span v-if="errorMsg" class="error-msg">{{ errorMsg }}</span>
        </div>

        <button @click="handleSendLetter" class="btn btn-outline action-btn">Send a letter</button>
      </div>

      <!-- VERIFY STEP -->
      <div v-else class="step-container">
        <h1 class="page-title">Enter verification code</h1>
        <p class="instruction">We sent a 6-digit code to your email address</p>

        <div class="code-inputs">
          <input 
            v-for="(digit, idx) in code" 
            :key="idx"
            :id="'code-input-' + idx"
            type="text"
            maxlength="1"
            v-model="code[idx]"
            @input="handleCodeInput(idx, $event)"
            class="digit-box"
          />
        </div>

        <span class="resend-link">Resend code in 30s</span>
        
        <button @click="handleVerify" class="btn btn-primary action-btn verify-btn">Verify</button>
        
        <span @click="step = 'setup'" class="alt-method-link">Use another method</span>
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
  margin-bottom: 1.5rem;
  text-align: center;
}

.error-msg {
  color: var(--color-error);
  font-size: 0.85rem;
  display: block;
  margin-top: 0.5rem;
}

.step-container {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.instruction {
  font-family: 'Inter', sans-serif;
  color: var(--color-text-light);
  margin-bottom: 2rem;
}

.input-group {
  width: 100%;
  max-width: 350px;
  margin-bottom: 2rem;
  text-align: center;
}

.action-btn {
  width: 100%;
  max-width: 250px;
}

.verify-btn {
  margin-top: 1.5rem;
  margin-bottom: 1.5rem;
}

.code-inputs {
  display: flex;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.digit-box {
  width: 50px;
  height: 50px;
  text-align: center;
  font-size: 1.5rem;
  font-family: 'Inter', sans-serif;
  border: 1px solid #CCCCCC;
  border-radius: 8px;
  outline: none;
}

.digit-box:focus {
  border-color: var(--color-primary);
}

.resend-link, .alt-method-link {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  color: var(--color-text-light);
  cursor: pointer;
}

.alt-method-link:hover {
  text-decoration: underline;
  color: var(--color-primary);
}
</style>
