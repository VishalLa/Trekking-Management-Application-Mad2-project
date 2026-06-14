<template>
  <Teleport to="body">
    <div v-if="show" class="backdrop" @click.self="$emit('close')">
      
      <div class="custom-modal">
        
        <div class="custom-modal-header">
          <h3>Update {{ trek ? trek.trek_name : 'Trek' }}</h3>
          <button class="custom-modal-close" @click="$emit('close')">✕</button>
        </div>

        <form @submit.prevent="submit" class="custom-modal-body">
          <div class="form-row">
            <div class="field">
              <label>Start Date *</label>
              <input v-model="form.start_date" type="date" required />
            </div>
            <div class="field">
              <label>End Date *</label>
              <input v-model="form.end_date" type="date" required />
            </div>
          </div>

          <div class="form-row">
            <div class="field full">
              <label>Price (₹) *</label>
              <input v-model.number="form.price" type="number" min="0" step="0.01" required />
            </div>
          </div>

          <div class="field full">
            <label>Description</label>
            <textarea v-model="form.description" rows="3" placeholder="Brief description of the trek…"></textarea>
          </div>

          <div v-if="error" class="inline-error">{{ error }}</div>

          <div class="custom-modal-footer">
            <button type="button" class="btn-cancel" @click="$emit('close')">Cancel</button>
            <button type="submit" class="btn-confirm" :disabled="loading">
              {{ loading ? 'Updating…' : 'Update Trek' }}
            </button>
          </div>
        </form>
        
      </div>
    </div>
  </Teleport>
</template>

<script>
const emptyForm = () => ({
    start_date: '',
    end_date: '',
    price: '',
    description: ''
})

export default {
    name: 'UpdateTrekModal',
    props: {
        show: { type: Boolean, default: false },
        trek: { type: Object, default: null } 
    },

    emits: ['update', 'close'],

    data() {
        return {
            form: emptyForm(),
            loading: false, 
            error: ''
        }
    },

    watch: {
        show(isShown) {
            if (isShown && this.trek) {
                this.form = {
                    start_date: this.trek.start_date || '',
                    end_date: this.trek.end_date || '',
                    price: this.trek.price || '',
                    description: this.trek.description || ''
                }
            } else {
                this.form = emptyForm()
                this.error = ''
            }
        }
    },

    methods: { 
        token() { return localStorage.getItem('tma_token') },

        header() {
            const t = this.token()

            if (!t || t === 'null' || t === 'undefined') {
                this.$router.push('/')
                return {}
            }
            
            return {
                Authorization: `Bearer ${t}`, 
                'Content-Type': 'application/json'
            }
        },

        async submit() {
            if (!this.trek || !this.trek.trek_id) return

            this.loading = true
            this.error = ''

            try {
                const res = await fetch(`/admin/trek/update/${this.trek.trek_id}`, {
                    method: 'POST',
                    headers: this.header(),
                    body: JSON.stringify(this.form)
                })

                const data = await res.json()

                if (!res.ok) {
                    throw new Error(data.error || 'Failed to update trek')
                }

                this.$emit('update')
                this.$emit('close')

            } catch (err) {
                this.error = err.message
            } finally {
                this.loading = false
            }
        }
    } 
}
</script>


<style scoped>
.backdrop {
  position: fixed; 
  inset: 0; 
  background: rgba(0,0,0,0.4);
  display: flex; 
  align-items: center; 
  justify-content: center;
  z-index: 9999; 
  padding: 20px;
  font-family: 'IBM Plex Sans', sans-serif;
}

/* ── Custom Modal Container ── */
.custom-modal {
  display: block;
  opacity: 1;
  position: relative;
  background: #fff; 
  border: 1px solid #dde1e7; 
  border-radius: 10px;
  width: 100%; 
  max-width: 560px; 
  max-height: 90vh; 
  overflow-y: auto;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
  animation: modal-pop 0.2s ease-out forwards;
}

@keyframes modal-pop {
  0% { opacity: 0; transform: scale(0.95) translateY(-15px); }
  100% { opacity: 1; transform: scale(1) translateY(0); }
}

/* ── Header ── */
.custom-modal-header {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  padding: 18px 20px; 
  border-bottom: 1px solid #dde1e7;
  position: sticky; 
  top: 0; 
  background: #fff; 
  z-index: 10;
}
.custom-modal-header h3 { 
  font-size: 15px; 
  font-weight: 600; 
  color: #121619; 
  margin: 0; 
}
.custom-modal-close { 
  background: none; 
  border: none; 
  font-size: 16px; 
  color: #9ca3af; 
  cursor: pointer; 
}
.custom-modal-close:hover { color: #374151; }

/* ── Body & Forms ── */
.custom-modal-body { 
  padding: 20px; 
  display: flex; 
  flex-direction: column; 
  gap: 14px; 
}
.form-row   { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; }

.field { display: flex; flex-direction: column; gap: 6px; }
.field.full { grid-column: span 2; }
.field label { font-size: 12.5px; font-weight: 500; color: #374151; }
.field input, .field select, .field textarea {
  padding: 8px 12px; border: 1px solid #dde1e7; border-radius: 6px;
  font-family: inherit; font-size: 13.5px; color: #121619; outline: none;
  transition: border-color 0.12s;
}
.field input:focus, .field select:focus, .field textarea:focus { border-color: #1a6b42; }
.field textarea { resize: vertical; }

.inline-error { font-size: 12.5px; color: #dc2626; }

/* ── Footer ── */
.custom-modal-footer {
  display: flex; 
  justify-content: flex-end; 
  gap: 10px;
  padding-top: 14px; 
  border-top: 1px solid #f3f4f6; 
  margin-top: 4px;
}
.btn-cancel {
  padding: 8px 16px; border: 1px solid #dde1e7; border-radius: 6px;
  background: #fff; font-family: inherit; font-size: 13px; color: #374151; cursor: pointer;
}
.btn-cancel:hover { background: #f4f5f7; }
.btn-confirm {
  padding: 8px 16px; border: none; border-radius: 6px;
  background: #1a6b42; font-family: inherit; font-size: 13px; font-weight: 500; color: #fff;
  cursor: pointer; transition: background 0.12s;
}
.btn-confirm:hover:not(:disabled) { background: #155a36; }
.btn-confirm:disabled { opacity: 0.6; cursor: not-allowed; }

@media (max-width: 560px) {
  .form-row { grid-template-columns: 1fr; }
  .field.full { grid-column: span 1; }
}
</style>

