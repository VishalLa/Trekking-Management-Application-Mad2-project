<template>
  <Teleport to="body">
    <div v-if="show" class="backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h3>Create New Staff Account</h3>
          <button class="modal-close" @click="$emit('close')">✕</button>
        </div>

        <form @submit.prevent="submit" class="modal-body">
          
          <div class="form-row">
            <div class="field">
              <label>First Name *</label>
              <input v-model="form.first_name" type="text" placeholder="e.g. John" required />
            </div>
            <div class="field">
              <label>Last Name</label>
              <input v-model="form.last_name" type="text" placeholder="e.g. Doe (Optional)" />
            </div>
          </div>

          <div class="form-row">
            <div class="field">
              <label>Email Address *</label>
              <input v-model="form.email" type="email" placeholder="john@example.com" required />
            </div>
            <div class="field">
              <label>Phone Number *</label>
              <input v-model="form.phone_no" type="tel" placeholder="+91 9999999999" required />
            </div>
          </div>

          <div class="form-row">
            <div class="field">
              <label>Temporary Password *</label>
              <input v-model="form.password" type="password" placeholder="••••••••" minlength="8" required />
            </div>
            <div class="field">
              <label>Years of Experience *</label>
              <input v-model.number="form.experience" type="number" min="0" placeholder="e.g. 5" required />
            </div>
          </div>

          <div v-if="error" class="inline-error">{{ error }}</div>

          <div class="modal-footer">
            <button type="button" class="btn-cancel" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn-confirm" :disabled="loading">
              {{ loading ? 'Creating…' : 'Create Staff' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </Teleport>
</template>

<script>
const emptyForm = () => ({
  first_name: '', 
  last_name: '', 
  email: '', 
  phone_no: '',
  password: '', 
  experience: ''
})

export default {
  name: 'CreateStaffModal',
  props: {
    show: { type: Boolean, default: false }
  },
  emits: ['created', 'close'],

  data() {
    return {
      form: emptyForm(),
      loading: false,
      error: ''
    }
  },

  watch: {
    show(val) {
      if (val) { this.form = emptyForm(); this.error = '' }
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

    async submit() {
      this.loading = true
      this.error = ''
      
      try {
        const res = await fetch('/auth/register/staff', {
          method: 'POST',
          headers: this.headers(),
          body: JSON.stringify(this.form)
        })

        const contentType = res.headers.get("content-type")
        
        if (!res.ok) {
          if (contentType && contentType.includes("application/json")) {
            const d = await res.json()
            console.error("Backend Error Details:", d);
            // throw new Error(d.message || d.error || "Failed to create staff account.")
          } else {
            throw new Error(`Server Error ${res.status}: The backend route was not found.`)
          }
        }
        
        this.$emit('created')
        
      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    }
  }
}
</script>

<style scoped>
/* Identical styling to your CreateTrekModal for perfect consistency */
.backdrop { position: fixed; inset: 0; background: rgba(0,0,0,0.32); display: flex; align-items: center; justify-content: center; z-index: 1000; padding: 20px; font-family: 'IBM Plex Sans', sans-serif; }
.modal { display: block !important; position: relative; z-index: 210; background: #fff; border: 1px solid #dde1e7; border-radius: 10px; width: 100%; max-width: 560px; max-height: 90vh; overflow-y: auto; }
.modal-header { display: flex; align-items: center; justify-content: space-between; padding: 18px 20px; border-bottom: 1px solid #dde1e7; position: sticky; top: 0; background: #fff; z-index: 1; }
.modal-header h3 { font-size: 15px; font-weight: 600; color: #121619; }
.modal-close { background: none; border: none; font-size: 16px; color: #9ca3af; cursor: pointer; }
.modal-close:hover { color: #374151; }

.modal-body { padding: 20px; display: flex; flex-direction: column; gap: 14px; }
.form-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field label { font-size: 12.5px; font-weight: 500; color: #374151; }
.field input { padding: 8px 12px; border: 1px solid #dde1e7; border-radius: 6px; font-family: inherit; font-size: 13.5px; color: #121619; outline: none; transition: border-color 0.12s; }
.field input:focus { border-color: #1a6b42; }

.inline-error { font-size: 12.5px; color: #dc2626; }

.modal-footer { display: flex; justify-content: flex-end; gap: 10px; padding-top: 8px; border-top: 1px solid #f3f4f6; margin-top: 4px; }
.btn-cancel { padding: 8px 16px; border: 1px solid #dde1e7; border-radius: 6px; background: #fff; font-family: inherit; font-size: 13px; color: #374151; cursor: pointer; }
.btn-cancel:hover { background: #f4f5f7; }
.btn-confirm { padding: 8px 16px; border: none; border-radius: 6px; background: #1a6b42; font-family: inherit; font-size: 13px; font-weight: 500; color: #fff; cursor: pointer; transition: background 0.12s; }
.btn-confirm:hover:not(:disabled) { background: #155a36; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 560px) { .form-row { grid-template-columns: 1fr; } }
</style>
