<script setup>
import { ref } from 'vue';

const username = ref('');
const email = ref('');
const password = ref('');
const confirmPassword = ref('');
const passwordStrength = ref('');

const checkPassword = () => {
  if (password.value.length === 0) {
    passwordStrength.value = '';
    return;
  }
  if (password.value.length < 8) {
    passwordStrength.value = 'Password is too weak';
  } else {
    passwordStrength.value = '';
  }
};
</script>

<template>
  <div class="auth-container">
    <div class="auth-box">
      <router-link to="/" class="auth-logo">
        <div class="mascot-placeholder">
          <span class="owl-icon">🎓</span>
        </div>
        <div class="logo-text">
          <span class="logo-title">STEP BY STEP</span>
          <span class="logo-subtitle">Learn with Flashcards</span>
        </div>
      </router-link>

      <h1 class="title">Sign up</h1>

      <form class="auth-form" @submit.prevent>
        <div class="input-group">
          <label>Username <span class="required">*</span></label>
          <input 
            type="text" 
            v-model="username" 
            class="input-base" 
            placeholder="johndoe"
          />
        </div>

        <div class="input-group">
          <label>Email <span class="required">*</span></label>
          <input 
            type="email" 
            v-model="email" 
            class="input-base" 
            placeholder="example@mail.com"
          />
        </div>

        <div class="input-group">
          <label>Password <span class="required">*</span></label>
          <div class="password-wrapper">
            <input 
              type="password" 
              v-model="password" 
              class="input-base" 
              :class="{ 'input-error': passwordStrength }"
              @input="checkPassword"
              placeholder="••••••••"
            />
            <span class="eye-icon">👁️</span>
          </div>
          <span v-if="passwordStrength" class="error-msg">{{ passwordStrength }}</span>
          <p class="hint-msg">Password must contain 1 uppercase letter and 1 special character</p>
        </div>

        <div class="input-group">
          <label>Confirm Password <span class="required">*</span></label>
          <div class="password-wrapper">
            <input 
              type="password" 
              v-model="confirmPassword" 
              class="input-base" 
              placeholder="••••••••"
            />
            <span class="eye-icon">👁️</span>
          </div>
        </div>

        <div class="actions">
          <button class="btn btn-primary create-btn">Create an account</button>
        </div>

        <p class="switch-auth">
          Already have an account? <router-link to="/login">Log in</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<style scoped>
.auth-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.8rem;
  text-decoration: none;
  margin-bottom: 2rem;
  transition: transform 0.2s ease;
}

.auth-logo:hover {
  transform: scale(1.02);
}

/* Mascot unrotates and pops on hover — same as Home page */
.auth-logo:hover .mascot-placeholder {
  transform: rotate(0deg) scale(1.08);
}

.auth-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
}

.auth-box {
  width: 100%;
  max-width: 480px;
  padding: 3rem 2rem;
  text-align: center;
}

.title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 1.8rem;
  margin-bottom: 2rem;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  text-align: left;
}

.input-group label {
  display: block;
  font-family: 'Inter', sans-serif;
  font-size: 0.9rem;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.required {
  color: var(--color-error);
}

.password-wrapper {
  position: relative;
}
.eye-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  cursor: pointer;
  opacity: 0.6;
}

.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.switch-auth {
  text-align: center;
  margin-top: 1rem;
  font-size: 0.9rem;
}
.switch-auth a {
  color: var(--color-primary);
  font-weight: bold;
  text-decoration: none;
}
.switch-auth a:hover {
  text-decoration: underline;
}

.error-msg {
  color: var(--color-error);
  font-size: 0.85rem;
  display: block;
  margin-top: 0.5rem;
}
.hint-msg {
  color: var(--color-text-light);
  font-size: 0.75rem;
  margin-top: 0.5rem;
}
.create-btn {
  width: 100%;
  max-width: 300px;
  padding: 0.75rem;
}
</style>
