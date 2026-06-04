<template>
  <div class="bookings-panel">
    
    <div class="bp-header">
      <span class="bp-title">Assigned Staff — {{ trek.trek_name }}</span>
      <div class="bp-header-right">
        <span class="bp-count" v-if="staff.length">
          {{ staff.length }} Staff Member{{ staff.length !== 1 ? 's' : '' }}
        </span>
      </div>
    </div>

    <p v-if="loading" class="bp-state">Loading assigned staff…</p>
    <p v-else-if="error" class="bp-error">{{ error }}</p>
    <p v-else-if="staff.length === 0" class="bp-state">No staff members assigned to this trek yet.</p>

    <table v-else class="bookings-table">
      <thead>
        <tr>
          <th>Staff Member</th>
          <th>Email</th>
          <th>Phone</th>
          <th>Experience</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="member in staff" :key="member.user_id || member.id">
          <td class="td-name">
            <div class="mini-avatar">{{ initials(member) }}</div>
            {{ fullName(member) }}
          </td>
          <td class="td-email">{{ member.email || '—' }}</td>
          <td>{{ member.phone_no || '—' }}</td>
          <td class="td-center">{{ member.experience || 0 }} yrs</td>
          <td>
            <StatusBadge :status="member.status" type="user" />
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import StatusBadge from '@/components/shared/StatusBadge.vue'

export default {
  name: 'TrekAssignedStaff',
  components: { StatusBadge },
  props: {
    trek: {
      type: Object,
      required: true
    }
  },

  data() {
    return {
      staff: [],
      loading: true,
      error: null
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

    fullName(u) {
      if (!u) return '—'
      return [u.first_name, u.last_name].filter(Boolean).join(' ') || '—'
    },

    initials(u) {
      if (!u) return '?'
      return ((u.first_name?.[0] || '') + (u.last_name?.[0] || '')).toUpperCase() || '?'
    },

    async loadStaff() {
      this.loading = true
      this.error = null
      try {
        const res = await fetch(`/admin/trek/${this.trek.trek_id}/staff`, { 
            headers: this.headers() 
        })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)
        
        const data = await res.json()
        this.staff = data.data || data.staff || data
        
        this.$emit('loaded', this.staff.length)

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    }
  },
  
  mounted() {
    this.loadStaff()
  }
}
</script>

<style scoped>
.bookings-panel { background: #f9fafb; border-top: 1px solid #dde1e7; padding: 16px 20px 20px; }
.bp-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.bp-title { font-size: 13px; font-weight: 600; color: #121619; }
.bp-header-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.bp-count { font-size: 12px; color: #6b7280; font-weight: 500; }
.bp-state { font-size: 13px; color: #9ca3af; padding: 16px 0; text-align: center; }
.bp-error { font-size: 13px; color: #b91c1c; padding: 10px 0; }

.bookings-table { width: 100%; border-collapse: collapse; background: #fff; border: 1px solid #dde1e7; border-radius: 8px; overflow: hidden; font-family: 'IBM Plex Sans', sans-serif; }
.bookings-table thead tr { background: #f4f5f7; }
.bookings-table th { font-size: 11.5px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; text-align: left; padding: 9px 14px; border-bottom: 1px solid #dde1e7; white-space: nowrap; }
.bookings-table td { padding: 10px 14px; font-size: 13px; color: #374151; border-bottom: 1px solid #f3f4f6; vertical-align: middle; }
.bookings-table tbody tr:last-child td { border-bottom: none; }
.bookings-table tbody tr:hover td     { background: #f9fafb; }

.td-name { display: flex; align-items: center; gap: 8px; font-weight: 500; color: #121619; white-space: nowrap; }
.mini-avatar { width: 26px; height: 26px; border-radius: 50%; background: #e7f5ee; color: #1a6b42; font-size: 11px; font-weight: 600; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
.td-email  { color: #6b7280; font-size: 12.5px; }
.td-center { text-align: center; }

@media (max-width: 900px) {
  .bookings-panel { padding: 12px 14px 16px; overflow-x: auto; }
  .bookings-table { min-width: 580px; }
}
</style>
