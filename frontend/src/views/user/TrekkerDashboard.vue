<template>
  <div class="trekker-layout">
    
    <AppSidebar 
      :navItems="navItems" 
      :active="activeRoute" 
      @navigate="handleNavigate" 
      @logout="handleLogout" 
    />

    <div class="layout-body">
      
      <div class="dashboard-header">
        <AppTopbar :title="currentTitle" />
        
        <div class="header-controls">
          <button
            v-if="!isProfileRoute"
            class="control-btn btn-profile"
            @click="$router.push('/trekker/profile')" 
          >
            🧑 My Profile
          </button>
          
          <button 
            v-else 
            class="control-btn btn-profile" 
            @click="$router.push('/trekker/treks')"
          >
            🏔️ View Treks
          </button>

          <button class="control-btn btn-logout" @click="handleLogout">
            🚪 Logout
          </button>
        </div>
      </div>

      <div class="layout-content">
        <router-view></router-view>
      </div>

    </div>

  </div>
</template>

<script>
import AppTopbar from '@/components/shared/AppTopbar.vue'
import AppSidebar from '@/components/shared/AppSidebar.vue'

export default {
  name: 'TrekkerDashboard',
  components: { AppTopbar, AppSidebar },

  data() {
    return {
      navItems: [
        {
          id: 'treks', 
          label: 'Available Treks', 
          route: '/trekker/treks' 
        },
        { 
          id: 'booked-treks', 
          label: 'My Bookings', 
          route: '/trekker/booked-trek-list' 
        }
      ]
    }
  },

  computed: {
    isProfileRoute() {
      return this.$route.path.includes('profile');
    },

    activeRoute() {
      const path = this.$route.path;
      if (path.includes('booked-trek-list')) return 'booked-treks';
      return 'treks'; 
    },
    
    currentTitle() {
      if (this.isProfileRoute) return 'My Profile';
      if (this.activeRoute === 'booked-treks') return 'My Bookings';
      return 'Available Treks';
    }
  },

  methods: {
    handleNavigate(route) {
      this.$router.push(route);
    },

    handleLogout() {
      localStorage.removeItem('tma_token');
      localStorage.removeItem('user_id');
      localStorage.removeItem('role');
      this.$router.push('/');
    }
  }
}
</script>

<style scoped>
.trekker-layout {
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
