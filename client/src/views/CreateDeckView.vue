<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()

const deckName = ref('')
const deckDescription = ref('')

const cards = ref([
  { id: Date.now(), question: '', isCorrect: true },
  { id: Date.now() + 1, question: '', isCorrect: false },
  { id: Date.now() + 2, question: '', isCorrect: true }
])

const addCard = () => {
  cards.value.push({
    id: Date.now(),
    question: '',
    isCorrect: true
  })
}

const removeCard = (index) => {
  cards.value.splice(index, 1)
}

const saveDeck = () => {
  if (!deckName.value) {
    alert("Please enter a deck name.")
    return
  }
  alert(`Deck "${deckName.value}" saved with ${cards.value.length} cards!`)
  router.push('/dashboard')
}
</script>

<template>
  <div class="page-container">
    
    <!-- Navbar (same as Dashboard but without search) -->
    <header class="deck-header">
      <router-link to="/dashboard" class="logo">
        <div class="mascot-placeholder">
          <span class="owl-icon">🎓</span>
        </div>
        <div class="logo-text">
          <h1 class="logo-title">STEP BY STEP</h1>
          <span class="logo-subtitle">Learn with Flashcards</span>
        </div>
      </router-link>

      <router-link to="/cabinet" class="profile-icon" title="My Cabinet">
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" xmlns="http://www.w3.org/2000/svg">
          <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
          <circle cx="12" cy="7" r="4"></circle>
        </svg>
      </router-link>
    </header>

    <main class="deck-form">
      <h1 class="page-title">Create your deck</h1>

      <!-- Editor Layout (Meta + Cards & Sidebar) -->
      <div class="editor-layout">
        
        <!-- Main Column (Centered content) -->
        <div class="main-column">
          <!-- Deck Meta Info -->
          <div class="deck-meta">
            <input 
              type="text" 
              v-model="deckName" 
              placeholder="Deck name" 
              class="deck-name-input"
            />
            <input 
              type="text" 
              v-model="deckDescription" 
              placeholder="Description" 
              class="deck-desc-input"
            />
          </div>

          <!-- Cards List -->
          <div class="cards-list">
            <transition-group name="list">
              <div 
                class="card-item-wrapper" 
                v-for="(card, index) in cards" 
                :key="card.id"
              >
                <div class="card-box">
                  <button class="delete-card-btn" @click="removeCard(index)" title="Remove card">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                      <path d="M3 6h18M19 6V20a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6h14zm-3 0V4a2 2 0 0 0-2-2h-4a2 2 0 0 0-2 2v2h8z" stroke="black" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
                    </svg>
                  </button>
                  
                  <div class="fields-row">
                    <div class="field-col">
                      <label>Question</label>
                      <textarea 
                        v-model="card.question" 
                        placeholder="Enter question" 
                        class="card-input"
                        rows="2"
                      ></textarea>
                    </div>
                    <div class="field-col toggle-col">
                      <label>Is this statement Correct or Wrong?</label>
                      <div class="answer-toggle">
                        <button 
                          class="toggle-btn" 
                          :class="{ 'active-correct': card.isCorrect === true }"
                          @click="card.isCorrect = true"
                        >Correct</button>
                        <button 
                          class="toggle-btn" 
                          :class="{ 'active-wrong': card.isCorrect === false }"
                          @click="card.isCorrect = false"
                        >Wrong</button>
                      </div>
                    </div>
                  </div>
                </div> <!-- /card-box -->
              </div> <!-- /card-item-wrapper -->
            </transition-group>
          </div> <!-- /cards-list -->
        </div> <!-- /main-column -->

        <!-- Sidebar Actions -->
        <div class="actions-sidebar">
          <div class="add-action" @click="addCard" title="Add new card">
            <button class="add-card-btn">
              <span class="plus-icon">+</span>
            </button>
            <span class="action-label">Add card</span>
          </div>

          <button class="btn btn-outline save-btn" @click="saveDeck">
            Save
          </button>
        </div>

      </div>
    </main>

  </div>
</template>


<style scoped>
.page-container {
  height: 100vh;
  overflow: hidden;
  padding: 2rem 4rem;
  display: flex;
  flex-direction: column;
  position: relative;
  align-items: center;
}

@media (max-width: 768px) {
  .page-container {
    height: auto;
    min-height: 100vh;
    overflow: visible;
    padding: 1rem 2rem;
  }
}

/* --- Header / Navbar --- */
.deck-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  width: 100%;
}

/* --- Main Form area --- */
.deck-form {
  display: flex;
  flex-direction: column;
  align-items: center;
  width: 100%;
  flex: 1;
  min-height: 0;
  animation: fadeIn 0.4s ease-out;
}

.page-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 2.2rem;
  color: var(--color-text);
  margin-bottom: 2rem;
  text-align: center;
}

/* --- Editor Layout (Main Col + Sidebar) --- */
.editor-layout {
  display: flex;
  width: 100%;
  max-width: 1100px;
  justify-content: center;
  align-items: stretch;
  gap: 4rem;
  flex: 1;
  min-height: 0;
}

.main-column {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  max-width: 800px; /* Force the grid to match */
  min-height: 0;
}

@media (max-width: 1024px) {
  .editor-layout {
    flex-direction: column;
    align-items: center;
  }
}

/* --- Deck Meta (Title & Desc) --- */
.deck-meta {
  display: flex;
  flex-direction: column;
  width: 100%;
  margin-bottom: 2.5rem;
  gap: 0.8rem;
}

