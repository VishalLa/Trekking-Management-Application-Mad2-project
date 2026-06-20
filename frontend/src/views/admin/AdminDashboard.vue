<template>
  <div class="admin-layout">
    
    <AppSidebar
      :nav-items="navItems"
      :active="activeRoute"
      :role="ADMIN"
      @navigate="handleNavigate"
      @logout="handleLogout"
    />

    <div class="layout-body">
      <AppTopbar :title="currentTitle" />
      
      <main class="layout-content">
        <router-view />
      </main>
    </div>

  </div>
</template>

<script>
import AppSidebar from '@/components/shared/AppSidebar.vue'
import AppTopbar  from '@/components/shared/AppTopbar.vue'

export default {
  name: 'AdminDashboard',
  components: { AppSidebar, AppTopbar },

  data() {
    return {
      navItems: [
        { id: 'staff',   label: 'Staff list',   route: '/dashboard/staff'   },
        { id: 'users',   label: 'User list',    route: '/dashboard/users'   },
        { id: 'treks',   label: 'Trek list',    route: '/dashboard/treks'   },
        { id: 'reports', label: 'Reports',      route: '/dashboard/reports' },
      ]
    }
  },

  computed: {
    activeRoute() {
      return this.$route.path.split('/')[2] || 'staff'
    },
    currentTitle() {
      return this.navItems.find(n => n.id === this.activeRoute)?.label || 'Admin Dashboard'
    }
  },

  methods: {
    handleNavigate(route) {
      this.$router.push(route)
    },
    handleLogout() {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_role')
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.admin-layout {
  display: flex;
  height: 100vh;
  overflow: hidden;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 14px;
  color: #121619;
  background: #f4f5f7;
}

.layout-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-width: 0;
}

.layout-content {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

@media (max-width: 768px) {
  .layout-content { padding: 16px; }
}
</style>

