<template>
  <aside class="sidebar">
    
    <div class="sidebar-brand">
      <div class="brand-icon">
        <svg width="18" height="18" viewBox="0 0 20 20" fill="none">
          <path d="M2 18L6 8l3 5 3-8 4 13"
                stroke="#fff" stroke-width="1.8"
                stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
      <div class="brand-text">
        <span class="brand-title">Trek Management</span>
        <span class="brand-sub">System</span>
      </div>
    </div>

    <!-- Nav -->
    <nav class="sidebar-nav" role="navigation">
      <button
        v-for="item in navItems"
        :key="item.id"
        class="nav-item"
        :class="{ active: active === item.id }"
        :aria-current="active === item.id ? 'page' : undefined"
        @click="$emit('navigate', item.route)"
      >
        <span class="nav-dot" aria-hidden="true">-</span>
        {{ item.label }}
      </button>
    </nav>

    <div v-if="role === 'ADMIN'" class="sidebar-footer">
      <div class="admin-label">Admin</div>
      <button class="logout-btn" @click="$emit('logout')">Logout</button>
    </div>

  </aside>
</template>

<script>
export default {
  name: 'AppSidebar',
  props: {
    navItems: {
      type: Array,
      default: () => []
    },
    active: {
      type: String,
      default: ''
    },
    role: {
      type: String,
      default: 'TREKKER' 
    }
  },
  emits: ['navigate', 'logout']
}
</script>

<style scoped>
.sidebar {
  width: 200px;
  min-width: 200px;
  background: #ffffff;
  border-right: 1px solid #dde1e7;
  display: flex;
  flex-direction: column;
  font-family: 'IBM Plex Sans', sans-serif;
}

.sidebar-brand {
  padding: 20px 16px 16px;
  border-bottom: 1px solid #dde1e7;
  display: flex;
  align-items: center;
  gap: 10px;
}
.brand-icon {
  width: 32px;
  height: 32px;
  background: #1a6b42;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.brand-text {
  display: flex;
  flex-direction: column;
}
.brand-title {
  font-size: 13px;
  font-weight: 600;
  color: #121619;
  line-height: 1.3;
}
.brand-sub {
  font-size: 11.5px;
  color: #6b7280;
}

.sidebar-nav {
  flex: 1;
  padding: 14px 10px;
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 8px 10px;
  border: none;
  border-radius: 6px;
  background: none;
  font-family: inherit;
  font-size: 13.5px;
  color: #4b5563;
  cursor: pointer;
  text-align: left;
  transition: background 0.12s, color 0.12s;
}
.nav-item:hover  { background: #f4f5f7; color: #121619; }
.nav-item.active { background: #f0faf4; color: #1a6b42; font-weight: 500; }
.nav-dot         { color: #9ca3af; font-size: 16px; line-height: 1; }
.nav-item.active .nav-dot { color: #1a6b42; }

.sidebar-footer {
  padding: 14px 16px;
  border-top: 1px solid #dde1e7;
}
.admin-label {
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}
.logout-btn {
  background: none;
  border: none;
  font-family: inherit;
  font-size: 13px;
  color: #6b7280;
  cursor: pointer;
  padding: 0;
  transition: color 0.12s;
}
.logout-btn:hover { color: #dc2626; }

@media (max-width: 768px) {
  .sidebar { display: none; }
}
</style>
