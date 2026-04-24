<script setup>
import { ref } from 'vue'

const searchQuery = ref('')

const decks = ref([
  { id: 1, name: 'Spanish Verbs', description: 'Essential regular and irregular verbs.', cardsCount: 120, lastRepetition: '2 hours ago' },
  { id: 2, name: 'React Fundamentals', description: 'Hooks, state, and props basics.', cardsCount: 45, lastRepetition: '1 day ago' }
])
</script>

<template>
  <div class="dashboard-container">
    
    <!-- Header -->
    <header class="dashboard-header">
      <router-link to="/" class="logo">
        <div class="mascot-placeholder">
          <span class="owl-icon">🎓</span>
        </div>
        <div class="logo-text">
          <h1 class="logo-title">STEP BY STEP</h1>
          <span class="logo-subtitle">Learn with Flashcards</span>
        </div>
      </router-link>

      <div class="search-bar">
        <input 
          type="text" 
          v-model="searchQuery" 
          placeholder="Search your decks..." 
          class="input-base search-input"
        />
        <span class="search-icon">🔍</span>
      </div>

      <router-link to="/cabinet" class="profile-icon" title="My Cabinet">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </router-link>
    </header>

    <!-- Main Content -->
    <main class="dashboard-content">
      <div class="decks-grid">
        
        <!-- Deck Cards -->
        <div v-for="deck in decks" :key="deck.id" class="deck-card">
          <div class="deck-actions">
            <router-link :to="'/deck/' + deck.id + '/study'" class="icon-btn play-btn" title="Study Deck">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="currentColor" xmlns="http://www.w3.org/2000/svg">
                <path d="M8 5v14l11-7z" />
              </svg>
            </router-link>
            <router-link :to="'/deck/' + deck.id + '/manage'" class="icon-btn edit-btn" title="Manage Deck">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"></path>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"></path>
              </svg>
            </router-link>
          </div>
          
          <h2 class="deck-name">{{ deck.name }}</h2>
          <p class="deck-desc">{{ deck.description }}</p>
          <div class="deck-footer">
            <span class="stat">Cards: {{ deck.cardsCount }}</span>
            <span class="stat">Date of last repetition: <br/>{{ deck.lastRepetition }}</span>
          </div>
        </div>

        <!-- Add Deck CTA -->
        <div class="add-deck-container">
          <span class="make-more-text">Make more!</span>
          <router-link to="/decks/create" class="add-btn">
            +
          </router-link>
        </div>

      </div>
    </main>

  </div>
</template>


<style scoped>
.dashboard-container {
  min-height: 100vh;
  padding: 2rem 4rem;
  display: flex;
  flex-direction: column;
}

@media (max-width: 768px) {
  .dashboard-container {
    padding: 1rem 2rem;
  }
}

/* --- Header --- */
.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4rem;
  gap: 2rem;
}

.search-bar {
  flex: 1;
  max-width: 600px;
  position: relative;
}

.search-input {
  width: 100%;
  padding: 0.8rem 1rem 0.8rem 2.5rem;
  border-radius: 30px;
  border: 1px solid #CCCCCC;
}

.search-icon {
  position: absolute;
  left: 12px;
  top: 50%;
  transform: translateY(-50%);
  opacity: 0.5;
  font-size: 1.1rem;
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-wrap: wrap;
  }
  .search-bar {
    order: 3;
    width: 100%;
    max-width: 100%;
  }
}

/* --- Main Content --- */
.dashboard-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  animation: fadeIn 0.4s ease-out forwards;
}

.decks-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 2rem;
  width: 100%;
  max-width: 1200px;
  justify-content: center;
}

.deck-card {
  width: 260px;
  min-height: 380px;
  background-color: var(--color-primary);
  border-radius: 16px;
  padding: 1.5rem;
  color: #FFFFFF;
  box-shadow: 0 8px 20px rgba(140, 82, 255, 0.4);
  display: flex;
  flex-direction: column;
  transition: transform 0.3s ease;
  position: relative;
  text-align: center;
}

.deck-card:hover {
  transform: translateY(-5px);
}

.deck-actions {
  position: absolute;
  top: 1.2rem;
  right: 1.2rem;
  display: flex;
  gap: 0.5rem;
}

.icon-btn {
  color: #FFFFFF;
  opacity: 0.6;
  width: 32px;
  height: 32px;
  display: flex;
  justify-content: center;
  align-items: center;
  border-radius: 50%;
  transition: all 0.2s ease;
  background-color: rgba(255,255,255,0.1);
}

.icon-btn:hover {
  opacity: 1;
  background-color: rgba(255,255,255,0.25);
  transform: scale(1.1);
}

.play-btn svg {
  margin-left: 3px; /* visual center for play icon */
}

.deck-name {
  font-family: 'Inter', sans-serif;
  font-size: 1.25rem;
  font-weight: 700;
  margin-top: 1rem;
  margin-bottom: 2rem;
  line-height: 1.2;
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

.deck-footer {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
  margin-top: 1.5rem;
  font-family: 'Inter', sans-serif;
  font-size: 0.85rem;
  opacity: 0.85;
}

/* Add CTA */
.add-deck-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 260px;
  min-height: 380px;
  gap: 1.5rem;
}

.make-more-text {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 2rem;
  color: var(--color-text);
  font-weight: 700;
}

.add-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 1px solid var(--color-text);
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 2rem;
  color: var(--color-text);
  text-decoration: none;
  transition: all 0.3s ease;
  background-color: transparent;
}

.add-btn:hover {
  background-color: var(--color-text);
  color: white;
  transform: scale(1.1);
}
</style>
