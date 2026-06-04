<template>
  <div class="bookings-panel">
    
    <div class="bp-header">
      <span class="bp-title">Assigned Treks — {{ fullName(staff) }}</span>
      <div class="bp-header-right">
        <span class="bp-count" v-if="treks.length">
          {{ treks.length }} Trek{{ treks.length !== 1 ? 's' : '' }} Assigned
        </span>
      </div>
    </div>

    <p v-if="loading" class="bp-state">Loading assigned treks…</p>
    <p v-else-if="error" class="bp-error">{{ error }}</p>
    <p v-else-if="treks.length === 0" class="bp-state">No treks assigned to this staff member yet.</p>

    <table v-else class="bookings-table">
      <thead>
        <tr>
          <th>Trek Name</th>
          <th>Location</th>
          <th>Duration</th>
          <th>Difficulty</th>
          <th>Schedule (Start → End)</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(t, index) in treks" :key="index">
          <td class="td-name">{{ t.trek_name }}</td>
          <td>📍 {{ t.location }}</td>
          <td class="td-center">{{ t.duration }} Days</td>
          <td>
            <StatusBadge :status="t.difficulty" type="difficulty" />
          </td>
          <td>{{ formatDate(t.start_date) }} → {{ formatDate(t.end_date) }}</td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import StatusBadge from '@/components/shared/StatusBadge.vue'

export default {
  name: 'StaffAssignedTreks',
  components: { StatusBadge },
  props: {
    staff: {
      type: Object,
      required: true
    }
  },
  data() {
    return {
      treks: [],
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

    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },

    fullName(u) {
      if (!u) return '—'
      return [u.first_name, u.last_name].filter(Boolean).join(' ') || '—'
    },

    async loadTreks() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch(`/admin/staff/${this.staff.user_id}/treks`, { 
            headers: this.headers() 
        })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)
        
        const data = await res.json()
        this.treks = data.assigned_treks || data.data || data

        this.$emit('loaded', this.treks.length)

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    }
  },
  mounted() {
    this.loadTreks()
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
.bookings-table tbody tr:hover td { background: #f9fafb; }
.td-name { font-weight: 500; color: #121619; }
.td-center { text-align: center; }

@media (max-width: 900px) {
  .bookings-panel { padding: 12px 14px 16px; overflow-x: auto; }
  .bookings-table { min-width: 580px; }
}
</style>
