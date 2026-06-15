<template>
    <div class="page">
        <div class="card">

            <h1 class="title">Sign in</h1>
            <p class="subtitle">Trekking Management Application</p>

            <div v-if="errorMessage" class="alert">{{ errorMessage }}</div>

            <form @submit.prevent="handleLogin" novalidate>

                <!-- Email -->
                <div class="field" :class="{ error: errors.email }">
                <label for="email">Email</label>
                <input
                    id="email"
                    v-model="form.email"
                    type="email"
                    placeholder="you@example.com"
                    autocomplete="email"
                    :disabled="loading"
                    @blur="validateField('email')"
                />
                <span v-if="errors.email" class="field-msg">{{ errors.email }}</span>
                </div>

                <!-- Password -->
                <div class="field" :class="{ error: errors.password }">
                <label for="password">Password</label>
                <div class="input-row">
                    <input
                    id="password"
                    v-model="form.password"
                    :type="showPassword ? 'text' : 'password'"
                    placeholder="••••••••"
                    autocomplete="current-password"
                    :disabled="loading"
                    @blur="validateField('password')"
                    />
                    <button type="button" class="eye" @click="showPassword = !showPassword" tabindex="-1">
                    {{ showPassword ? 'Hide' : 'Show' }}
                    </button>
                </div>
                <span v-if="errors.password" class="field-msg">{{ errors.password }}</span>
                </div>

                <!-- Role -->
                <!-- <div class="field">
                <label>Role</label>
                    <div class="roles">
                        <button
                        v-for="r in roles"
                        :key="r.value"
                        type="button"
                        class="role-btn"
                        :class="{ active: form.role === r.value }"
                        :disabled="loading"
                        @click="form.role = r.value"
                        >
                        {{ r.label }}
                        </button>
                    </div>
                </div> -->

                <button type="submit" class="submit" :disabled="loading">
                {{ loading ? 'Signing in…' : 'Sign in' }}
                </button>

            </form>

            <div class="footer-links">
                <a href="#" @click.prevent>Forgot password?</a>
                <span>·</span>
                <a href="#" @click.prevent="$router.push('/register')">Register</a>
            </div>
        </div>

    </div>
</template>>


<script>
export default {
    name: "LoginPage",
    data() {
        return {
            form: {email: '', password: '', role: 'ADMIN'},
            errors: {},
            errorMessage: '',
            loading: false,
            showPassword: false,
        }
    },

    methods: {
        validateField(field) {
            if (field === 'email') {
                if (!this.form.email) this.errors.email = "Email is required"

                else if ((!/\S+@\S+\.\S+/.test(this.form.email))) this.errors.email == "Enter a valid email"

                else delete this.errors.email
            }

            if (field === "password") {
                if (!this.form.password) this.errors.password = "Password is required"

                else if (this.form.password.length < 8) this.errors.password = "At least 8 characters"

                else delete this.errors.password
            }
        },

        async handleLogin() {
            this.validateField("email")
            this.validateField("password")

            if (Object.keys(this.errors).length) return 
                this.loading = true 
                this.errorMessage = ""

            try {
                const result = await fetch("/auth/login", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({email: this.form.email, password: this.form.password})
                })

                const data = await result.json()

                if (!result.ok) {this.errorMessage = data.message || "Invalid credentials."; return}

                localStorage.setItem("tma_token", data.token || data.access_token)
                localStorage.setItem("tma_role", data.role)
                localStorage.setItem('user_id', data.user_id)

                if (data.role === "ADMIN") this.$router.push('/dashboard')
                if (data.role === "STAFF") this.$router.push('/staff')
                // if (data.role === "TREKKER") this.$router.push('/trekker')

                const map = {
                    ADMIN: '/dashboard',
                    STAFF: '/staff',
                    TREKKER: '/user/treks'
                }

                this.$router.push(map[data.role] || '/')
            } catch {
                this.errorMessage = "Network error. Please try again."
            } finally{
                this.loading = false
            }
        }
    }
}
</script>


<style scoped>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

.page { min-height: 100vh; background: #9eaece; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Sans', sans-serif; padding: 24px 16px; }

.card { background: #ffffff; border: 1px solid #dde1e7; border-radius: 8px;  padding: 36px 32px; width: 100%; max-width: 400px; }

.title { font-size: 22px; font-weight: 600; color: #121619; margin-bottom: 4px; }
.subtitle { font-size: 13px; color: #697077; margin-bottom: 24px;
}

.alert { background: #fff1f1; border: 1px solid #ffc2c2; border-radius: 6px; padding: 10px 14px; font-size: 13px; color: #c62828; margin-bottom: 18px;
}

.field { margin-bottom: 16px; }
.field label { display: block; font-size: 13px; font-weight: 500; color: #393f45; margin-bottom: 6px;
}
.field input { width: 100%; height: 40px; padding: 0 12px; border: 1px solid #dde1e7; border-radius: 6px; font-family: inherit; font-size: 14px; color: #121619; background: #fff; outline: none; transition: border-color 0.15s;
}
.field input:focus { border-color: #1a6b42; }
.field input:disabled { background: #f4f5f7; cursor: not-allowed; }
.field.error input { border-color: #e53935; }
.field-msg { display: block; font-size: 12px; color: #c62828; margin-top: 4px; }

.input-row { display: flex; gap: 8px; }
.input-row input { flex: 1; }
.eye { height: 40px; padding: 0 12px; border: 1px solid #dde1e7; border-radius: 6px; background: #f4f5f7; font-family: inherit; font-size: 12px; font-weight: 500; color: #697077; cursor: pointer; white-space: nowrap;
}
.eye:hover { background: #e8eaed; }

.submit { width: 100%; height: 42px; margin-top: 8px; background: #1a6b42; border: none; border-radius: 6px; color: #fff; font-family: inherit; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.15s;
}
.submit:hover:not(:disabled) { background: #155a36; }
.submit:disabled { opacity: 0.6; cursor: not-allowed; }

.footer-links { display: flex; justify-content: center; align-items: center; gap: 10px; margin-top: 20px; font-size: 13px; color: #697077;
}
.footer-links a { color: #1a6b42; text-decoration: none;
}
.footer-links a:hover { text-decoration: underline; }

@media (max-width: 480px) {
    .card { padding: 28px 20px; }
}

</style>