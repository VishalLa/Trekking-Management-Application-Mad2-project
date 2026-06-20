import { createRouter, createWebHistory } from 'vue-router'

import LoginPage from '../views/auth/LoginPage.vue'
import RegisterPage from '../views/auth/RegisterPage.vue'
import ResetPasswordPage from '../views/auth/ResetPasswordPage.vue'
import EmailVerifyPage from '../views/auth/EmailVerifyPage.vue'

import AdminDashboard from '../views/admin/AdminDashboard.vue'
import StaffDashboard from '../views/staff/StaffDashboard.vue'
import TrekkerDashboard from '../views/user/TrekkerDashboard.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/', 
      name: 'login',
      component: LoginPage
    },
    {
      path: '/register',
      name: 'register',
      component: RegisterPage
    },
    {
      path: '/reset-password',
      name: 'reset-password',
      component: ResetPasswordPage
    },
    {
      path: '/verify-email',
      name: 'verify-email',
      component: EmailVerifyPage
    }, 

    {
      path: '/dashboard',
      component: AdminDashboard,
      redirect: "/dashboard/staff",

      children: [
        {
          path: "staff",
          name: "admin-staff",
          component: () => import('@/views/admin/StaffList.vue') 
        },
        { 
          path: 'users',   
          name: 'admin-users',
          component: () => import('@/views/admin/UserList.vue')    
        },
        { 
          path: 'treks',   
          name: 'admin-treks',
          component: () => import('@/views/admin/TrekList.vue')    
        },
        { 
          path: 'reports', 
          name: 'admin-reports',
          component: () => import('@/views/admin/Report.vue')  
        }
      ]
    },
    {
      path: '/staff',
      component: StaffDashboard,
      redirect: '/staff/treks',

      children: [
        {
          path: 'treks',
          name: 'staff-treks',
          component: () => import('@/views/staff/TrekList.vue')
        },
        {
          path: 'profile',
          name: 'staff-profile',
          component: () => import('@/components/shared/UserProfile.vue'),
          props: { role: 'STAFF' }
        }
      ]
    },
    {
      path: '/trekker', 
      component: TrekkerDashboard,
      // redirect: '/trekker/treks',

      children: [
        {
          path: 'treks',
          name: 'trekker-treks',
          component: () => import('@/views/user/TrekList.vue')
        },
        {
          path: 'booked-trek-list',
          name: 'booked-trek-list',
          computed: () => import('@/views/user/BookedTrekList.vue')
        },
        {
          path: 'profile',
          name: 'trekker-profile',
          component: () => import('@/components/shared/UserProfile.vue'),
          props: { role: 'TREKKER' }
        }
      ]
    }
  ]
})

export default router

