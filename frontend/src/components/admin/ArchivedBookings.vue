<template>
  <div class="archive-container">
    <div class="section-header">
      <h2 class="section-title">🗄️ Historical Booking Archive</h2>
      <div class="header-right">
        <button class="primary-btn outline" @click="load">↻ Refresh</button>
      </div>
    </div>

    <p v-if="loading" class="state-msg">Loading historical records…</p>
    <div v-else-if="error" class="state-error">
      {{ error }}
      <button @click="load" class="retry-link">Retry</button>
    </div>
    <p v-else-if="archives.length === 0" class="state-msg">No archived bookings found.</p>

    <div v-else class="table-wrapper">
      <table class="archive-table">
        <thead>
          <tr>
            <th>Trekker</th>
            <th>Trek Name</th>
            <th>Historical Dates</th>
            <th>Booked On</th>
            <th>Seats</th>
            <th>Status</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="record in archives" :key="record.archive_id">
            <td>
              <div class="user-name">{{ record.user_name }}</div>
              <div class="user-email">{{ record.user_email }}</div>
            </td>
            <td class="fw-500">{{ record.trek_name }}</td>
            <td class="dates">{{ record.historical_start_date }} → {{ record.historical_end_date }}</td>
            <td class="text-muted">{{ record.booking_date }}</td>
            <td>{{ record.seats }}</td>
            <td>
              <span class="status-badge" :class="record.status.toLowerCase()">
                {{ record.status }}
              </span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ArchivedBookings',
  data() {
    return {
      archives: [],
      loading: false,
      error: null
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

    async load() {
      this.loading = true;
      this.error = null;

      try {
        const res = await fetch('/admin/bookings/archive', { headers: this.headers() });
        
        if (res.status === 401) { this.$router.push('/'); return; }
        if (!res.ok) throw new Error(`Server error ${res.status}`);

        const payload = await res.json();
        this.archives = payload.data || [];

      } catch (e) {
        this.error = e.message;
      } finally {
        this.loading = false;
      }
    }
  },
  mounted() {
    this.load();
  }
}
</script>

<style scoped>
.archive-container { padding: 20px; background: #fff; border-radius: 8px; border: 1px solid #dde1e7; }
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-title  { font-size: 18px; font-weight: 600; color: #121619; margin: 0; }
.header-right   { display: flex; gap: 10px; }

.primary-btn.outline { background: #fff; color: #1a6b42; border: 1px solid #1a6b42; padding: 6px 14px; border-radius: 6px; cursor: pointer; font-weight: 500; }
.primary-btn.outline:hover { background: #f0faf4; }

.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 14px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; margin-bottom: 16px; }

.table-wrapper { overflow-x: auto; }
.archive-table { width: 100%; border-collapse: collapse; text-align: left; font-size: 13px; }
.archive-table th { background: #f9fafb; padding: 12px 16px; color: #6b7280; font-weight: 600; border-bottom: 1px solid #dde1e7; }
.archive-table td { padding: 12px 16px; border-bottom: 1px solid #dde1e7; color: #374151; vertical-align: middle; }
.archive-table tr:hover { background-color: #f8fafc; }

.user-name { font-weight: 600; color: #111827; }
.user-email { font-size: 11px; color: #6b7280; margin-top: 2px; }
.fw-500 { font-weight: 500; }
.text-muted { color: #6b7280; }
.dates { font-family: monospace; font-size: 12px; background: #f3f4f6; padding: 4px 8px; border-radius: 4px; }

.status-badge { padding: 4px 8px; border-radius: 12px; font-size: 11px; font-weight: 600; }
.status-badge.completed { background: #e7f5ee; color: #1a6b42; }
.status-badge.cancelled { background: #fef2f2; color: #dc2626; }
.status-badge.booked { background: #eff6ff; color: #2563eb; }
</style>
