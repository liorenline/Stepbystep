<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

const goDashboard = () => {
  router.push('/dashboard')
}

const studyAgain = () => {
  router.push(`/deck/${route.params.id}/study`)
}
</script>

<template>
  <div class="success-container">
    
    <div class="success-card">
      <div class="icon-wrapper">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round" class="check-icon">
          <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path>
          <polyline points="22 4 12 14.01 9 11.01"></polyline>
        </svg>
      </div>

      <h1 class="success-title">Done!</h1>
      <p class="success-text">You have successfully completed this studying session. Great job learning the new cards!</p>

      <div class="actions">
        <button class="btn btn-outline lg-btn" @click="studyAgain">Study Again</button>
        <button class="btn btn-primary lg-btn" @click="goDashboard">Back to Dashboard</button>
      </div>
    </div>

  </div>
</template>


<style scoped>
.success-container {
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 2rem;
}

.success-card {
  width: 100%;
  max-width: 500px;
  background-color: #FFFFFF;
  border-radius: 32px;
  padding: 4rem 3rem;
  box-shadow: 0 20px 50px rgba(140, 82, 255, 0.15);
  border: 2px solid rgba(192, 132, 252, 0.1);
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

@keyframes slideUp {
  0% { opacity: 0; transform: translateY(40px) scale(0.95); }
  100% { opacity: 1; transform: translateY(0) scale(1); }
}

.icon-wrapper {
  width: 120px;
  height: 120px;
  background-color: rgba(140, 82, 255, 0.1);
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 2rem;
  color: var(--color-primary);
  animation: scalePop 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.2s both;
}

@keyframes scalePop {
  0% { transform: scale(0); }
  70% { transform: scale(1.1); }
  100% { transform: scale(1); }
}

.check-icon {
  width: 60px;
  height: 60px;
}

.success-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 3.5rem;
  font-weight: 800;
  color: var(--color-text);
  margin-bottom: 1rem;
}

.success-text {
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  color: var(--color-text-light);
  line-height: 1.5;
  margin-bottom: 3rem;
}

.lg-btn {
  width: 100%;
  padding: 1rem 3rem;
  font-size: 1.2rem;
  border-radius: 50px;
  min-width: 200px;
}

.actions {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  width: 100%;
}
</style>
