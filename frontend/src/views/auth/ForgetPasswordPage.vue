<template>
    <div class="page">
        <div class="card">
            <h1 class="title">Reset Password</h1>
            <p class="subtitle">Choose how you want to recover your account.</p>

            <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

            <form @submit.prevent="handleRequest" v-if="!successMessage">
                
                <div class="method-toggle mb-16">
                    <button type="button" class="toggle-btn" :class="{ active: form.method === 'email' }" @click="form.method = 'email'">
                        Via Email
                    </button>
                    <button type="button" class="toggle-btn" :class="{ active: form.method === 'phone' }" @click="form.method = 'phone'">
                        Via Phone (SMS)
                    </button>
                </div>

                <div class="field" :class="{ error: errorField }">
                    <label :for="form.method">
                        {{ form.method === 'email' ? 'Email Address' : 'Phone Number' }}
                    </label>
                    <input 
                        :id="form.method" 
                        v-model="form.identifier" 
                        :type="form.method === 'email' ? 'email' : 'tel'" 
                        :placeholder="form.method === 'email' ? 'you@example.com' : '+91 9999999999'" 
                        :disabled="loading"
                    />
                    <span v-if="errorField" class="field-msg">{{ errorField }}</span>
                </div>

                <button type="submit" class="submit" :disabled="loading">
                    {{ loading ? 'Sending...' : 'Send Reset Instructions' }}
                </button>
            </form>

            <div class="footer-links">
                <a href="#" @click.prevent="$router.push('/')">← Back to Login</a>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "ForgetPasswordPage",
    data() {
        return {
            form: {
                method: 'email',
                identifier: '' 
            },
            errorField: '',
            errorMessage: '',
            successMessage: '',
            loading: false
        }
    },
    watch: {
        'form.method'() {
            this.form.identifier = '';
            this.errorField = '';
            this.errorMessage = '';
        }
    },
    methods: {
        async handleRequest() {
            this.errorField = '';
            this.errorMessage = '';

            if (!this.form.identifier.trim()) {
                this.errorField = `Please enter your ${this.form.method === 'email' ? 'email' : 'phone number'}.`;
                return;
            }

            this.loading = true;

            const payload = { method: this.form.method };
            if (this.form.method === 'email') {
                payload.email = this.form.identifier;
            } else {
                payload.phone_no = this.form.identifier;
            }

            try {
                const result = await fetch("/auth/forgot-password", { 
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await result.json();

                if (!result.ok) {
                    this.errorMessage = data.error || data.message || "Failed to send request.";
                    return;
                }

                if (this.form.method === 'email') {
                    this.successMessage = "If the email exists, a reset link has been sent to your inbox.";
                } 
                else if (this.form.method === 'phone') {
                    this.$router.push({
                        path: '/reset-password',
                        query: { method: 'phone', token: data.reset_token }
                    });
                }

            } catch (error) {
                this.errorMessage = "Network error. Please try again.";
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>

<style scoped>
/* Importing the shared styles from your Login page */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.page { min-height: 100vh; background: #9eaece; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Sans', sans-serif; padding: 24px 16px; }
.card { background: #ffffff; border: 1px solid #dde1e7; border-radius: 8px; padding: 36px 32px; width: 100%; max-width: 400px; }
.title { font-size: 22px; font-weight: 600; color: #121619; margin-bottom: 4px; }
.subtitle { font-size: 13px; color: #697077; margin-bottom: 24px; }
.alert { background: #fff1f1; border: 1px solid #ffc2c2; border-radius: 6px; padding: 10px 14px; font-size: 13px; color: #c62828; margin-bottom: 18px; }
.alert-success { background: #f0fdf4; border-color: #bbf7d0; color: #15803d; }
.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; font-weight: 500; color: #393f45; margin-bottom: 6px; }
.field input { width: 100%; height: 40px; padding: 0 12px; border: 1px solid #dde1e7; border-radius: 6px; font-family: inherit; font-size: 14px; color: #121619; background: #fff; outline: none; transition: border-color 0.15s; }
.field input:focus { border-color: #1a6b42; }
.field input:disabled { background: #f4f5f7; cursor: not-allowed; }
.field.error input { border-color: #e53935; }
.field-msg { display: block; font-size: 12px; color: #c62828; margin-top: 4px; }
.submit { width: 100%; height: 42px; margin-top: 8px; background: #1a6b42; border: none; border-radius: 6px; color: #fff; font-family: inherit; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.15s; }
.submit:hover:not(:disabled) { background: #155a36; }
.submit:disabled { opacity: 0.6; cursor: not-allowed; }
.footer-links { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px; font-size: 13px; color: #697077; }
.footer-links a { color: #1a6b42; text-decoration: none; font-weight: 500;}
.footer-links a:hover { text-decoration: underline; }
.mb-16 { margin-bottom: 16px; }

/* Custom toggle switch for Email vs Phone */
.method-toggle { display: flex; background: #f4f5f7; border-radius: 6px; padding: 4px; }
.toggle-btn { flex: 1; background: transparent; border: none; padding: 8px 0; font-size: 13px; font-weight: 500; color: #697077; cursor: pointer; border-radius: 4px; transition: all 0.2s; }
.toggle-btn.active { background: #fff; color: #1a6b42; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
</style>
