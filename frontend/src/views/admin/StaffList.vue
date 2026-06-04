<template>
  <div>
    <div class="section-header">
      <h2 class="section-title">Staff List</h2>
      <div class="header-right">
        <SearchBar v-model="query" placeholder="Search by name or email…" />
        <button class="primary-btn" @click="showCreate = true">+ Create Staff</button>
      </div>
    </div>

    <p v-if="loading" class="state-msg">Loading staff…</p>
    <div v-else-if="error" class="state-error">
      {{ error }} <button @click="load" class="retry-link">Retry</button>
    </div>
    <p v-else-if="filtered.length === 0" class="state-msg">No staff found.</p>

    <div v-else>
      <div 
        v-for="member in filtered" 
        :key="member.user_id" 
        class="staff-block"
        :class="{ expanded: expandedId === member.user_id }"
      >

        <div class="list-card">
          <div class="card-main">
            <div class="card-avatar">{{ initials(member) }}</div>
            <div class="card-body">
              <div class="card-name">{{ fullName(member) }}</div>
              <div class="card-meta">
                <span>{{ member.email }}</span>
                <span class="sep">·</span>
                <span>{{ member.phone_no }}</span>
                <span class="sep">·</span>
                <span>{{ member.experience }} yrs experience</span>
              </div>
            </div>
          </div>

          <div class="card-actions">
            <StatusBadge :status="member.status" type="user" />

            <button
              class="action-btn"
              :class="member.status === 'ACTIVE' ? 'btn-danger' : 'btn-success'"
              @click="toggleStatus(member)"
            >
              {{ member.status === 'ACTIVE' ? 'Suspend' : 'Activate' }}
            </button>

            <button class="action-btn btn-outline" @click="openAssign(member)">
              Assign Trek
            </button>

            <button
              class="action-btn btn-treks"
              :class="{ active: expandedId === member.user_id }"
              @click="togglePanel(member.user_id)"
            >
              <svg width="13" height="13" viewBox="0 0 16 16" fill="none">
                <rect x="2" y="3" width="12" height="11" rx="2" stroke="currentColor" stroke-width="1.4"/>
                <path d="M5 1v4M11 1v4M2 7h12" stroke="currentColor" stroke-width="1.4" stroke-linecap="round"/>
              </svg>
              {{ expandedId === member.user_id ? 'Hide Treks' : 'View Treks' }}
              <span v-if="trekCounts[member.user_id] !== undefined" class="trek-count-chip">
                {{ trekCounts[member.user_id] }}
              </span>
            </button>

            <button class="action-btn btn-danger-outline" @click="askDelete(member)">
              Delete
            </button>
          </div>
        </div>

        <StaffAssignedTreks 
          v-if="expandedId === member.user_id" 
          :staff="member" 
          @loaded="count => updateTrekCount(member.user_id, count)" 
        />
        
      </div>
    </div>

    <CreateStaffModal 
      :show="showCreate" 
      @created="onCreated" 
      @close="showCreate = false" 
    />

    <ConfirmModal
      :show="showConfirm"
      title="Delete Staff Member"
      :message="`Are you sure you want to delete ${deleteTarget?.first_name || 'this staff member'}? This cannot be undone.`"
      confirm-label="Delete"
      :danger="true"
      @confirm="confirmDelete"
      @cancel="showConfirm = false"
    />

    <AssignTrekModal 
      :show="showAssign" 
      :staff="assignTarget"
      @assigned="onAssigned" 
      @close="showAssign = false" 
    />

  </div>
</template>

<script>
import SearchBar              from '@/components/shared/SearchBar.vue'
import StatusBadge            from '@/components/shared/StatusBadge.vue'
import ConfirmModal           from '@/components/shared/ConfirmModal.vue'
import AssignTrekModal        from '@/components/admin/AssignTrekModal.vue'
import StaffAssignedTreks     from '@/components/admin/StaffAssignedTreks.vue'
import CreateStaffModal       from '@/components/admin/CreateStaffModal.vue'

