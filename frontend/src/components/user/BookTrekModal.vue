<template>
  <Teleport to="body">
    <div v-if="show" class="backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h3>Book Trek: {{ trek?.trek_name }}</h3>
          <button class="modal-close" @click="$emit('close')">✕</button>
        </div>

        <form v-if="!showPayment" @submit.prevent="submit_data" class="modal-body">

          <div class="trek-summary">
            <div class="summary-item">
              <span class="label">Location:</span>
              <span class="value">{{ trek?.location }}</span>
            </div>

            <div class="summary-item"> 
              <span class="label">Dates:</span>
              <span class="value">{{ formatDate(trek?.start_date) }} → {{ formatDate(trek?.end_date) }}</span>
            </div>

            <div class="summary-item">
              <span class="label">Available Slots:</span>
              <span class="value">{{ trek?.available_slots }}</span>
            </div>
          </div>

          <div class="field">
            <label>Number of Tickets *</label>
            <input
              v-model.number="numberOfTickets"
              type="number"
              min="1"
              :max="trek?.available_slots || 1"
              required
            />
          </div>

          <div class="total-price-box">
            <span class="total-label">Total Amount Due:</span>
            <span class="total-value">₹ {{ formatPrice(totalPrice) }}</span>
          </div>

          <div v-if="error" class="inline-error">{{ error }}</div>
          <div v-if="success" class="inline-success">Booking created successfully! Redirecting...</div>

          <div class="modal-footer">
            <button
              type="button"
              class="btn-cancel"
              @click="$emit('close')"
              :disabled="loading"
            >
              Cancel
            </button>

            <button
              type="submit"
              class="btn-confirm"
              :disabled="loading || numberOfTickets < 1 || numberOfTickets > trek?.available_slots"
            >
              {{ loading ? 'Processing...' : 'Confirm Booking' }}
            </button>
          </div>
        </form>

        <div v-else class="modal-body">
          <PaymentForm 
            :amount="totalPrice"
            :bookingId="newBookingId"
            @payment-success="handlePaymentSuccess"
          />
        </div>

      </div>
    </div>
  </Teleport>
</template>

<script>
import PaymentForm from '@/components/user/PaymentForm.vue'

export default {
  name: 'BookTrekModal',
  components: { PaymentForm },
  props: {
    show: { type: Boolean, default: false },
    trek: { type: Object, default: null }
  },
  emits: ['booked', 'close'],

  data() {
    return {
      numberOfTickets: 1,
      loading: false,
      error: '',
      success: false,

      showPayment: false,
      newBookingId: null
    }
  },

  computed: {
    totalPrice() {
      if (!this.trek || !this.trek.price || !this.numberOfTickets) return 0
      return this.trek.price * this.numberOfTickets
    }
  },

  watch: {
    show(val) {
      if (val) {
        this.numberOfTickets = 1 
        this.error = ''
        this.success = false
        this.showPayment = false
        this.newBookingId = null
      }
    }
  },

  methods: {
    token()   { return localStorage.getItem('tma_token') },
    userId()  { return localStorage.getItem('user_id') },

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

    formatPrice(price) {
      if (!price) return '0';
      return Number(price).toLocaleString('en-IN')
    },

    async submit_data() {
      if (this.numberOfTickets < 1) {
        this.error = "You must book at least 1 ticket."
        return
      }

      if (this.numberOfTickets > this.trek.available_slots) {
        this.error = `Only ${this.trek.available_slots} slots are available.`
        return
      }

      this.loading = true
      this.error = ''

      try {
        const endpoint = `/trekker/${this.userId()}/book-trek/${this.trek.trek_id}`

        const res = await fetch(endpoint, {
          method: 'POST',
          headers: this.headers(),
          body: JSON.stringify({
            number_of_booking: this.numberOfTickets
          })
        })

        const data = await res.json()

        if (!res.ok) {
          throw new Error(data.error || data.message || "Failed to book trek.")
        }

        this.success = true
        this.newBookingId = data.booking_id

        setTimeout(() => {
          this.showPayment = true
          this.success = false
        }, 800)

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    handlePaymentSuccess() {
      this.$emit('booked') 
      this.$emit('close')
    }
  }
}
</script>


<style scoped>
/* Base Modal Styles */
.backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.32); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; font-family: 'IBM Plex Sans', sans-serif; }
.modal { display: block !important; position: relative; z-index: 210; background: #fff; border: 1px solid #dde1e7; border-radius: 10px; width: 100%; max-width: 480px; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid #dde1e7; position: sticky; top: 0; background: #fff; z-index: 1; }
.modal-header h3 { font-size: 15px; font-weight: 600; color: #121619; }
.modal-close { background: none; border: none; font-size: 16px; color: #9ca3af; cursor: pointer; }
.modal-close:hover { color: #374151; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 16px; }

/* Trek Summary Box */
.trek-summary { background: #f9fafb; border: 1px solid #dde1e7; border-radius: 8px; padding: 12px 16px; display: flex; flex-direction: column; gap: 8px; }
.summary-item { display: flex; justify-content: space-between; font-size: 13px; color: #374151; }
.summary-item.highlight .value { color: #1a6b42; font-weight: 600; }
.summary-item .label { color: #6b7280; }
.summary-item .value { font-weight: 500; }

/* Form Fields */
.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12.5px; font-weight: 500; color: #374151; }
.field input { padding: 8px 12px; border: 1px solid #dde1e7; border-radius: 6px; font-family: inherit; font-size: 13.5px; color: #121619; outline: none; transition: border-color 0.12s; }
.field input:focus { border-color: #1a6b42; }

/* Total Price Calculator */
.total-price-box { display: flex; justify-content: space-between; align-items: center; padding-top: 12px; border-top: 1px dashed #dde1e7; }
.total-label { font-size: 14px; font-weight: 500; color: #121619; }
.total-value { font-size: 18px; font-weight: 600; color: #1a6b42; }

/* Alerts */
.inline-error { font-size: 12.5px; color: #dc2626; background: #fef2f2; padding: 8px; border-radius: 4px; border: 1px solid #fca5a5; }
.inline-success { font-size: 12.5px; color: #15803d; background: #f0fdf4; padding: 8px; border-radius: 4px; border: 1px solid #bbf7d0; }

/* Footer */
.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 8px; border-top: 1px solid #f3f4f6; margin-top: 4px; }
.btn-cancel { padding: 8px 16px; border: 1px solid #dde1e7; border-radius: 6px; background: #fff; font-family: inherit; font-size: 13px; color: #374151; cursor: pointer; }
.btn-cancel:hover { background: #f4f5f7; }
.btn-cancel:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-confirm { padding: 8px 16px; border: none; border-radius: 6px; background: #1a6b42; font-family: inherit; font-size: 13px; font-weight: 500; color: #fff; cursor: pointer; transition: background 0.12s; }
.btn-confirm:hover:not(:disabled) { background: #155a36; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }
</style>
