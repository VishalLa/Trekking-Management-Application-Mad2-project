<template>
  <div class="payment-container">
    <div class="payment-header">
      <h3>Payment Details</h3>
      <p class="subtitle">Securely complete your booking.</p>
    </div>

    <form @submit.prevent="submit" class="payment-body">
      
      <!-- Cardholder Name -->
      <div class="field">
        <label>Name on Card *</label>
        <input 
          v-model="form.card_holder_name" 
          type="text" 
          placeholder="e.g. Jane Doe" 
          required 
        />
      </div>

      <!-- Card Number -->
      <div class="field">
        <label>Card Number *</label>
        <div class="input-with-icon">
          <span class="icon">💳</span>
          <input 
            v-model="form.card_no" 
            type="text" 
            maxlength="19"
            placeholder="0000 0000 0000 0000" 
            @input="formatCardNumber"
            required 
          />
        </div>
      </div>

      <!-- Expiry and CVV Row -->
      <div class="form-row">
        <div class="field">
          <label>Expiration Date *</label>
          <input 
            v-model="form.expration_date" 
            type="text" 
            placeholder="MM/YY" 
            maxlength="5"
            @input="formatExpiry"
            required 
          />
        </div>
        
        <div class="field">
          <label>Security Code (CVV) *</label>
          <input 
            v-model="form.card_cvv" 
            type="password" 
            placeholder="•••" 
            maxlength="4"
            @input="formatNumeric('card_cvv')"
            required 
          />
        </div>
      </div>

      <!-- Phone Number -->
      <div class="field">
        <label>Billing Phone Number *</label>
        <input 
          v-model="form.phone_no" 
          type="tel" 
          placeholder="e.g. 9876543210" 
          maxlength="15"
          @input="formatNumeric('phone_no')"
          required 
        />
      </div>

      <!-- Total & Submit -->
      <div class="payment-footer">
        <div class="total-box">
          <span class="total-label">Total to Pay:</span>
          <span class="total-amount">₹ {{ formatPrice(amount) }}</span>
        </div>
        
        <button type="submit" class="btn-confirm" :disabled="loading">
          {{ loading ? 'Processing...' : 'Pay Now' }}
        </button>
      </div>

    </form>
  </div>
</template>

<script>
export default {
  name: 'PaymentForm',
  props: {
    amount: {
      type: Number,
      required: true
    },
    bookingId: {
      type: [String, Number],
      required: true
    }
  },
  emits: ['payment-success', 'payment-failed'],

  data() {
    return {
      loading: false,
      form: {
        card_holder_name: '',
        card_no: '',
        expration_date: '',
        card_cvv: '',
        phone_no: ''
      }
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
      if (!price) return '0';
      return Number(price).toLocaleString('en-IN');
    },

    formatCardNumber(e) {
      let val = e.target.value.replace(/\D/g, '');
      let formatted = val.match(/.{1,4}/g)?.join(' ') || '';
      this.form.card_no = formatted;
    },

    formatExpiry(e) {
      let val = e.target.value.replace(/\D/g, '');
      if (val.length >= 2) {
        val = val.substring(0, 2) + '/' + val.substring(2, 4);
      }
      this.form.expration_date = val;
    },

    formatNumeric(field) {
      this.form[field] = this.form[field].replace(/\D/g, '');
    },

    async submit() {
      this.loading = true;
      const payload = {
        card_holder_name: this.form.card_holder_name.trim(),
        expration_date: this.form.expration_date,
        price: parseFloat(this.amount),
        card_no: parseInt(this.form.card_no.replace(/\s/g, ''), 10),
        card_cvv: parseInt(this.form.card_cvv, 10),
        phone_no: parseInt(this.form.phone_no, 10)
      }

      try {
        const endpoint = `/trekker/${this.userId()}/complete-booking/${this.bookingId}`
        const res = await fetch(endpoint, {
          method: 'POST',
          headers: this.headers(),
          body: JSON.stringify(payload)
        })

        const data = await res.json()

        if (!res.ok) {
          throw new Error(data.error || data.message || "Payment declined. Please try again.")
        }
        alert(`Payment successful! Confirmed.`)

        this.$emit('payment-success')

      } catch (e) {
        alert(e.message);
        this.$emit('payment-failed', e.message)
      } finally {
        this.loading = false
      }
    }
  },

}
</script>

<style scoped>
.payment-container { background: #ffffff; border: 1px solid #dde1e7; border-radius: 10px;
  max-width: 440px; margin: 0 auto; overflow: hidden; font-family: 'IBM Plex Sans', sans-serif; }
.payment-header { padding: 20px 24px; background: #f9fafb; border-bottom: 1px solid #dde1e7; }
.payment-header h3 { margin: 0 0 4px 0; font-size: 16px; font-weight: 600; color: #121619; }

.subtitle { margin: 0; font-size: 13px; color: #6b7280; }

.payment-body { padding: 24px; display: flex; flex-direction: column; gap: 16px; }

.form-row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.field { display: flex; flex-direction: column; gap: 6px; }

.field label { font-size: 12.5px; font-weight: 500; color: #374151; }
.field input { padding: 10px 12px; border: 1px solid #dde1e7; border-radius: 6px; font-family: inherit; font-size: 14px; color: #121619; outline: none; transition: border-color 0.12s; }
.field input:focus { border-color: #1a6b42; box-shadow: 0 0 0 2px rgba(26, 107, 66, 0.1); }

.input-with-icon { position: relative; display: flex; align-items: center; }

.input-with-icon .icon { position: absolute; left: 12px; font-size: 16px; color: #9ca3af; pointer-events: none; }
.input-with-icon input { width: 100%; padding-left: 38px; }
.payment-footer { margin-top: 8px; padding-top: 20px; border-top: 1px dashed #dde1e7; display: flex; flex-direction: column; gap: 16px; }

.total-box { display: flex; justify-content: space-between; align-items: center; }
.total-label { font-size: 14px; font-weight: 500; color: #374151; }
.total-amount { font-size: 20px; font-weight: 700; color: #1a6b42; }

.btn-confirm {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 6px;
  background: #1a6b42;
  font-family: inherit;
  font-size: 14px;
  font-weight: 600;
  color: #fff;
  cursor: pointer;
  transition: background 0.12s;
}

.btn-confirm:hover:not(:disabled) { background: #155a36; }
.btn-confirm:disabled { opacity: 0.7; cursor: not-allowed; }
</style>