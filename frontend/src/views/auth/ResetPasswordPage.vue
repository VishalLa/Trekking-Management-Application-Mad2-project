<template>
    <div class="page">
        <div class="card">
            <h1 class="title">Set New Password</h1>
            <p class="subtitle">Please enter your new secure password below.</p>

            <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
            <div v-if="successMessage" class="alert alert-success">
                {{ successMessage }} <br><br>
                <button class="submit" @click="$router.push('/')">Go to Login</button>
            </div>

            <form @submit.prevent="handleReset" v-if="!successMessage">
                
                <div v-if="method === 'phone'" class="field">
                    <label for="otp">Enter 6-Digit OTP</label>
                    <input id="otp" v-model="form.otp" type="text" maxlength="6" placeholder="123456" :disabled="loading" required />
                    <span class="field-msg" style="color: #697077;">Check your phone for the code.</span>
                </div>

                <div class="field">
                    <label for="password">New Password</label>
                    <input id="password" v-model="form.new_password" type="password" placeholder="••••••••" :disabled="loading" required minlength="8" />
                </div>

                <div class="field" :class="{ error: passwordMismatch }">
                    <label for="confirm">Confirm Password</label>
                    <input id="confirm" v-model="form.confirm_password" type="password" placeholder="••••••••" :disabled="loading" required />
                    <span v-if="passwordMismatch" class="field-msg">Passwords do not match.</span>
                </div>

                <button type="submit" class="submit" :disabled="loading || passwordMismatch">
                    {{ loading ? 'Updating...' : 'Update Password' }}
                </button>
            </form>

        </div>
    </div>
</template>

<script>
export default {
    name: "ResetPasswordPage",
    data() {
        return {
            method: '',
            token: '',
            form: {
                otp: '',
                new_password: '',
                confirm_password: ''
            },
            errorMessage: '',
            successMessage: '',
            loading: false
        }
    },
    computed: {
        passwordMismatch() {
            if (this.form.confirm_password.length > 0) {
                return this.form.new_password !== this.form.confirm_password;
            }
            return false;
        }
    },
    mounted() {
        this.method = this.$route.query.method;
        this.token = this.$route.query.token;

        if (!this.method || !this.token) {
            this.errorMessage = "Invalid or missing reset token. Please request a new password reset link.";
        }
    },
    methods: {
        async handleReset() {
            if (this.passwordMismatch) return;
            if (this.form.new_password.length < 8) {
                this.errorMessage = "Password must be at least 8 characters.";
                return;
            }

            this.loading = true;
            this.errorMessage = '';

            const payload = {
                method: this.method,
                new_password: this.form.new_password
            };

            if (this.method === 'email') {
                payload.token = this.token;
            } else if (this.method === 'phone') {
                payload.reset_token = this.token;
                payload.otp = this.form.otp;
            }

            try {
                const result = await fetch("/auth/reset-password", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(payload)
                });

                const data = await result.json();

                if (!result.ok) {
                    this.errorMessage = data.error || data.message || "Failed to reset password.";
                    return;
                }
                this.successMessage = "Your password has been reset successfully!";
                
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
/* Re-using the exact same UI styles from the ForgetPassword page! */
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
</style>