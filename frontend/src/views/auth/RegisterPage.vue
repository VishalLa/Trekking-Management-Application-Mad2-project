<template>
    <div class="page">
        <div class="card">

            <h1 class="title">Create an Account</h1>
            <p class="subtitle">Join the Trekking Management Application</p>

            <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>
            <div v-if="successMessage" class="alert alert-success">{{ successMessage }}</div>

            <form @submit.prevent="handleRegister" novalidate v-if="!successMessage">

                <div class="input-row mb-16">
                    <div class="field w-50" :class="{ error: errors.first_name }">
                        <label for="first_name">First Name</label>
                        <input id="first_name" v-model="form.first_name" type="text" placeholder="Jane" :disabled="loading" @blur="validateField('first_name')" />
                        <span v-if="errors.first_name" class="field-msg">{{ errors.first_name }}</span>
                    </div>
                    
                    <div class="field w-50">
                        <label for="last_name">Last Name</label>
                        <input id="last_name" v-model="form.last_name" type="text" placeholder="Doe (Optional)" :disabled="loading" />
                    </div>
                </div>

                <div class="field" :class="{ error: errors.phone_no }">
                    <label for="phone_no">Phone Number</label>
                    <input id="phone_no" v-model="form.phone_no" type="tel" placeholder="+91 9999999999" :disabled="loading" @blur="validateField('phone_no')" />
                    <span v-if="errors.phone_no" class="field-msg">{{ errors.phone_no }}</span>
                </div>

                <div class="field" :class="{ error: errors.email }">
                    <label for="email">Email</label>
                    <input id="email" v-model="form.email" type="email" placeholder="you@example.com" autocomplete="email" :disabled="loading" @blur="validateField('email')" />
                    <span v-if="errors.email" class="field-msg">{{ errors.email }}</span>
                </div>

                <div class="field" :class="{ error: errors.password }">
                    <label for="password">Password</label>
                    <div class="input-row">
                        <input id="password" v-model="form.password" :type="showPassword ? 'text' : 'password'" placeholder="••••••••" autocomplete="new-password" :disabled="loading" @blur="validateField('password')" />
                        <button type="button" class="eye" @click="showPassword = !showPassword" tabindex="-1">
                            {{ showPassword ? 'Hide' : 'Show' }}
                        </button>
                    </div>
                    <span v-if="errors.password" class="field-msg">{{ errors.password }}</span>
                </div>

                <button type="submit" class="submit" :disabled="loading">
                    {{ loading ? 'Creating account…' : 'Register' }}
                </button>

            </form>

            <div class="footer-links">
                <span>Already have an account?</span>
                <a href="#" @click.prevent="$router.push('/')">Sign in</a>
            </div>
        </div>
    </div>
</template>

<script>
export default {
    name: "RegisterPage",
    data() {
        return {
            form: {
                first_name: '',
                last_name: '',
                phone_no: '',
                email: '',
                password: '',
                role: 'TREKKER'
            },
            errors: {},
            errorMessage: '',
            successMessage: '',
            loading: false,
            showPassword: false,
        }
    },

    methods: {
        validateField(field) {
            if (field === 'first_name') {
                if (!this.form.first_name.trim()) this.errors.first_name = "First name is required";
                else delete this.errors.first_name;
            }

            if (field === 'phone_no') {
                if (!this.form.phone_no.trim()) this.errors.phone_no = "Phone number is required";
                else if (this.form.phone_no.length < 10) this.errors.phone_no = "Enter a valid phone number";
                else delete this.errors.phone_no;
            }

            if (field === 'email') {
                if (!this.form.email) this.errors.email = "Email is required";
                else if (!/\S+@\S+\.\S+/.test(this.form.email)) this.errors.email = "Enter a valid email";
                else delete this.errors.email;
            }

            if (field === "password") {
                if (!this.form.password) this.errors.password = "Password is required";
                else if (this.form.password.length < 8) this.errors.password = "At least 8 characters required";
                else delete this.errors.password;
            }
        },

        async handleRegister() {
            ['first_name', 'phone_no', 'email', 'password'].forEach(f => this.validateField(f));

            if (Object.keys(this.errors).length) return;
            
            this.loading = true;
            this.errorMessage = "";
            this.successMessage = "";

            try {
                const result = await fetch("/auth/register", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(this.form)
                });

                const data = await result.json();

                if (!result.ok) {
                    this.errorMessage = data.message || data.error || "Registration failed.";
                    return;
                }

                this.successMessage = "Account created successfully! Please check your email to verify your account.";
                
                setTimeout(() => {
                    this.$router.push('/');
                }, 3000);

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
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.page { min-height: 100vh; background: #9eaece; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Sans', sans-serif; padding: 24px 16px; }
.card { background: #ffffff; border: 1px solid #dde1e7; border-radius: 8px; padding: 36px 32px; width: 100%; max-width: 450px; } /* Slightly wider for the name row */

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

.mb-16 { margin-bottom: 16px; }
.w-50 { width: 50%; }

.input-row { display: flex; gap: 12px; }
.input-row input { flex: 1; }
.eye { height: 40px; padding: 0 12px; border: 1px solid #dde1e7; border-radius: 6px; background: #f4f5f7; font-family: inherit; font-size: 12px; font-weight: 500; color: #697077; cursor: pointer; white-space: nowrap; }
.eye:hover { background: #e8eaed; }

.submit { width: 100%; height: 42px; margin-top: 8px; background: #1a6b42; border: none; border-radius: 6px; color: #fff; font-family: inherit; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.15s; }
.submit:hover:not(:disabled) { background: #155a36; }
.submit:disabled { opacity: 0.6; cursor: not-allowed; }

.footer-links { display: flex; justify-content: center; align-items: center; gap: 6px; margin-top: 20px; font-size: 13px; color: #697077; }
.footer-links a { color: #1a6b42; text-decoration: none; font-weight: 500;}
.footer-links a:hover { text-decoration: underline; }

@media (max-width: 480px) { .card { padding: 28px 20px; } .input-row { flex-direction: column; gap: 0;} .w-50 { width: 100%;} }
</style>
