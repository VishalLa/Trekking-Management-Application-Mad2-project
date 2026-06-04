<template>
  <div>
    <div class="section-header">
      <h2 class="section-title">User List</h2>
      <SearchBar v-model="query" placeholder="Search by name or email…" />
    </div>

    <p v-if="loading" class="state-msg">Loading users…</p>

    <div v-else-if="error" class="state-error">
      {{ error }}
      <button @click="load" class="retry-link">Retry</button>
    </div>

    <p v-else-if="filtered.length === 0" class="state-msg">No users found.</p>

    <div v-else>
      <div v-for="user in filtered" :key="user.id" class="list-card">

        <div class="card-main">
          <div class="card-avatar">{{ initials(user) }}</div>
          <div class="card-body">
            <div class="card-name">{{ fullName(user) }}</div>
            <div class="card-meta">
              <span>{{ user.email }}</span>
              <span class="sep">·</span>
              <span>{{ user.phone_no }}</span>
              <span class="sep">·</span>
              <span>Joined {{ formatDate(user.date_created) }}</span>
            </div>
            <div class="card-meta" v-if="user.address">
              <span>{{ user.address }}</span>
            </div>
          </div>
        </div>

        <div class="card-actions">
          <StatusBadge :status="user.status" type="user" />
          <button
            class="action-btn"
            :class="user.status === 'ACTIVE' ? 'btn-danger' : 'btn-success'"
            @click="askToggle(user)"
          >
            {{ user.status === 'ACTIVE' ? 'Blacklist' : 'Unblacklist' }}
          </button>
        </div>

      </div>
    </div>

    <!-- Confirm Blacklist / Unblacklist -->
    <ConfirmModal
      :show="showConfirm"
      :title="confirmUser?.status === 'ACTIVE' ? 'Blacklist User' : 'Unblacklist User'"
      :message="confirmUser?.status === 'ACTIVE'
        ? `Blacklist ${fullName(confirmUser)}? They will lose access.`
        : `Restore access for ${fullName(confirmUser)}?`"
      :confirm-label="confirmUser?.status === 'ACTIVE' ? 'Blacklist' : 'Unblacklist'"
      :danger="confirmUser?.status === 'ACTIVE'"
      @confirm="toggleStatus"
      @cancel="showConfirm = false"
    />

  </div>
</template>

<script>
import SearchBar    from '@/components/shared/SearchBar.vue'
import StatusBadge  from '@/components/shared/StatusBadge.vue'
import ConfirmModal from '@/components/shared/ConfirmModal.vue'

export default {
  name: 'UserList',
  components: { SearchBar, StatusBadge, ConfirmModal },

  data() {
    return {
      users: [],
      loading: false,
      error: null,
      query: '',
      showConfirm: false,
      confirmUser: null,
    }
  },

  computed: {
    filtered() {
      const q = this.query.toLowerCase()

      if (!q) return this.users
      return this.users.filter(u =>
        this.fullName(u).toLowerCase().includes(q) ||
        u.email?.toLowerCase().includes(q)
      )
    }
  },

  methods: {
    token()   { return localStorage.getItem('tma_token') },
    headers() { 
      const t = this.token();

      if (!t || t === 'null' || t === 'undefined') {
        this.$router.push('/')
        return {};
      }
      return {
        Authorization: `Bearer ${t}`, 
        'Content-Type': 'application/json'
      }
     },

    fullName(u) { return u ? [u.first_name, u.last_name].filter(Boolean).join(' ') : '—' },

    initials(u) { return u ? ((u.first_name?.[0] || '') + (u.last_name?.[0] || '')).toUpperCase() || '?' : '?' },

    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },

    async load() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/admin/list-user', { headers: this.headers() })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)

        const responseData = await res.json()
        console.log("EXACT FLASK RESPONSE:", responseData);

        let userArray = [];

        if (Array.isArray(responseData)) {
            userArray = responseData; 
        } else if (responseData.data && Array.isArray(responseData.data)) {
            userArray = responseData.data; 
        } else if (responseData.users && Array.isArray(responseData.users)) {
            userArray = responseData.users; 
        } else {
            throw new Error("Backend did not return a valid list of users.");
        }

        this.users = userArray.filter(u => u.role === 'TREKKER');

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    askToggle(user) {
      this.confirmUser = user
      this.showConfirm = true
    },

    async toggleStatus() {
      const u = this.confirmUser
      if (!u) return

      const targetId = u.id || u.user_id

      const route = u.status === 'ACTIVE' ? 'blacklist' : 'unblacklist'

      try {
        const res = await fetch(`/admin/user/${targetId}/${route}`, {
          method: 'PUT', headers: this.headers()
        })

        if (!res.ok) throw new Error('Status update failed')
        
        u.status = u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'
        
        this.showConfirm = false
        this.confirmUser = null

      } catch (e) { 
        alert(e.message); 
      }
    },
  },

  mounted() { this.load() }
}
</script>

<style scoped>
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 600; color: #121619; }
.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 13px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; }

.list-card {
  display: flex; align-items: center; justify-content: space-between; gap: 16px; background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; transition: border-color 0.12s; }
.list-card:hover { border-color: #b6c6d6; }
.card-main { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.card-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e7f5ee; color: #1a6b42; font-size: 13px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.card-body  { flex: 1; min-width: 0; }
.card-name  { font-size: 14px; font-weight: 500; color: #121619; margin-bottom: 3px; }
.card-meta  { font-size: 12px; color: #6b7280; display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 2px; }
.sep        { color: #d1d5db; }
.card-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; }

.action-btn { padding: 5px 12px; border-radius: 5px; font-family: 'IBM Plex Sans', sans-serif; font-size: 12px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.12s;
}
.btn-success       { background: #1a6b42; border: 1px solid #1a6b42; color: #fff; }
.btn-success:hover { background: #155a36; }
.btn-danger        { background: #dc2626; border: 1px solid #dc2626; color: #fff; }
.btn-danger:hover  { background: #b91c1c; }

@media (max-width: 768px) {
  .list-card    { flex-direction: column; align-items: flex-start; }
  .card-actions { width: 100%; }
}
</style>