<script setup>
import { onMounted, onUnmounted } from 'vue';
import { RouterLink, RouterView } from 'vue-router';
import { useStore } from './stores/store';
import { Hexagon, LayoutDashboard, Monitor, Panda, Radio, Toolbox, Wrench } from '@lucide/vue';

const store = useStore();
const links = [
  { to: '/main', label: 'Main', icon: LayoutDashboard },
  { to: '/sensors', label: 'Sensors', icon: Radio },
  { to: '/tools', label: 'Tools', icon: Wrench },
  { to: '/foxglove', label: 'Foxglove', icon: Monitor },
  { to: '/utilities', label: 'Utilities', icon: Toolbox },
  { to: '/space_panda', label: 'Space Panda', icon: Panda },
];
onMounted(() => store.startPolling());
onUnmounted(() => store.stopPolling());
</script>

<template>
  <div class="desk-shell">
    <header class="app-header">
      <RouterLink to="/main" class="brand" aria-label="RGT Desk home">
        <Hexagon :size="23" :stroke-width="1.7" />
        <span>RGT <strong>Desk</strong></span>
      </RouterLink>
      <nav class="main-nav" aria-label="Main navigation">
        <RouterLink v-for="link in links" :key="link.to" :to="link.to" class="nav-link" exact-active-class="is-active">
          <component :is="link.icon" :size="17" :stroke-width="1.7" />
          <span>{{ link.label }}</span>
        </RouterLink>
      </nav>
      <div class="connection-state" role="status">
        <span class="status-dot" :class="store.connection" />
        <span>{{ store.connection === 'connected' ? 'Connected' : store.connection === 'connecting' ? 'Connecting…' : 'Disconnected' }}</span>
      </div>
    </header>
    <main id="main-content" class="workspace-main">
      <div v-if="store.connection === 'disconnected'" class="connection-banner" role="alert">
        <Radio :size="16" /><span>Backend disconnected. Status may be out of date. Reconnecting…</span>
      </div>
      <RouterView />
    </main>
  </div>
</template>
