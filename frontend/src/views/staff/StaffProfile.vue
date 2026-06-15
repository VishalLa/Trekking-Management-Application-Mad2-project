<template>
  <div class="profile-container">
    <div class="section-header">
      <h2 class="section-title">My Profile</h2>
    </div>

    <p v-if="loading" class="state-msg">Loading profile data…</p>
    
    <div v-else-if="fetchError" class="state-error">
      {{ fetchError }}
      <button @click="loadProfile" class="retry-link">Retry</button>
    </div>

    <div v-else class="panel">
      <form @submit.prevent="saveProfile" class="profile-form">
        
        <h3 class="group-title">Personal Details</h3>
        <div class="form-row">
          <div class="field">
            <label>First Name *</label>
            <input v-model="form.first_name" type="text" required />
          </div>
          <div class="field">
            <label>Last Name</label>
            <input v-model="form.last_name" type="text" />
          </div>
        </div>

        <div class="form-row">
          <div class="field">
            <label>Email Address</label>
            <input :value="form.email" type="email" disabled class="disabled-input" title="Contact Admin to change email" />
          </div>
          <div class="field">
            <label>Phone Number *</label>
            <input v-model="form.phone_no" type="tel" required />
          </div>
        </div>

        <div class="field full">
          <label>Address</label>
          <input v-model="form.address" type="text" placeholder="City, State, Country" />
        </div>

        <hr class="divider" />

        <h3 class="group-title">Professional Details</h3>
        <div class="form-row">
          <div class="field">
            <label>Years of Experience</label>
            <input v-model.number="form.experience" type="number" min="0" />
          </div>
          <div class="field">
             </div>
        </div>

        <div class="field full">
          <label>Short Bio</label>
          <textarea v-model="form.bio" rows="3" placeholder="Tell us a bit about yourself..."></textarea>
        </div>

        <div class="field full">
          <label>Guide Description (Visible to Trekkers)</label>
          <textarea v-model="form.description" rows="4" placeholder="How would you describe your guiding style?"></textarea>
        </div>

        <div v-if="saveError" class="inline-error">{{ saveError }}</div>
        <div v-if="saveSuccess" class="inline-success">✅ Profile updated successfully!</div>

        <div class="form-actions">
          <button type="submit" class="primary-btn" :disabled="saving">
            {{ saving ? 'Saving…' : 'Save Changes' }}
          </button>
        </div>

      </form>
    </div>
  </div>
</template>

<script>
const emptyForm = () => ({
    first_name: '',
    last_name: '',
    email: '',
    phone_no: '',
    address: '',
    experience: 0,
    bio: '',
    description: ''
})

export default {
  name: 'StaffProfile',
  
  data() {
    return {
      form: emptyForm(),
      loading: true,
      saving: false,
      fetchError: null,
      saveError: null,
      saveSuccess: false
    }
  },

  methods: {
    token() { return localStorage.getItem('tma_token') },
    
    headers() {
      const t = this.token();
      if (!t) {
        this.$router.push('/');
        return {};
      }
      return {
        Authorization: `Bearer ${t}`,
        'Content-Type': 'application/json'
      }
    },

    async loadProfile() {
      this.loading = true;
      this.fetchError = null;
      this.saveSuccess = false;

      try {
        const res = await fetch('/staff/profile', {
          method: 'GET',
          headers: this.headers()
        });

        if (res.status === 401) { this.$router.push('/'); return; }
        if (!res.ok) throw new Error('Failed to load profile data');

        const data = await res.json();
        
        this.form = {
          first_name: data.first_name || '',
          last_name: data.last_name || '',
          email: data.email || '',
          phone_no: data.phone_no || '',
          address: data.address || '',
          experience: data.experience || 0,
          bio: data.bio || '',
          description: data.description || ''
        };

      } catch (e) {
        this.fetchError = e.message;
      } finally {
        this.loading = false;
      }
    },

    async saveProfile() {
      this.saving = true;
      this.saveError = null;
      this.saveSuccess = false;

      try {
        const res = await fetch('/staff/profile', {
          method: 'PUT',
          headers: this.headers(),
          body: JSON.stringify(this.form)
        });

        const result = await res.json();

        if (!res.ok) throw new Error(result.error || 'Failed to update profile');

        this.saveSuccess = true;
        
        setTimeout(() => {
          this.saveSuccess = false;
        }, 4000);

      } catch (e) {
        this.saveError = e.message;
      } finally {
        this.saving = false;
      }
    }
  },

  mounted() {
    this.loadProfile();
  }
}
</script>

<style scoped>
.profile-container { max-width: 800px; margin: 0 auto; padding-bottom: 40px; }

.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-title  { font-size: 18px; font-weight: 600; color: #121619; margin: 0; }

.panel { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 24px 28px; }

.group-title { font-size: 14px; font-weight: 600; color: #1a6b42; margin: 0 0 16px 0; border-left: 3px solid #1a6b42; padding-left: 8px; }
.divider { border: none; border-top: 1px solid #dde1e7; margin: 30px 0; }

/* Form Grid */
.form-row { display: flex; gap: 16px; margin-bottom: 16px; }
.field { flex: 1; display: flex; flex-direction: column; }
.field.full { width: 100%; margin-bottom: 16px; }

label { font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 6px; }

input, textarea {
  padding: 10px 12px; font-family: 'IBM Plex Sans', sans-serif; font-size: 14px;
  border: 1px solid #dde1e7; border-radius: 6px; color: #121619; outline: none; transition: border-color 0.2s;
}
input:focus, textarea:focus { border-color: #1a6b42; box-shadow: 0 0 0 2px rgba(26, 107, 66, 0.1); }

.disabled-input { background-color: #f3f4f6; color: #6b7280; cursor: not-allowed; }

.form-actions { display: flex; justify-content: flex-end; margin-top: 24px; }

.primary-btn {
  padding: 10px 20px; background: #1a6b42; border: none; border-radius: 6px;
  color: #fff; font-family: 'IBM Plex Sans', sans-serif; font-size: 14px; font-weight: 500;
  cursor: pointer; transition: background 0.12s;
}
.primary-btn:hover:not(:disabled) { background: #155a36; }
.primary-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 14px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; font-weight: 600; margin-left: 10px; }

.inline-error   { color: #dc2626; font-size: 13px; background: #fef2f2; padding: 10px; border-radius: 6px; margin-bottom: 16px; border: 1px solid #fca5a5; }
.inline-success { color: #16a34a; font-size: 13px; background: #f0faf4; padding: 10px; border-radius: 6px; margin-bottom: 16px; border: 1px solid #bbf7d0; font-weight: 500; }

@media (max-width: 768px) {
  .form-row { flex-direction: column; gap: 0; }
  .field { margin-bottom: 16px; }
}
</style>