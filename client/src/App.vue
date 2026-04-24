<script setup>
import { ref, watch, onMounted, onBeforeUnmount } from 'vue'
import { RouterView, useRoute } from 'vue-router'

const route = useRoute()

// Base configs for our 5 blobs
const baseBlobs = [
  { color1: 'rgba(255, 182, 193, 1)', color2: 'rgba(200, 162, 200, 0.5)' }, // Pinkish
  { color1: 'rgba(230, 255, 200, 1)', color2: 'rgba(255, 255, 150, 0.5)' }, // Yellow/Greenish
  { color1: 'rgba(192, 132, 252, 0.8)', color2: 'rgba(100, 200, 250, 0.4)' }, // Purple/Blueish
  { color1: 'rgba(255, 200, 100, 0.8)', color2: 'rgba(255, 100, 100, 0.4)' }, // Orange/Reddish
  { color1: 'rgba(150, 250, 250, 0.8)', color2: 'rgba(50, 150, 255, 0.4)' }  // Cyan/Deep Blue
]

const blobs = ref([])

// Algorithm to calculate sizes and placements WITHOUT overlapping
const generateRandomLayout = () => {
  if (typeof window === 'undefined') return;

  const w = window.innerWidth;
  const h = window.innerHeight;
  const clearance = 80; // Minimum gap between the edges of the blobs (accounts for blur)

  let newBlobs = [];

  for (let i = 0; i < baseBlobs.length; i++) {
    let placed = false;
    let attempts = 0;
    
    while (!placed && attempts < 150) {
      // Pick a random size. Smaller range so they have room to breathe
      let size = Math.floor(Math.random() * 200) + 250; // 250px - 450px
      
      // Coordinates can spill slightly off screen (-100 to w+100)
      let x = Math.floor(Math.random() * (w + 200)) - 100;
      let y = Math.floor(Math.random() * (h + 200)) - 100;

      // Check collision with already placed circles
      let collision = false;
      for (let j = 0; j < newBlobs.length; j++) {
        const other = newBlobs[j];
        const dx = x - other.left;
        const dy = y - other.top;
        const distance = Math.sqrt(dx*dx + dy*dy);
        
        // The distance between centers must be greater than both radiuses + clearance
        const minDistanceAllowed = (size / 2) + (other.size / 2) + clearance;
        
        if (distance < minDistanceAllowed) {
          collision = true;
          break; // Try different random cords
        }
      }

      if (!collision) {
        newBlobs.push({
          id: i,
          ...baseBlobs[i],
          size: size,
          top: y,
          left: x
        });
        placed = true;
      }
      attempts++;
    }
    
    // Strict fallback: if screen is too crowded and we ran out of attempts, push a tiny invisible-ish blob
    if (!placed) {
      newBlobs.push({
         id: i,
         ...baseBlobs[i],
         size: 100,
         top: Math.random() * h,
         left: Math.random() * w
      })
    }
  }

  blobs.value = newBlobs;
}

// Watch for route changes to trigger the animation
watch(() => route.path, () => {
  generateRandomLayout()
})

// Initial layout on load
let resizeTimeout;
const handleResize = () => {
  clearTimeout(resizeTimeout);
  resizeTimeout = setTimeout(generateRandomLayout, 300);
}

onMounted(() => {
  generateRandomLayout()
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<template>
  <div class="app-wrapper">
    <!-- Dynamic animated backgrounds -->
    <div class="blobs-container">
      <div 
        v-for="blob in blobs" 
        :key="blob.id" 
        class="blob-item"
        :style="{
          width: blob.size + 'px',
          height: blob.size + 'px',
          top: blob.top + 'px',
          left: blob.left + 'px',
          background: `radial-gradient(circle, ${blob.color1} 0%, ${blob.color2} 100%)`
        }"
      ></div>
    </div>
    
    <!-- Main Application Content -->
    <div class="content-wrapper">
      <RouterView />
    </div>
  </div>
</template>


<style scoped>
.app-wrapper {
  position: relative;
  min-height: 100vh;
  width: 100%;
}

.blobs-container {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.blob-item {
  position: absolute;
  border-radius: 50%;
  filter: blur(60px);
  opacity: 0.6;
  transform: translate(-50%, -50%);
  transition: all 2.5s cubic-bezier(0.25, 1, 0.5, 1);
}

.content-wrapper {
  position: relative;
  z-index: 1;
  width: 100%;
  min-height: 100vh;
  animation: fadeIn 0.8s ease-out forwards;
}
</style>
