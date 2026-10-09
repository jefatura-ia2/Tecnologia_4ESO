import { createApp } from 'vue'
import { createRouter, createWebHashHistory } from 'vue-router'
import App from './App.vue'
import { session } from './lib/api.js'
import './styles.css'

import LoginView from './views/LoginView.vue'
import MissionsView from './views/MissionsView.vue'
import SectionView from './views/SectionView.vue'
import CalendarView from './views/CalendarView.vue'
import HardwareView from './views/HardwareView.vue'
import RecursosView from './views/RecursosView.vue'
import TeacherView from './views/TeacherView.vue'
import TeacherStudentView from './views/TeacherStudentView.vue'

const routes = [
  { path: '/login', component: LoginView, meta: { public: true } },
  { path: '/', component: MissionsView },
  { path: '/seccion/:id', component: SectionView, props: true },
  { path: '/calendario', component: CalendarView },
  { path: '/placas', component: HardwareView },
  { path: '/recursos', component: RecursosView },
  { path: '/profesor', component: TeacherView, meta: { teacher: true } },
  { path: '/profesor/alumno/:id', component: TeacherStudentView, props: true, meta: { teacher: true } },
  { path: '/:pathMatch(.*)*', redirect: '/' },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to) => {
  if (!to.meta.public && !session.token) return '/login'
  if (to.meta.teacher && session.user?.role !== 'teacher') return '/'
  if (to.path === '/login' && session.token) return session.user?.role === 'teacher' ? '/profesor' : '/'
})

createApp(App).use(router).mount('#app')
