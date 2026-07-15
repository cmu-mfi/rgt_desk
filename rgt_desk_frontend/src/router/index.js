import { createRouter, createWebHistory } from 'vue-router';
import MainTab from '../views/MainTab.vue';
import UtilitiesTab from '../views/UtilitiesTab.vue';
import SensorsTab from '../views/SensorsTab.vue';
import SpacePandaTab from '../views/SpacePandaTab.vue';

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    { path: '/', redirect: '/main' },
    { path: '/main', name: 'main', component: MainTab },
    { path: '/sensors', name: 'sensors', component: SensorsTab },
    { path: '/utilities', name: 'utilities', component: UtilitiesTab },
    { path: '/space_panda', name: 'space_panda', component: SpacePandaTab },
  ]
});

export default router;
