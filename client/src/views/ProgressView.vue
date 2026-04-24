<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const overallCorrect = ref(85) // Example stat

const decks = ref([
  { id: 1, name: 'Spanish Verbs', description: 'Essential regular and irregular verbs.', correctPercentage: 92, cardsCount: 120, lastReviewed: '2 hours ago' },
  { id: 2, name: 'React Fundamentals', description: 'Hooks, state, and props basics.', correctPercentage: 78, cardsCount: 45, lastReviewed: '1 day ago' },
  { id: 3, name: 'Biology 101', description: 'Cell structures and functions.', correctPercentage: 60, cardsCount: 88, lastReviewed: '3 days ago' }
])

const goHome = () => {
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
      <h1 class="page-title">My progress</h1>
      <p class="subtitle">You have {{ overallCorrect }}% correct answers from all decks</p>

      <div class="decks-grid">
        <div v-for="deck in decks" :key="deck.id" class="deck-card">
          <div class="card-header">
            <h2 class="deck-name">{{ deck.name }}</h2>
            <span class="percentage">{{ deck.correctPercentage }}% correct</span>
          </div>
          <p class="deck-desc">{{ deck.description }}</p>
          
          <div class="progress-section">
             <div class="progress-bar-bg">
               <div class="progress-bar-fill" :style="{ width: deck.correctPercentage + '%' }"></div>
             </div>
             <span class="progress-label">{{ deck.cardsCount * (deck.correctPercentage / 100) }} mastered / {{ deck.cardsCount }} remaining</span>
          </div>

          <div class="card-footer">
            <span class="stat">Last reviewed: {{ deck.lastReviewed }}</span>
            <button class="btn btn-outline small-action" @click="router.push('/deck/' + deck.id + '/study')">Play again!</button>
          </div>
        </div>
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

/* --- Cabinet logo hover animation --- */
.cabinet-logo {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  text-decoration: none;
  transition: transform 0.2s ease;
}

.cabinet-logo:hover {
  transform: scale(1.02);
}

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

.cabinet-logo:hover .cabinet-mascot {
  transform: rotate(0deg) scale(1.08);
}

.cabinet-logo:hover .cabinet-owl {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.6);
}

.cabinet-logo:hover .back-arrow {
  opacity: 1;
  transform: translate(-50%, -50%) scale(1);
}

.content-box {
  width: 100%;
  max-width: 1200px;
  animation: fadeIn 0.4s ease-out;
}

.page-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 3rem;
  color: var(--color-text);
  margin-bottom: 1rem;
  text-align: center;
}

.subtitle {
  font-family: var(--font-main), 'Playfair Display', serif;
  text-align: center;
  font-size: 1.2rem;
  color: var(--color-text-light);
  margin-bottom: 3rem;
}

.decks-grid {
  display: grid;
  flex-wrap: wrap;
  gap: 2rem;
  width: 100%;
  justify-content: center;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
}

@media (max-width: 768px) {
  .decks-grid {
    grid-template-columns: 1fr;
  }
}

.deck-card {
  background-color: var(--color-primary);
  border-radius: 16px;
  padding: 1.5rem;
  color: #FFFFFF;
  box-shadow: 0 8px 20px rgba(140, 82, 255, 0.4);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
}

.deck-card:hover {
  transform: translateY(-5px);
}

.deck-name {
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin: 0;
}

.deck-desc {
  font-family: 'Inter', sans-serif;
  font-size: 0.95rem;
  opacity: 0.9;
  flex: 1;
  line-height: 1.5;
  margin-bottom: 1.5rem;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 1rem;
}

.percentage {
  font-family: 'Inter', sans-serif;
  font-weight: 800;
  font-size: 1.1rem;
  background-color: rgba(0, 0, 0, 0.2);
  padding: 0.25rem 0.5rem;
  border-radius: 8px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-top: 1px solid rgba(255, 255, 255, 0.2);
  padding-top: 1rem;
}

.stat {
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  opacity: 0.8;
}

.progress-section {
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.progress-bar-bg {
  width: 100%;
  height: 8px;
  background-color: rgba(255, 255, 255, 0.25);
  border-radius: 10px;
  overflow: hidden;
}

.progress-bar-fill {
  height: 100%;
  background-color: #FFFFFF;
  border-radius: 10px;
  transition: width 0.4s ease;
  box-shadow: 0 0 8px rgba(255, 255, 255, 0.5);
}

.progress-label {
  font-family: 'Inter', sans-serif;
  font-size: 0.8rem;
  opacity: 0.8;
  text-align: right;
}

.small-action {
  padding: 0.4rem 1rem;
  font-size: 0.85rem;
  border-color: #FFFFFF;
  color: #FFFFFF;
}
.small-action:hover {
  background-color: #FFFFFF;
  color: var(--color-primary);
}
</style>
