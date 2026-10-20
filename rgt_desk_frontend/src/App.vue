<script setup>
import { onMounted, onUnmounted } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import { useStore } from './stores/store';
import { LayoutDashboard, Activity, Toolbox, Panda } from '@lucide/vue';

const store = useStore();

onMounted(() => {
  store.startPolling();
});

onUnmounted(() => {
  store.stopPolling();
});
</script>

<template>
  <div class="h-dvh w-full flex flex-col bg-black text-gray-200 font-sans">
    <header class="flex items-center justify-between px-4 py-2 bg-black border-b-1 border-gray-700 backdrop-blur-md">
      <div class="flex items-center gap-3">
        <div class="w-3 h-3 rounded-full bg-green-500 animate-pulse"></div>
        <h1 class="text-lg sm:text-xl font-bold tracking-tight">RGT Desk</h1>
      </div>
      
      <nav class="flex flex-nowrap bg-black p-1 rounded-xl border border-gray-800 text-gray-500">
        <RouterLink 
          to="/main" 
          class="nav-link"
          exact-active-class="bg-gray-700 text-white"
        >
          <LayoutDashboard :size="18" /> <span class="hidden sm:inline">Main</span>
        </RouterLink>

        <RouterLink 
          to="/sensors" 
          class="nav-link"
          exact-active-class="bg-gray-700 text-white"
        >
          <Activity :size="18" /> <span class="hidden sm:inline">Sensors</span>
        </RouterLink>
        
        <RouterLink 
          to="/utilities" 
          class="nav-link"
          exact-active-class="bg-gray-700 text-white"
        >
          <Toolbox :size="18" /> <span class="hidden sm:inline">Utilities</span>
        </RouterLink>

        <RouterLink 
          to="/space_panda" 
          class="nav-link"
          exact-active-class="bg-gray-700 text-white"
        >
          <Panda :size="18" /> <span class="hidden sm:inline">Space Panda</span>
        </RouterLink>
      </nav>
    </header>

    <main class="flex-1 min-h-0 overflow-y-auto md:overflow-hidden relative">
      <router-view v-slot="{ Component, route }"> 
        <transition name="fade" mode="out-in">
        <component :is="Component" :key="route.path" /> 
        </transition>
      </router-view>
    </main>
  </div>
</template>

<style scoped>
@reference "tailwindcss";

.RouterLink {
  @apply bg-red-500;
}

.nav-link {
  @apply flex items-center justify-center gap-2 px-3 py-2.5 sm:px-5 sm:py-2 rounded-lg transition-all duration-200 text-sm font-medium;
}

.nav-link:hover {
  @apply text-gray-50;
}

/* Tab Transition Animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from { opacity: 0; transform: translateY(10px); }
.fade-leave-to { opacity: 0; transform: translateY(-10px); }
</style>