export default {
  name: 'StaffList',
  components: { SearchBar, StatusBadge, ConfirmModal, AssignTrekModal, StaffAssignedTreks, CreateStaffModal },

  data() {
    return {
      staff: [],
      loading: false,
      error: null,
      query: '',

      showAssign: false,
      assignTarget: null,
      
      showConfirm: false,
      deleteTarget: null,

      showCreate: false,

      expandedId: null,  
      trekCounts: {},    
    }
  },

  computed: {
    filtered() {
      const q = this.query.toLowerCase()

      if (!q) return this.staff
      return this.staff.filter(s =>
        this.fullName(s).toLowerCase().includes(q) ||
        (s.email && s.email.toLowerCase().includes(q))
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

    async load() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/admin/list-staff', { headers: this.headers() })
        
        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)
        
        const data = await res.json()
        this.staff = data.data || data

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async toggleStatus(member) {
      const u = member
      const route = u.status === 'ACTIVE' ? 'blacklist' : 'unblacklist'

      try {
        const res = await fetch(`/admin/user/${u.user_id}/${route}`, {
          method: 'PUT', headers: this.headers()
        })

        if (!res.ok) throw new Error('Status update failed')
        u.status = u.status === 'ACTIVE' ? 'SUSPENDED' : 'ACTIVE'

      } catch (e) { alert(e.message) }
    },

    openAssign(member) {
      this.assignTarget = member
      this.showAssign = true
    },

    onAssigned() {
      this.showAssign = false
      if (this.expandedId === this.assignTarget?.user_id) {
          this.expandedId = null;
          setTimeout(() => { this.expandedId = this.assignTarget.user_id }, 50);
      }
      this.load()
    },

    askDelete(member) {
      this.deleteTarget = member
      this.showConfirm = true
    },

    onCreated() {
      this.showCreate = false;
      this.load();
    },

    async confirmDelete() {
      this.showConfirm = false
      const targetId = this.deleteTarget.user_id

      try {
        const res = await fetch(`/admin/staff/${targetId}/delete`, {
          method: 'DELETE', headers: this.headers()
        })

        if (!res.ok) {
          const contentType = res.headers.get("content-type")
          
          if (contentType && contentType.includes("application/json")) {
            const errorData = await res.json()
            throw new Error(errorData.error || errorData.message || `Backend rejected with status ${res.status}`)
          } else {
            throw new Error(`Server Error ${res.status}: The delete route was not found.`)
          }
        }

        this.staff = this.staff.filter(s => s.user_id !== targetId);
      } catch (e) { alert(e.message) }
    },

    togglePanel(targetId) {
      this.expandedId = this.expandedId === targetId ? null: targetId
    },

    updateTrekCount(targetId, count){
      this.trekCounts[targetId] = count;
    }
  },

  mounted() { this.load() }
}
</script>

<style scoped>
/* ── Layout helpers ── */
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 16px; }
.section-title { font-size: 16px; font-weight: 600; color: #121619; }

.header-right { display: flex;  align-items: center;  gap: 10px; }

.primary-btn {  padding: 8px 16px;  background: #1a6b42;  border: none;  border-radius: 6px;  color: #fff;  font-family: 'IBM Plex Sans', sans-serif;  font-size: 13px;  font-weight: 500;  cursor: pointer;  white-space: nowrap;  transition: background 0.12s; }
.primary-btn:hover {  background: #155a36; }

/* ── State messages ── */
.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 13px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; }

/* ── List card ── */
.list-card { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 14px 16px; margin-bottom: 10px; transition: border-color 0.12s; }
.list-card:hover { border-color: #b6c6d6; }

.card-main { display: flex; align-items: center; gap: 12px; flex: 1; min-width: 0; }
.card-avatar { width: 36px; height: 36px; border-radius: 50%; background: #e7f5ee; color: #1a6b42; font-size: 13px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.card-body   { flex: 1; min-width: 0; }
.card-name   { font-size: 14px; font-weight: 500; color: #121619; margin-bottom: 3px; }
.card-meta   { font-size: 12px; color: #6b7280; display: flex; flex-wrap: wrap; gap: 4px; margin-bottom: 2px; }
.sep         { color: #d1d5db; }

.card-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }

.action-btn         { padding: 5px 12px; border-radius: 5px; font-family: 'IBM Plex Sans', sans-serif;font-size: 12px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.12s; }
.btn-success        { background: #1a6b42; border: 1px solid #1a6b42; color: #fff; }
.btn-success:hover  { background: #155a36; }
.btn-danger         { background: #dc2626; border: 1px solid #dc2626; color: #fff; }
.btn-danger:hover   { background: #b91c1c; }
.btn-outline        { background: #fff; border: 1px solid #dde1e7; color: #374151; }
.btn-outline:hover  { background: #f4f5f7; }
.btn-danger-outline { background: #fff; border: 1px solid #fca5a5; color: #dc2626; }
.btn-danger-outline:hover { background: #fef2f2; }

.staff-block {  margin-bottom: 10px;  border-radius: 8px;  overflow: hidden;  border: 1px solid #dde1e7;  transition: border-color 0.12s; }
.staff-block:hover      { border-color: #b6c6d6; }
.staff-block.expanded   { border-color: #1a6b42; }

.staff-block .list-card {  margin-bottom: 0;  border: none;  border-radius: 0; }

.btn-treks { background: #fff; border: 1px solid #dde1e7; color: #374151; }
.btn-treks:hover { background: #f0faf4; border-color: #1a6b42; color: #1a6b42; }
.btn-treks.active { background: #f0faf4; border-color: #1a6b42; color: #1a6b42; font-weight: 600; }
.trek-count-chip { background: #1a6b42; color: #fff; font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 20px; min-width: 18px; text-align: center; }
.btn-treks:not(.active) .trek-count-chip { background: #e5e7eb; color: #4b5563; }

@media (max-width: 768px) {
  .list-card    { flex-direction: column; align-items: flex-start; }
  .card-actions { width: 100%; }
}
</style>