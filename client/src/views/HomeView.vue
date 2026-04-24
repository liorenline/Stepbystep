<script setup>
</script>

<template>
  <div class="home-container">
    <div class="content-wrapper">
      
      <!-- Left Column: Branding -->
      <div class="left-col">
        <div class="big-mascot">
          <span class="big-owl">🎓</span>
        </div>
        <h1 class="brand-title">STEP BY STEP</h1>
        <span class="brand-subtitle">Learn with Flashcards</span>
      </div>

      <!-- Right Column: Welcome Content -->
      <div class="right-col">
        <h2 class="welcome-title">Welcome to our website!</h2>
        <p class="welcome-desc">
          Here, knowledge becomes simple and learning becomes interesting. Start your journey to success today!
        </p>
        <div class="actions">
          <router-link to="/signup" class="btn btn-primary start-btn">Start</router-link>
        </div>
      </div>

    </div>
  </div>
</template>


<style scoped>
.home-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  padding: 2rem;
}

.content-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8rem;
  max-width: 1100px;
  width: 100%;
}

/* --- Left Column: Big Logo --- */
.left-col {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
  flex-shrink: 0;
}

.big-mascot {
  background-color: var(--color-primary);
  width: 120px;
  height: 120px;
  border-radius: 30px;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 15px 35px rgba(140, 82, 255, 0.45);
  transform: rotate(-10deg);
  margin-bottom: 1.5rem;
  transition: transform 0.3s ease;
}

.big-mascot:hover {
  transform: rotate(0deg) scale(1.05);
}

.big-owl {
  font-size: 3.2rem;
  transform: rotate(5deg);
  line-height: 1;
  display: block;
}

.brand-title {
  font-family: 'Inter', 'Montserrat', sans-serif;
  color: var(--color-text);
  font-size: 2rem;
  font-weight: 900;
  line-height: 1;
  letter-spacing: -1px;
  margin: 0 0 0.3rem 0;
}

.brand-subtitle {
  font-family: 'Inter', 'Montserrat', sans-serif;
  color: #6C4AB6;
  font-size: 0.95rem;
  font-weight: 500;
}

/* --- Right Column --- */
.right-col {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  max-width: 450px;
}

.welcome-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  color: var(--color-text);
  font-size: 2.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
  line-height: 1.2;
}

.welcome-desc {
  font-family: 'Inter', sans-serif;
  color: var(--color-text-light);
  font-size: 1.1rem;
  line-height: 1.7;
  margin-bottom: 3rem;
}

.actions {
  display: flex;
  width: 100%;
}

.start-btn {
  padding: 1rem 4rem;
  font-size: 1.2rem;
  font-weight: 700;
}

/* --- Responsive --- */
@media (max-width: 900px) {
  .content-wrapper {
    flex-direction: column;
    gap: 4rem;
    text-align: center;
  }
  .right-col {
    align-items: center;
  }
}
</style>