.deck-name-input {
  width: 100%;
  font-family: var(--font-main), 'Playfair Display', serif;
  font-size: 3rem;
  text-align: center;
  padding: 1rem;
  border: 1px solid rgba(192, 132, 252, 0.4);
  background-color: rgba(255, 255, 255, 0.8);
  border-radius: 12px;
  color: var(--color-text);
  transition: all 0.3s ease;
  outline: none;
}

.deck-name-input:focus {
  border-color: var(--color-primary);
  background-color: #FFFFFF;
  box-shadow: 0 4px 15px rgba(140, 82, 255, 0.1);
}

.deck-desc-input {
  width: 100%;
  font-family: 'Inter', sans-serif;
  font-size: 1.1rem;
  text-align: left;
  padding: 1rem;
  border: 1px solid #E0E0E0;
  background-color: rgba(255, 255, 255, 0.6);
  border-radius: 8px;
  color: var(--color-text);
  outline: none;
  transition: all 0.3s ease;
}

.deck-desc-input:focus {
  background-color: #FFFFFF;
  border-color: #CCCCCC;
}

/* --- Cards List --- */
.cards-list {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2.5rem;
  width: 100%;
  overflow-y: auto;
  padding-right: 1rem;
  padding-bottom: 2rem;
}

@media (max-width: 768px) {
  .cards-list {
    overflow-y: visible;
  }
}

.card-item-wrapper {
  display: flex;
  align-items: stretch;
  gap: 2rem;
  width: 100%;
  transition: all 0.3s ease;
}

.list-enter-active, .list-leave-active {
  transition: all 0.4s ease;
}
.list-enter-from, .list-leave-to {
  opacity: 0;
  transform: translateY(20px);
}

.card-box {
  flex: 1;
  background-color: rgba(255, 255, 255, 0.9);
  border: 2px solid #C084FC; /* Brighter purple/blue border */
  border-radius: 32px;
  padding: 2rem 3rem;
  position: relative;
  box-shadow: 0 10px 25px rgba(0,0,0,0.03);
}

.card-item-wrapper:active .card-box, .card-item-wrapper:focus-within .card-box {
  border-color: #38BDF8; /* subtle active cyan effect per figma */
}

.delete-card-btn {
  position: absolute;
  top: 1.5rem;
  right: 1.5rem;
  background: none;
  border: none;
  cursor: pointer;
  opacity: 0.5;
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.delete-card-btn:hover {
  opacity: 1;
  transform: scale(1.1);
  color: var(--color-error);
}

.fields-row {
  display: flex;
  gap: 2rem;
  margin-top: 0.5rem;
}

@media (max-width: 768px) {
  .fields-row {
    flex-direction: column;
  }
}

.field-col {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.field-col label {
  font-size: 0.9rem;
  color: var(--color-text-light);
  font-family: 'Inter', sans-serif;
}

.card-input {
  width: 100%;
  border: 1px solid #CCCCCC;
  border-radius: 16px;
  padding: 1rem;
  font-family: 'Inter', sans-serif;
  font-size: 1rem;
  resize: vertical;
  background-color: #FAFAFA;
  transition: border-color 0.2s ease;
  outline: none;
}

.card-input:focus {
  border-color: var(--color-primary);
  background-color: #FFFFFF;
}

.toggle-col {
  justify-content: flex-end;
  padding-bottom: 0.2rem;
}

.answer-toggle {
  display: flex;
  background: #FAFAFA;
  border-radius: 16px;
  padding: 6px;
  border: 2px solid #E0E0E0;
  height: 70px;
}

.toggle-btn {
  flex: 1;
  padding: 0.8rem;
  border-radius: 12px;
  border: none;
  background: transparent;
  font-family: 'Inter', sans-serif;
  font-size: 1.2rem;
  font-weight: 600;
  cursor: pointer;
  color: var(--color-text-light);
  transition: all 0.3s ease;
}

.toggle-btn.active-correct {
  background-color: #22c55e; /* Green */
  color: white;
  box-shadow: 0 4px 15px rgba(34, 197, 94, 0.3);
}

.toggle-btn.active-wrong {
  background-color: #ef4444; /* Red */
  color: white;
  box-shadow: 0 4px 15px rgba(239, 68, 68, 0.3);
}

/* --- Sidebar Actions --- */
.actions-sidebar {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 5rem; /* Large gap between add and save button */
  min-width: 150px;
}

@media (max-width: 1024px) {
  .actions-sidebar {
    position: relative;
    top: 0;
    flex-direction: row;
    width: 100%;
    justify-content: space-between;
    margin-top: 2rem;
  }
}

.add-action {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  cursor: pointer;
}

.add-card-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: radial-gradient(circle at top left, rgba(232, 172, 255, 0.4), rgba(255, 230, 250, 0.8));
  display: flex;
  justify-content: center;
  align-items: center;
  color: var(--color-text);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  cursor: pointer;
}

.plus-icon {
  font-size: 3rem;
  font-weight: 300;
}

.add-action:hover .add-card-btn {
  transform: translateY(-5px) scale(1.05);
  box-shadow: 0 8px 25px rgba(232, 172, 255, 0.4);
}

.action-label {
  font-family: var(--font-main), serif;
  font-size: 1.2rem;
}

.save-btn {
  padding: 0.8rem 2.5rem;
  border-color: #38BDF8; /* Cyan outline */
  color: var(--color-text);
  font-size: 1.1rem;
  border-width: 1.5px;
  background-color: rgba(255, 255, 255, 0.5);
}

.save-btn:hover {
  background-color: #38BDF8;
  color: #FFFFFF;
}
</style>
