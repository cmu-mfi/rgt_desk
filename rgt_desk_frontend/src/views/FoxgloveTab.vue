<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { RouterLink } from 'vue-router';
import { FoxgloveViewer } from '@foxglove/embed';

const settingsKey = 'rgt-desk.foxglove';
const secureContext = window.isSecureContext;
const defaultUrl = `${window.location.protocol === 'https:' ? 'wss' : 'ws'}://${window.location.hostname}:8765`;
let saved = {};
try {
  saved = JSON.parse(localStorage.getItem(settingsKey) || '{}') || {};
} catch {
  // Storage may be disabled, or settings may have been edited outside the app.
}
const bridgeUrl = ref(typeof saved.bridgeUrl === 'string' ? saved.bridgeUrl : import.meta.env.VITE_FOXGLOVE_BRIDGE_URL || defaultUrl);
const orgSlug = ref(typeof saved.orgSlug === 'string' ? saved.orgSlug : import.meta.env.VITE_FOXGLOVE_ORG_SLUG || '');
const container = ref(null);
const status = ref('Viewer not loaded');
const error = ref('');
let viewer;

// Keep the local robot connection in RGT Desk's browser context.
function createTransport({ url, protocols, onOpen, onMessage, onError, onClose }) {
  const socket = new WebSocket(url, [...protocols]);
  socket.binaryType = 'arraybuffer';
  status.value = 'Connecting to bridge…';
  socket.onopen = () => {
    error.value = '';
    status.value = 'Bridge connected';
    onOpen(socket.protocol);
  };
  socket.onmessage = event => onMessage(event.data);
  socket.onerror = () => {
    error.value = 'Unable to reach the bridge. Check its address, TLS settings, and that Foxglove Bridge is running.';
    onError(new Error(error.value));
  };
  socket.onclose = event => {
    status.value = 'Bridge disconnected';
    onClose({ code: event.code, reason: event.reason, wasClean: event.wasClean });
  };
  return {
    send: frame => socket.send(frame),
    close: () => {
      socket.onopen = socket.onmessage = socket.onerror = socket.onclose = null;
      socket.close();
    },
  };
}

function openViewer() {
  error.value = '';
  if (!secureContext) return;
  let url;
  try {
    url = new URL(bridgeUrl.value.trim());
    if (!['ws:', 'wss:'].includes(url.protocol) || url.username || url.password || url.hash) throw new Error();
  } catch {
    error.value = 'Enter a ws:// or wss:// bridge URL without credentials or a fragment.';
    return;
  }
  if (window.location.protocol === 'https:' && url.protocol !== 'wss:') {
    error.value = 'Use a wss:// bridge endpoint when RGT Desk is served over HTTPS.';
    return;
  }
  bridgeUrl.value = url.href;
  orgSlug.value = orgSlug.value.trim();
  try {
    localStorage.setItem(settingsKey, JSON.stringify({ bridgeUrl: bridgeUrl.value, orgSlug: orgSlug.value }));
  } catch {
    // The viewer still works when browser storage is unavailable.
  }
  viewer?.destroy();
  status.value = 'Loading viewer · sign in to Foxglove';
  try {
    viewer = new FoxgloveViewer({
      parent: container.value,
      orgSlug: orgSlug.value || undefined,
      colorScheme: 'dark',
      initialLayoutParams: { storageKey: 'rgt-desk' },
    });
    const currentViewer = viewer;
    currentViewer.addEventListener('ready', () => {
      status.value = 'Viewer ready';
      const source = { type: 'live', protocol: 'foxglove-websocket', url: url.href };
      if (currentViewer.getCapabilities().parentOwnedLiveTransport === 'available') {
        source.transport = createTransport;
      } else if (url.protocol === 'ws:') {
        error.value = 'This viewer cannot use the local bridge transport. Use a wss:// endpoint or check your Foxglove embedding access.';
        return;
      }
      currentViewer.setDataSource(source);
    });
    currentViewer.addEventListener('error', event => {
      error.value = String(event.detail || 'Foxglove could not load. Check your sign-in and embedding access.');
    });
  } catch (cause) {
    viewer?.destroy();
    viewer = undefined;
    status.value = 'Viewer unavailable';
    error.value = cause.message || 'Unable to initialize Foxglove. Try opening the viewer again.';
  }
}

onMounted(openViewer);
onUnmounted(() => viewer?.destroy());
</script>

<template>
  <section class="foxglove-tab" aria-labelledby="foxglove-title">
    <div class="panel-toolbar">
      <h1 id="foxglove-title">Foxglove</h1>
      <span class="viewer-status" role="status">{{ status }}</span>
    </div>
    <form class="viewer-settings" @submit.prevent="openViewer">
      <label class="bridge-field">Bridge URL
        <input v-model="bridgeUrl" class="field" type="url" required spellcheck="false" placeholder="ws://localhost:8765" />
      </label>
      <label>Organization (optional)
        <input v-model="orgSlug" class="field" type="text" spellcheck="false" placeholder="Choose after signing in" />
      </label>
      <button class="action-btn" type="submit" :disabled="!secureContext">Open viewer</button>
    </form>
    <p class="viewer-note">Start <RouterLink to="/main">Foxglove Bridge on Main</RouterLink>, then sign in with your embedding-enabled Foxglove account. Connection settings and layout changes are saved in this browser when storage is available.</p>
    <p v-if="!secureContext" class="connection-banner" role="alert">Foxglove requires HTTPS or localhost. Open RGT Desk at localhost on the robot host, or serve it over HTTPS with a secure wss:// bridge endpoint for LAN access.</p>
    <p v-if="error" class="viewer-error" role="alert">{{ error }}</p>
    <div v-show="secureContext" ref="container" class="foxglove-frame" aria-label="Foxglove viewer" />
  </section>
</template>

<style scoped>
.foxglove-tab { display: flex; flex-direction: column; gap: 12px; }
.panel-toolbar { margin-bottom: 0; }
.viewer-status { color: #a9b0bb; font-size: 12px; }
.viewer-settings { display: flex; flex-wrap: wrap; align-items: end; gap: 12px; padding: 14px; border: 1px solid #303845; border-radius: 8px; background: #111317; }
.viewer-settings label { display: flex; flex: 1 1 200px; flex-direction: column; gap: 7px; color: #bec8d4; font-size: 12px; }
.viewer-settings .bridge-field { flex-grow: 2; }
.viewer-settings .field { max-width: none; }
.viewer-note { margin: 0; color: #a9b0bb; font-size: 12px; line-height: 1.6; }
.viewer-note a { color: var(--color-accent-text); text-decoration: underline; }
.viewer-error { margin: 0; color: #f3a1a1; font-size: 12px; line-height: 1.6; overflow-wrap: anywhere; }
.foxglove-frame { height: calc(100dvh - 280px); min-height: 480px; overflow: hidden; border: 1px solid #303845; border-radius: 8px; background: #111317; }
.foxglove-frame :deep(iframe) { display: block; }
@media (max-width: 1100px) {
  .foxglove-frame { height: 70dvh; }
}
</style>
