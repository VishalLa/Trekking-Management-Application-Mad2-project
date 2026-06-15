<template>
  <div class="staff-layout">
    <div class="layout-body">
      
      <div class="dashboard-header">
        <AppTopbar :title="currentTitle" />
        
        <div class="header-controls">
          <button 
            v-if="activeRoute === 'treks'" 
            class="control-btn btn-profile" 
            @click="$router.push('/staff/profile')"
          >
            🧑 My Profile
          </button>
          <button 
            v-else 
            class="control-btn btn-profile" 
            @click="$router.push('/staff/treks')"
          >
            🏔️ View Treks
          </button>
          
          <button class="control-btn btn-logout" @click="handleLogout">
            🚪 Logout
          </button>
        </div>
      </div>

      <main class="layout-content">
        <router-view />
      </main>
    </div>
  </div>
</template>

<script>
import AppTopbar from '@/components/shared/AppTopbar.vue'

export default {
  name: 'StaffDashboard',
  components: { AppTopbar },

  computed: {
    activeRoute() {
      return this.$route.path.split('/')[2] || 'treks'
    },
    
    currentTitle() {
      if (this.activeRoute === 'treks') return 'My Assigned Treks'
      if (this.activeRoute === 'profile') return 'My Profile'
      return 'Staff Dashboard'
    }
  },

  methods: {
    handleLogout() {
      localStorage.removeItem('tma_token')
      localStorage.removeItem('tma_role')
      localStorage.removeItem('user_id')
      this.$router.push('/')
    }
  },

  mounted() {
    const token = localStorage.getItem('tma_token')
    const role = localStorage.getItem('tma_role')

    if (!token || role !== 'STAFF') {
      this.$router.push('/')
    }
  }
}
</script>

<style scoped>
.staff-layout {
  display: flex;
  min-height: 100vh;
  background-color: #f4f5f7;
}

.layout-body {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0; 
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: #ffffff;
  padding-right: 24px;
  border-bottom: 1px solid #dde1e7;
}

.dashboard-header :deep(.topbar) {
  border-bottom: none !important;
}

.header-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.control-btn {
  padding: 6px 14px;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 13px;
  font-weight: 500;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.15s ease;
}

.btn-profile {
  background: #ffffff;
  border: 1px solid #dde1e7;
  color: #374151;
}
.btn-profile:hover {
  background: #f4f5f7;
  border-color: #cdd3dc;
}

.btn-logout {
  background: #fff5f5;
  border: 1px solid #fecaca;
  color: #dc2626;
}
.btn-logout:hover {
  background: #fee2e2;
  border-color: #fca5a5;
}

.layout-content {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}
</style>
