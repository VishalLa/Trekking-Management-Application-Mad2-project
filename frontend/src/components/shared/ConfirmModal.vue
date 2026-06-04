<template>
  <Teleport to="body">
    <div v-if="show" class="backdrop" @click.self="$emit('cancel')">
      <div class="modal" role="dialog" :aria-label="title">
        <h3 class="modal-title">{{ title }}</h3>
        <p class="modal-msg">{{ message }}</p>
        <div class="modal-actions">
          <button class="btn-cancel" @click="$emit('cancel')">Cancel</button>
          <button
            class="btn-confirm"
            :class="{ 'btn-danger': danger }"
            @click="$emit('confirm')"
          >
            {{ confirmLabel }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script>
export default {
  name: 'ConfirmModal',
  props: {
    show:         { type: Boolean, default: false },
    title:        { type: String,  default: 'Are you sure?' },
    message:      { type: String,  default: 'This action cannot be undone.' },
    confirmLabel: { type: String,  default: 'Confirm' },
    danger:       { type: Boolean, default: false }
  },
  emits: ['confirm', 'cancel']
}
</script>

<style scoped>
.backdrop {
  position: fixed; 
  top: 0; 
  left: 0; 
  right: 0; 
  bottom: 0;
  background: rgba(0, 0, 0, 0.4); 
  display: flex; 
  align-items: flex-start;
  justify-content: center;
  z-index: 9999;
  padding: 80px 20px 20px 20px;
  font-family: 'IBM Plex Sans', sans-serif;
}

.modal {
  display: block !important;
  height: auto !important;
  min-height: 0 !important;
  position: relative;
  background: #fff;
  border: 1px solid #dde1e7;
  border-radius: 10px;
  padding: 28px 24px;
  width: 100%;
  max-width: 400px;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15); 
  animation: modal-pop 0.2s ease-out forwards; 
}

@keyframes modal-pop {
  0% { 
    opacity: 0; 
    transform: scale(0.95) translateY(-15px); 
  }
  100% { 
    opacity: 1; 
    transform: scale(1) translateY(0); 
  }
}

.modal-title {
  font-size: 16px;
  font-weight: 600;
  color: #121619;
  margin-bottom: 10px;
}

.modal-msg {
  font-size: 13.5px;
  color: #4b5563;
  line-height: 1.5;
  margin-bottom: 24px;
}

.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 10px;
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
  transition: background 0.15s;
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
  transition: background 0.15s;
}

.btn-confirm:hover { 
  background: #155a36; 
}

.btn-confirm.btn-danger { 
  background: #dc2626; 
}

.btn-confirm.btn-danger:hover { 
  background: #b91c1c; 
}
</style>