<template>
    <div class="page">
        <div class="card text-center">
            <h1 class="title">Email Verification</h1>
            <p class="subtitle" v-if="loading">Please wait while we verify your account...</p>
            <p class="subtitle" v-else>Verification complete.</p>

            <div v-if="loading" class="verification-status">
                <div class="spinner"></div>
                <p>Verifying your secure token...</p>
            </div>

            <div v-else-if="successMessage" class="alert alert-success">
                {{ successMessage }}
                <br><br>
                <button class="submit" @click="$router.push('/')">Proceed to Login</button>
            </div>

            <div v-else-if="errorMessage" class="alert">
                {{ errorMessage }}
                <br><br>
                <button class="submit" style="background: #697077;" @click="$router.push('/')">
                    Back to Login
                </button>
            </div>

        </div>
    </div>
</template>

<script>
export default {
    name: "EmailVerifyPage",
    data() {
        return {
            loading: true,
            successMessage: '',
            errorMessage: ''
        }
    },
    async mounted() {
        await this.verifyToken();
    },
    methods: {
        async verifyToken() {
            const token = this.$route.query.token;

            if (!token) {
                this.loading = false;
                this.errorMessage = "Invalid request. No verification token found in the URL.";
                return;
            }

            try {
                const result = await fetch("/auth/verify-email", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ token: token })
                });

                const data = await result.json();

                if (!result.ok) {
                    this.errorMessage = data.error || data.message || "Verification failed. Your link may have expired.";
                    return;
                }

                this.successMessage = "Your email has been successfully verified! You can now log into your account.";

            } catch (error) {
                this.errorMessage = "Network error. Please check your connection and try again.";
            } finally {
                this.loading = false;
            }
        }
    }
}
</script>

<style scoped>
/* Importing the shared styles */
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Sans:wght@400;500;600&display=swap');
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
.page { min-height: 100vh; background: #9eaece; display: flex; align-items: center; justify-content: center; font-family: 'IBM Plex Sans', sans-serif; padding: 24px 16px; }
.card { background: #ffffff; border: 1px solid #dde1e7; border-radius: 8px; padding: 36px 32px; width: 100%; max-width: 400px; text-align: center; }
.title { font-size: 22px; font-weight: 600; color: #121619; margin-bottom: 4px; }
.subtitle { font-size: 13px; color: #697077; margin-bottom: 24px; }
.alert { background: #fff1f1; border: 1px solid #ffc2c2; border-radius: 6px; padding: 16px; font-size: 14px; color: #c62828; margin-bottom: 18px; line-height: 1.5; }
.alert-success { background: #f0fdf4; border-color: #bbf7d0; color: #15803d; }
.submit { width: 100%; height: 42px; background: #1a6b42; border: none; border-radius: 6px; color: #fff; font-family: inherit; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.15s; }
.submit:hover { opacity: 0.9; }

.verification-status { padding: 20px 0; color: #393f45; font-size: 14px; font-weight: 500;}
.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f4f5f7;
    border-top: 4px solid #1a6b42;
    border-radius: 50%;
    margin: 0 auto 16px auto;
    animation: spin 1s linear infinite;
}
@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
</style>
