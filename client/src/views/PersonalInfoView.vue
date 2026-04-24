<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const user = ref({
  firstName: 'John',
  lastName: 'Doe',
  email: 'johndoe@mail.com',
  password: '••••••••'
})

const goBack = () => {
  router.push('/cabinet')
}

const handleDeleteAccount = () => {
  const confirmText = prompt('Delete your account? All your decks, cards and progress will be permanently deleted. Type DELETE to confirm')
  if (confirmText === 'DELETE') {
    alert('Account deleted.')
    router.push('/')
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

      <div class="info-form">
        
        <div class="field-group">
          <label>First Name</label>
          <div class="input-row">
            <input type="text" v-model="user.firstName" class="input-base" readonly />
            <button class="edit-link">Edit</button>
          </div>
        </div>

        <div class="field-group">
          <label>Last Name</label>
          <div class="input-row">
            <input type="text" v-model="user.lastName" class="input-base" readonly />
            <button class="edit-link">Edit</button>
          </div>
        </div>

        <div class="field-group">
          <label>Email</label>
          <div class="input-row">
            <input type="email" v-model="user.email" class="input-base" readonly />
            <button class="edit-link">Edit email</button>
          </div>
        </div>

        <div class="field-group">
          <label>Password</label>
          <div class="input-row">
            <input type="password" v-model="user.password" class="input-base" readonly />
            <button class="edit-link">Edit password</button>
          </div>
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

.edit-link:hover {
  text-decoration: underline;
}

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

.delete-btn:hover {
  background-color: rgba(255, 0, 0, 0.05);
}
</style>
