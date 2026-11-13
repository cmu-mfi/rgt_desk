<script setup>
import PanelGrid from '../components/PanelGrid.vue';
import panelsConfig from '../config/panels.json';

const tab = panelsConfig.tabs.space_panda;
</script>

<template>
  <PanelGrid :panels="tab.panels" :columns="tab.columns" />
</template>
