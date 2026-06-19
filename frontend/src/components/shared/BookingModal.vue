<template>
  <div class="bookings-panel">
    
    <div class="bp-header">
      <span class="bp-title">Bookings — {{ trek.trek_name }}</span>
      <div class="bp-header-right">
        <span class="bp-count" v-if="bookings.length">
          {{ bookings.length }} booking{{ bookings.length !== 1 ? 's' : '' }}
        </span>
        
        <span
          v-for="(count, status) in bookingSummary"
          :key="status"
          class="bp-summary-pill"
          :class="`pill-${status.toLowerCase()}`"
        >
          {{ status }}: {{ count }}
        </span>
      </div>
    </div>

    <p v-if="loading" class="bp-state">Loading bookings…</p>
    <p v-else-if="error" class="bp-error">{{ error }}</p>
    <p v-else-if="bookings.length === 0" class="bp-state">No bookings found for this trek.</p>

    <table v-else class="bookings-table">
      <thead>
        <tr>
          <th>Trekker</th>
          <th>Email</th>
          <th>Booking Date</th>
          <th>Qty</th>
          <th>Payment</th>
          <th>Status</th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="b in bookings" :key="b.booking_id">
          <td class="td-name">
            <div class="mini-avatar">{{ initials(b.user_name) }}</div>
            {{ b.user_name }}
          </td>
          <td class="td-email">{{ b.email || '—' }}</td>
          <td>{{ formatDate(b.booking_date) }}</td>
          <td class="td-center">{{ b.number_of_booking }}</td>
          <td class="td-center">
            <span class="payment-chip" :class="b.payment_status ? 'paid' : 'unpaid'">
              {{ b.payment_status ? 'Paid' : 'Unpaid' }}
            </span>
          </td>
          <td>
            <StatusBadge :status="b.status" type="booking" />
          </td>
        </tr>
      </tbody>
    </table>

  </div>
</template>

<script>
import StatusBadge from '@/components/shared/StatusBadge.vue'

export default {
  name: 'BookingModal',
  components: { StatusBadge },
  props: {
    trek: {
      type: Object,
      required: true
    },
    role: {
      type: String, 
      default: 'ADMIN',
      validator: (val) => ['ADMIN', 'STAFF'].includes(val.toUpperCase())
    }
  },

  data() {
    return {
      bookings: [],
      loading: true,
      error: null
    }
  },

  computed: {
    bookingSummary() {
      const counts = {}
      for (const b of this.bookings) {
        counts[b.status] = (counts[b.status] || 0) + 1
      }
      return counts
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
      return [u.first_name, u.last_name].filter(Boolean).join(' ') || u.email || '—'
    },

    initials(nameString) {
      if (!nameString) return '?'
      const parts = nameString.trim().split(' ')
      const first = parts[0]?.[0] || ''
      const last = parts.length > 1 ? parts[parts.length - 1][0] : ''
      return (first + last).toUpperCase() || '?'
    },

    async loadBookings() {
      this.loading = true
      this.error = null
      try {
        const urlPrefix = this.role.toUpperCase() === 'STAFF' ? '/staff' : '/admin'
        const res = await fetch(`${urlPrefix }/booking/${this.trek.trek_id}`, { 
          headers: this.headers() 
        })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)
        
        const data = await res.json()
        this.bookings = data.data || data
        
        this.$emit('loaded', this.bookings.length)

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    }
  },

  mounted() {
    this.loadBookings()
  }
}
</script>

<style scoped>
.bookings-panel {
  background: #f9fafb;
  border-top: 1px solid #dde1e7;
  padding: 16px 20px 20px;
}

/* Panel header */
.bp-header { display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px; margin-bottom: 14px; }
.bp-title { font-size: 13px; font-weight: 600; color: #121619; }
.bp-header-right { display: flex; align-items: center; gap: 8px; flex-wrap: wrap; }
.bp-count { font-size: 12px; color: #6b7280; }

/* booking status summary pills */
.bp-summary-pill { font-size: 11px; font-weight: 500; padding: 2px 9px; border-radius: 20px; }
.pill-booked    { background: #f0fdf4; color: #15803d; }
.pill-cancelled { background: #fef2f2; color: #b91c1c; }
.pill-completed { background: #eff6ff; color: #1d4ed8; }

/* Panel state messages */
.bp-state { font-size: 13px; color: #9ca3af; padding: 16px 0; text-align: center; }
.bp-error { font-size: 13px; color: #b91c1c; padding: 10px 0; }

/* ── Bookings table ── */
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

.payment-chip { font-size: 11.5px; font-weight: 500; padding: 2px 9px; border-radius: 4px; }
.payment-chip.paid   { background: #f0fdf4; color: #15803d; }
.payment-chip.unpaid { background: #fffbeb; color: #b45309; }

@media (max-width: 900px) {
  .bookings-panel { padding: 12px 14px 16px; overflow-x: auto; }
  .bookings-table { min-width: 580px; }
}
</style>
