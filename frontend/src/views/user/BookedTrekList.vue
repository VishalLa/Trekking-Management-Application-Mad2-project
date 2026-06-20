<template>
  <div>
    <div class="section-header">
      <h2 class="section-title">My Bookings</h2>
      <p class="subtitle">Manage your upcoming and past treks.</p>
    </div>

    <p v-if="loading" class="state-msg">Loading your bookings…</p>
    
    <div v-else-if="error" class="state-error">
      {{ error }}
      <button @click="loadBookings" class="retry-link">Retry</button>
    </div>
    
    <div v-else-if="bookings.length === 0" class="state-msg empty-state">
      <span class="empty-icon">🏔️</span>
      <p>You have no active bookings right now.</p>
      <button class="action-btn btn-outline mt-10" @click="$router.push('/trekker/treks')">
        Browse Treks
      </button>
    </div>

    <div v-else class="payment-grid">
      
      <div v-for="booking in bookings" :key="booking.booking_id" class="payment-card">
        
        <div class="card-header">
          <div class="card-name">{{ booking.trek_name }}</div>
          <StatusBadge :status="booking.booking_status" type="booking" />
        </div>

        <div class="card-body">
          <div class="detail-row">
            <span class="label">Location:</span>
            <span class="value">{{ booking.location }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Dates:</span>
            <span class="value">{{ booking.start_date }} → {{ booking.end_date }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Tickets:</span>
            <span class="value">{{ booking.number_of_tickets }}</span>
          </div>
          <div class="detail-row">
            <span class="label">Total Paid:</span>
            <span class="value">₹ {{ formatPrice(booking.total_amount) }}</span>
          </div>
        </div>

        <div class="card-footer">
          <button 
            class="action-btn btn-danger-outline cancel-btn" 
            :disabled="cancellingId === booking.booking_id || booking.booking_status === 'CANCELLED'"
            @click="cancelBooking(booking)"
          >
            {{ cancellingId === booking.booking_id ? 'Cancelling...' : 'Cancel Booking' }}
          </button>
        </div>

      </div>
    </div>
  </div>
</template>

<script>
import StatusBadge from '@/components/shared/StatusBadge.vue'

export default {
  name: 'BookedTrekList',
  components: { StatusBadge },

  data() {
    return {
      bookings: [],
      loading: true,
      error: null,
      cancellingId: null
    }
  },

  methods: {
    token()  { return localStorage.getItem('tma_token') },
    userId() { return localStorage.getItem('user_id') },

    headers() {
      const t = this.token()
      if (!t) {
        this.$router.push('/')
        return {}
      }

      return {
        Authorization: `Bearer ${t}`, 
        'Content-Type': 'application/json'
      }
    },

    formatPrice(price) {
      if (!price) return '0'
      return Number(price).toLocaleString('en-IN')
    },

    async loadBookings() {
      this.loading = true
      this.error = null

      try {
        const endpoint = `/trekker/booked-trek/${this.userId()}`
        const res = await fetch(endpoint, { 
          method: 'GET',
          headers: this.headers() 
        })

        if (!res.ok) throw new Error("Failed to load your bookings.")
        
        const payload = await res.json()
        this.bookings = Array.isArray(payload) ? payload : (payload.data || [])

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async cancelBooking(booking) {
      if (!confirm(`Are you sure you want to cancel your booking for ${booking.trek_name}? This cannot be undone.`)) {
        return;
      }

      this.cancellingId = booking.booking_id

      try {
        const endpoint = `/trekker/${this.userId()}/cancel-booking/${booking.booking_id}`
        
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: this.headers()
        })

        const data = await res.json()

        if (!res.ok) {
          throw new Error(data.error || data.message || "Failed to cancel booking. Please try again.")
        }

        alert("Booking cancelled successfully! A refund will be initiated if applicable.")
        
        this.bookings = this.bookings.filter(b => b.booking_id !== booking.booking_id)

      } catch (e) {
        alert(e.message)
      } finally {
        this.cancellingId = null
      }
    }
  },

  mounted() {
    this.loadBookings()
  }
}
</script>

<style scoped>
.section-header { margin-bottom: 20px; }
.section-title  { font-size: 18px; font-weight: 600; color: #121619; margin-bottom: 4px;}
.subtitle       { font-size: 13px; color: #6b7280; }

.state-msg   { padding: 40px; text-align: center; color: #9ca3af; font-size: 14px; background: #fff; border-radius: 8px; border: 1px dashed #dde1e7; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; display: flex; gap: 10px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; }
.empty-icon { font-size: 32px; margin-bottom: 12px; }
.mt-10 { margin-top: 10px; }

/* Grid Layout */
.payment-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

/* Card Styling */
.payment-card { background: #ffffff; border: 1px solid #dde1e7; border-radius: 8px; display: flex; flex-direction: column; overflow: hidden; transition: box-shadow 0.2s; }
.payment-card:hover { box-shadow: 0 4px 12px rgba(0,0,0,0.05); border-color: #b6c6d6; }

.card-header { padding: 16px; border-bottom: 1px solid #f3f4f6; display: flex; justify-content: space-between; align-items: flex-start; gap: 12px; }
.card-name { font-size: 15px; font-weight: 600; color: #121619; line-height: 1.4; }

.card-body { padding: 16px; display: flex; flex-direction: column; gap: 10px; flex-grow: 1; }
.detail-row { display: flex; justify-content: space-between; font-size: 13px; }
.detail-row .label { color: #6b7280; }
.detail-row .value { font-weight: 500; color: #374151; }

.card-footer { padding: 16px; background: #f9fafb; border-top: 1px dashed #dde1e7; }

/* Buttons */
.action-btn { display: inline-flex; align-items: center; justify-content: center; gap: 5px; border-radius: 6px; font-family: 'IBM Plex Sans', sans-serif; font-weight: 600; cursor: pointer; transition: all 0.12s; }

.btn-outline { background: #fff; border: 1px solid #dde1e7; color: #374151; padding: 8px 16px; font-size: 13px; }
.btn-outline:hover { background: #f4f5f7; }

.btn-danger-outline { background: #fff; border: 1px solid #fca5a5; color: #dc2626; }
.btn-danger-outline:hover:not(:disabled) { background: #fef2f2; }
.btn-danger-outline:disabled { opacity: 0.6; cursor: not-allowed; border-color: #dde1e7; color: #9ca3af; }

.cancel-btn { width: 100%; height: 42px; font-size: 14px; }
</style>
