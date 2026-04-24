import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '../views/HomeView.vue'
import SignupView from '../views/SignupView.vue'
import LoginView from '../views/LoginView.vue'
import CabinetView from '../views/CabinetView.vue'
import ProgressView from '../views/ProgressView.vue'
import PersonalInfoView from '../views/PersonalInfoView.vue'
import TwoFactorAuthView from '../views/TwoFactorAuthView.vue'
import DashboardView from '../views/DashboardView.vue'
import CreateDeckView from '../views/CreateDeckView.vue'
import ManageDeckView from '../views/ManageDeckView.vue'
import StudyView from '../views/StudyView.vue'
import StudySuccessView from '../views/StudySuccessView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView
    },
    {
      path: '/signup',
      name: 'signup',
      component: SignupView
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView
    },
    {
      path: '/cabinet',
      name: 'cabinet',
      component: CabinetView
    },
    { path: '/cabinet/progress', name: 'progress', component: ProgressView },
    { path: '/cabinet/personal-info', name: 'personal-info', component: PersonalInfoView },
    { path: '/cabinet/2fa', name: 'two-factor-auth', component: TwoFactorAuthView },
    { path: '/dashboard', name: 'dashboard', component: DashboardView },
    { path: '/decks/create', name: 'create-deck', component: CreateDeckView },
    { path: '/deck/:id/manage', name: 'manage-deck', component: ManageDeckView, props: true },
    { path: '/deck/:id/study', name: 'study-deck', component: StudyView, props: true },
    { path: '/deck/:id/success', name: 'study-success', component: StudySuccessView, props: true }
  ]
})

export default router
