import { createRouter, createWebHistory } from 'vue-router'
import HomeView from '@/views/HomeView.vue'
import AdminView from '@/views/AdminView.vue'
import LoginView from '@/views/LoginView.vue'
import StudentView from '@/views/StudentView.vue'
import BookMeetingView from '@/views/student/BookMeetingView.vue'
import TeamView from '@/views/TeamView.vue'
import store from '@/store'
//import BookVisitView from '@/views/BookVisitView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView,
      meta: { title: "VIC - Start" }
    },{
      path: '/creators',
      name: 'Creators',
      component: TeamView,
      meta: { title: "VIC - Creators" }
    },
    {
      path: '/login',
      name: 'login',
      component: LoginView,
      meta: { title: "VIC - Login" }
    },
    {
      path: '/admin',
      name: 'admin', 
      component: AdminView,
      meta: { title: "VIC - Admin",requiresAuth: true, requiresAdmin: true }
    },
    {
      path: '/student',
      name: 'student',
      component: StudentView,
      meta: { title: "VIC - Bokningar", requiresAuth: true, requiresAdmin: false }
    },
    {
      path: '/mote',
      name: 'boka-möte',
      component: BookMeetingView,
      props: {submenu: ""},
      meta: { title: "VIC - Möte" }
    },
    {
      path: '/mote/:id',
      name: 'boka-möte',
      component: StudentView,
      props: {startView: "manageMeeting", startSubmenu: ""},
      meta: { title: "VIC - Möte" }
    },
    // {
    //   path: '/studiebesok',
    //   name: 'boka-studiebesök',
    //   component: BookVisitView,
    //   meta: { title: "VIC - Studiebesök" }
    // },
    // {
    //   path: '/groups/:id',
    //   name: 'group',
    //   component: BookVisitView,
    //   props: true,
    //   meta: { title: "VIC - Studiebesök" }
    // },
  ]
})

// Navigation guard for authentication and permission check
router.beforeEach((to, from, next) => {
  document.title = to.meta.title || "VIC"
  const requiresAdmin = to.meta.requiresAdmin;  // Get required permission from route meta

  console.log("is authenticated", store.state.authenticated)

  if (to.meta.requiresAuth && !store.state.authenticated) {
    next('/login'); // Redirect to login if not logged in and route requires auth
  } else if (requiresAdmin && !store.state.user.admin) {
    next('/login'); // Redirect to unauthorized page if permission doesn't match
  } else {
    next(); // Proceed with navigation if all checks pass
  }
});

export default router
// route level code-splitting
// this generates a separate chunk (About.[hash].js) for this route
// which is lazy-loaded when the route is visited.
// component: () => import('../views/AboutView.vue')