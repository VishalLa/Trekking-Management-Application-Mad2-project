<template>
  <Teleport to="body">
    <div v-if="show" class="backdrop" @click.self="$emit('close')">
      <div class="modal">
        <div class="modal-header">
          <h3>Assign Trek — {{ staffName }}</h3>
          <button class="modal-close" @click="$emit('close')">✕</button>
        </div>

        <div class="modal-body">
          <div class="field">
            <label>Select Trek</label>
            <select v-model="trekId" :disabled="loadingTreks">
              <option value="">{{ loadingTreks ? 'Loading treks…' : 'Choose a trek…' }}</option>
              <option v-for="t in treks" :key="t.trek_id" :value="t.trek_id">
                {{ t.trek_name }} ({{ t.status }})
              </option>
            </select>
          </div>

          <div v-if="error" class="inline-error">{{ error }}</div>
        </div>

        <div class="modal-footer">
          <button class="btn-cancel" @click="$emit('close')">Cancel</button>
          <button class="btn-confirm" :disabled="!trekId || loading" @click="submit">
            {{ loading ? 'Assigning…' : 'Assign' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'AssignTrekModal',
  props: {
    show:  { type: Boolean, default: false },
    staff: { type: Object,  default: null  }
  },
  emits: ['assigned', 'close'],

  data() {
    return {
      treks: [],
      trekId: '',
      loading: false,
      loadingTreks: false,
      error: ''
    }
  },

  computed: {
    staffName() {
      if (!this.staff?.user_account) return ''
      return [this.staff.first_name, this.staff.last_name].filter(Boolean).join(' ');
    }
  },

  watch: {
    show(val) {
      if (val) { this.trekId = ''; this.error = ''; this.loadTreks() }
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

    async loadTreks() {
      this.loadingTreks = true

      try {
        const res = await fetch('/admin/list-trek', { headers: this.headers() })

        const data = await res.json()
        this.treks = data.data || data

      } catch { /* ignore */ }
      finally { this.loadingTreks = false }
    },

    async submit() {
      this.loading = true
      this.error = ''

      try {
        const res = await fetch(
          `/admin/staff/${this.staff.user_id}/trek/${this.trekId}/assign`,
          { method: 'PUT', headers: this.headers() }
        )

        if (!res.ok) { const d = await res.json(); throw new Error(d.message || 'Assignment failed') }

        this.$emit('assigned')

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
.backdrop {
  position: fixed; 
  inset: 0; 
  background: rgba(0,0,0,0.4);
  z-index: 9999; 
  font-family: 'IBM Plex Sans', sans-serif;
}

.modal {
  display: flex !important;
  flex-direction: column;
  
  position: absolute !important; 
  top: 0 !important;
  right: 0 !important;    
  left: auto !important;  
  bottom: 0 !important;
  margin: 0 !important;   

  background: #fff; 
  border-left: 1px solid #dde1e7; 
  width: 100%; 
  max-width: 380px;
  height: 100vh !important; 
  box-shadow: -5px 0 25px rgba(0, 0, 0, 0.15); 
  animation: slide-in-right 0.25s ease-out forwards; 
}

@keyframes slide-in-right {
  0% { transform: translateX(100%); }
  100% { transform: translateX(0); }
}

.modal-header {
  display: flex; 
  align-items: center; 
  justify-content: space-between;
  padding: 18px 20px; 
  border-bottom: 1px solid #dde1e7;
}

.modal-header h3 { 
  font-size: 15px; 
  font-weight: 600; 
  color: #121619; 
  margin: 0;
}

.modal-close { 
  background: none; 
  border: none; 
  font-size: 16px; 
  color: #9ca3af; 
  cursor: pointer; 
}

.modal-close:hover { 
  color: #374151; 
}

.modal-body { 
  padding: 20px; 
  flex: 1; 
  overflow-y: auto; 
}

.field { 
  display: flex; 
  flex-direction: column; 
  gap: 6px; 
}

.field label { 
  font-size: 12.5px; 
  font-weight: 500; 
  color: #374151; 
}

.field select {
  padding: 8px 12px; 
  border: 1px solid #dde1e7; 
  border-radius: 6px;
  font-family: inherit; 
  font-size: 13.5px; 
  color: #121619; 
  outline: none;
}

.field select:focus { 
  border-color: #1a6b42; 
}

.inline-error { 
  margin-top: 10px; 
  font-size: 12.5px; 
  color: #dc2626; 
}

.modal-footer {
  display: flex; 
  justify-content: flex-end; 
  gap: 10px;
  padding: 14px 20px; 
  border-top: 1px solid #f3f4f6;
  background: #fff; 
}

.btn-cancel {
  padding: 8px 16px; 
  border: 1px solid #dde1e7; 
  border-radius: 6px;
  background: #fff; 
  font-family: inherit; 
  font-size: 13px; 
  color: #374151; 
  cursor: pointer;
}

.btn-cancel:hover { 
  background: #f4f5f7; 
}

.btn-confirm {
  padding: 8px 16px; 
  border: none; 
  border-radius: 6px;
  background: #1a6b42; 
  font-family: inherit; 
  font-size: 13px; 
  font-weight: 500; 
  color: #fff;
  cursor: pointer; 
  transition: background 0.12s;
}

.btn-confirm:hover:not(:disabled) { 
  background: #155a36; 
}

.btn-confirm:disabled { 
  opacity: 0.6; 
  cursor: not-allowed; 
}
</style>