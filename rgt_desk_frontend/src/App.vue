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
  <div class="h-dvh w-full flex flex-col bg-console text-zinc-200 font-sans">
    <header class="flex items-center justify-between gap-3 px-4 py-2.5 bg-console border-b border-hairline shrink-0">
      <div class="flex items-center gap-2.5 min-w-0">
        <span class="led w-2 h-2 bg-accent animate-pulse"></span>
        <h1 class="font-mono text-sm font-semibold tracking-[0.25em] text-zinc-100 whitespace-nowrap">RGT DESK</h1>
      </div>

      <nav class="flex flex-nowrap bg-panel border border-hairline p-px text-zinc-500">
        <RouterLink
          to="/main"
          class="seg-link"
          exact-active-class="bg-zinc-100 text-zinc-950"
        >
          <LayoutDashboard :size="14" /> <span class="hidden sm:inline">Main</span>
        </RouterLink>

        <RouterLink
          to="/sensors"
          class="seg-link"
          exact-active-class="bg-zinc-100 text-zinc-950"
        >
          <Activity :size="14" /> <span class="hidden sm:inline">Sensors</span>
        </RouterLink>

        <RouterLink
          to="/utilities"
          class="seg-link"
          exact-active-class="bg-zinc-100 text-zinc-950"
        >
          <Toolbox :size="14" /> <span class="hidden sm:inline">Utilities</span>
        </RouterLink>

        <RouterLink
          to="/space_panda"
          class="seg-link"
          exact-active-class="bg-zinc-100 text-zinc-950"
        >
          <Panda :size="14" /> <span class="hidden sm:inline">Space Panda</span>
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

.seg-link {
  @apply flex items-center justify-center gap-1.5 px-2.5 py-2 sm:px-4 sm:py-1.5 font-mono text-[12px] font-medium uppercase tracking-wider transition-colors duration-150;
}

.seg-link:hover {
  @apply text-zinc-200;
}

/* Tab Transition Animation */
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.15s ease;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>
