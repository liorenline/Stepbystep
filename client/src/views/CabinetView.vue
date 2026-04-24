<script setup>
</script>

<template>
  <div class="cabinet-container">
    
    <!-- Top Bar / Logo — click goes back to Dashboard -->
    <header class="cabinet-header">
      <router-link to="/dashboard" class="logo cabinet-logo">
        <div class="mascot-placeholder cabinet-mascot">
          <!-- Hat — visible by default, hidden on hover -->
          <span class="owl-icon cabinet-owl">🎓</span>
          <!-- Back arrow PNG — hidden by default, appears on hover -->
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

    <!-- Main Content -->
    <main class="cabinet-content">
      <h1 class="cabinet-title">My cabinet</h1>
      
      <div class="cabinet-menu">
        <router-link to="/cabinet/progress" class="btn btn-outline menu-btn">My progress</router-link>
        <router-link to="/cabinet/personal-info" class="btn btn-outline menu-btn">Personal Information</router-link>
        <router-link to="/cabinet/2fa" class="btn btn-outline menu-btn">Try Two-factor authentication method</router-link>
      </div>
    </main>

  </div>
</template>


<style scoped>
.cabinet-container {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  padding: 2rem;
}

/* --- Cabinet-specific logo hover: unrotate + swap icon --- */
.cabinet-mascot {
  position: relative;
  overflow: hidden;
}

/* Both icons sit inside the mascot, using absolute positioning */
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
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%) scale(0.6);
  transition: opacity 0.25s ease, transform 0.25s ease;
  display: flex;
  align-items: center;
  justify-content: center;
}

.arrow-img {
  width: 26px;
  height: 26px;
  /* Invert dark PNG to white so it's visible on the purple background */
  filter: brightness(0) invert(1);
  display: block;
}

/* On hover: mascot unrotates and scales, hat fades out, arrow fades in */
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

/* Main Content Styles */
.cabinet-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  margin-top: 2rem;
  animation: fadeIn 0.6s ease-out forwards;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(15px); }
  to { opacity: 1; transform: translateY(0); }
}

.cabinet-title {
  font-family: var(--font-main), 'Playfair Display', serif;
  color: var(--color-text);
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 3rem;
}

.cabinet-menu {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  width: 100%;
  max-width: 450px;
}

.menu-btn {
  padding: 1.2rem 1.5rem;
  font-size: 1.15rem;
  background-color: rgba(255, 255, 255, 0.6); 
  backdrop-filter: blur(5px);
  border: 1px solid var(--color-secondary);
  font-family: 'Inter', 'Montserrat', sans-serif;
  font-weight: 500;
  color: var(--color-text);
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.02);
  border-radius: 50px;
}

.menu-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 12px rgba(192, 163, 255, 0.3);
  border-color: var(--color-primary);
  background-color: rgba(255, 255, 255, 0.9);
}
</style>
