<template>
  <div>
    <div class="section-header">
      <h2 class="section-title">Reports & Archives</h2>
      <div class="header-actions">
        <button v-if="activeTab === 'overview'" class="primary-btn outline" @click="load" :disabled="loading">
          {{ loading ? 'Refreshing…' : '↻ Refresh' }}
        </button>

        <button class="primary-btn" @click="downloadBookingReport" :disabled="downloading">
          {{ downloading ? '⏳ Generating CSV...' : '📥 Download CSV Report' }}
        </button>
      </div>
    </div>

    <div class="report-tabs">
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'overview' }" 
        @click="activeTab = 'overview'"
      >
        📊 Dashboard Overview
      </button>
      
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'archives' }" 
        @click="activeTab = 'archives'"
      >
        🗄️ Historical Archives
      </button>
      
      <button 
        class="tab-btn" 
        :class="{ active: activeTab === 'charts' }" 
        @click="activeTab = 'charts'"
      >
        📈 Archive Charts
      </button>
    </div>

    <div v-if="activeTab === 'overview'">
      <p v-if="loading && !stats" class="state-msg">Loading report data…</p>

      <div v-else-if="error" class="state-error">
        {{ error }}
        <button @click="load" class="retry-link">Retry</button>
      </div>

      <template v-else-if="stats">
        <div class="kpi-grid">
          <div class="kpi-card" v-for="k in kpiCards" :key="k.label">
            <div class="kpi-label">{{ k.label }}</div>
            <div class="kpi-value">{{ k.value }}</div>
            <div class="kpi-sub">{{ k.sub }}</div>
          </div>
        </div>

        <div class="panels-grid">
          <div class="panel">
            <h3 class="panel-title">Trek Status</h3>
            <div class="bar-list">
              <div v-for="item in trekStatusBars" :key="item.label" class="bar-item">
                <div class="bar-top">
                  <span class="dot" :style="`background:${item.color}`"></span>
                  <span class="bar-label">{{ item.label }}</span>
                  <span class="bar-count">{{ item.count }}</span>
                </div>
                <div class="bar-track">
                  <div class="bar-fill" :style="`width:${item.pct}%; background:${item.color}`"></div>
                </div>
              </div>
            </div>
          </div>

          <div class="panel">
            <h3 class="panel-title">Booking Status</h3>
            <div class="stat-list">
              <div v-for="item in bookingItems" :key="item.label" class="stat-row">
                <div class="stat-left">
                  <span class="dot" :style="`background:${item.color}`"></span>
                  <span class="stat-label">{{ item.label }}</span>
                </div>
                <span class="stat-val">{{ item.count }}</span>
              </div>
            </div>
          </div>

          <div class="panel">
            <h3 class="panel-title">Trek Difficulty</h3>
            <div class="stat-list">
              <div v-for="d in difficultyRows" :key="d.label" class="stat-row">
                <StatusBadge :status="d.label" type="difficulty" />
                <span class="stat-val">{{ d.count }} treks</span>
              </div>
            </div>
          </div>

          <div class="panel">
            <h3 class="panel-title">User Metrics</h3>
            <div class="metric-list">
              <div v-for="m in userMetrics" :key="m.label" class="metric-row">
                <span class="metric-label">{{ m.label }}</span>
                <span class="metric-val">{{ m.value }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="panel full-panel">
          <h3 class="panel-title">Top 5 Revenue Generators</h3>
          <table class="rev-table">
            <thead>
              <tr>
                <th>#</th>
                <th>Trek Name</th>
                <th>Bookings</th>
                <th>Revenue</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(t, i) in stats.trek_metrics.top_5_revenue_generators" :key="t.id">
                <td class="rank-cell">{{ i + 1 }}</td>
                <td class="name-cell">{{ t.name }}</td>
                <td><span class="count-pill">{{ t.total_bookings }}</span></td>
                <td class="rev-cell">₹{{ t.total_revenue.toLocaleString('en-IN') }}</td>
              </tr>
              <tr v-if="!stats.trek_metrics.top_5_revenue_generators.length">
                <td colspan="4" class="empty-row">No data yet.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </template>
    </div>

    <div v-else-if="activeTab === 'archives'">
      <ArchivedBookings />
    </div>

    <div v-else-if="activeTab === 'charts'">
      <ArchivedHistoricalReport />
    </div>

  </div>
</template>


<script>
import StatusBadge from '@/components/shared/StatusBadge.vue'
import ArchivedBookings from '@/components/admin/ArchivedBookings.vue' 
import ArchivedHistoricalReport from '@/components/admin/ArchivedHistoricalReport.vue' 

export default {
  name: 'ReportView',
  components: { StatusBadge, ArchivedBookings, ArchivedHistoricalReport }, 

  data() {
    return {
      activeTab: 'overview',
      stats: null,
      loading: false,
      error: null,
      downloading: false
    }
  },

  computed: {
    kpiCards() {
      if (!this.stats) return []
      const o = this.stats.platform_overview
      return [
        { 
          label: 'Total Revenue',  
          value: '₹' + o.total_revenue.toLocaleString('en-IN', { maximumFractionDigits: 0 }), 
          sub: 'All paid bookings' 
        },
        { 
          label: 'Total Bookings', 
          value: o.total_bookings, 
          sub: (this.stats.booking_metrics.by_status.BOOKED || 0) + ' active'
        },
        { 
          label: 'Total Treks',    
          value: o.total_treks,    
          sub: (this.stats.trek_metrics.by_status.OPEN   || 0) + ' open now'
        },
        { 
          label: 'Total Trekkers', 
          value: this.stats.user_metrics.total_trekkers, 
          sub: this.stats.user_metrics.total_staff + ' staff'
        },
      ]
    },

    trekStatusBars() {
      if (!this.stats) return []

      const colors = { PENDING: '#f59e0b', APPROVED: '#3b82f6', OPEN: '#16a34a', CLOSED: '#ef4444', COMPLETE: '#6b7280' }
      const total = this.stats.platform_overview.total_treks || 1

      return Object.entries(this.stats.trek_metrics.by_status).map(([k, v]) => ({
        label: k, count: v, color: colors[k] || '#9ca3af',
        pct: Math.round((v / total) * 100)
      }))
    },

    bookingItems() {
      if (!this.stats) return []
      const colors = { 
        BOOKED: '#16a34a', 
        CANCELLED: '#dc2626', 
        COMPLETED: '#2563eb' 
      }

      return Object.entries(this.stats.booking_metrics.by_status).map(([k, v]) => ({
        label: k, count: v, color: colors[k] || '#6b7280'
      }))
    },

    difficultyRows() {
      if (!this.stats) return []
      const d = this.stats.trek_metrics.by_difficulty
      return [
        { label: 'EASY',   count: d.EASY   || 0 },
        { label: 'MEDIUM', count: d.MEDIUM || 0 },
        { label: 'HARD',   count: d.HARD   || 0 },
      ]
    },

    userMetrics() {
      if (!this.stats) return []
      const u = this.stats.user_metrics
      return [
        { label: 'Total Trekkers',  value: u.total_trekkers },
        { label: 'Total Staff',     value: u.total_staff },
        { label: 'Total Assignments', value: u.total_assignments },
        { label: 'Avg Staff / Trek',  value: this.stats.trek_metrics.average_staff_per_trek },
      ]
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

    async load() {
      this.loading = true
      this.error = null

      try {
        const res = await fetch('/admin/reports/dashboard', { headers: this.headers() })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)

        const data = await res.json()
        this.stats = data.data || data

      } catch (e) {
        this.error = e.message
      } finally {
        this.loading = false
      }
    },

    async downloadBookingReport() {
      this.downloading = true

      try {
        const triggerRes = await fetch('/admin/export/bookings/trigger', {
          method: 'POST',
          headers: this.headers() 
        })
        
        if (!triggerRes.ok){
          throw new Error("Failed to start export task")
        }

        const { task_id } = await triggerRes.json();

        const pollTimer = setInterval(async () => {
          const statusRes = await fetch(`/admin/export/bookings/status/${task_id}`, {
            method: 'GET',
            headers: this.headers()
          })

          if (statusRes.status === 202) {
            console.log("Still generating...")
          } else if (statusRes.status === 200) {
            clearInterval(pollTimer)

            const blob = await statusRes.blob()
            const url = window.URL.createObjectURL(blob)
            const a = document.createElement('a')

            a.style.display = 'none'
            a.href = url 
            a.download = "Master_Booking_Report.csv"
            document.body.appendChild(a)
            a.click()

            window.URL.revokeObjectURL(url)
            a.remove()

            this.downloading = false
          } else {
            clearInterval(pollTimer)
            this.downloading = false 
            alert("Background export failed on the server.")
          }
        }, 2000)

      } catch (error) {
        this.downloading = false
        alert("Download failed: " + error.message)
      }
    }
  },

  mounted() { this.load() }
}
</script>

<style scoped>
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 20px; }
.section-title  { font-size: 18px; font-weight: 600; color: #121619; }
.header-actions { display: flex; gap: 10px; }

/* ── Tab Navigation Styles ── */
.report-tabs {
  display: flex; gap: 10px; margin-bottom: 24px;
  border-bottom: 1px solid #dde1e7; padding-bottom: 10px;
}
.tab-btn {
  background: none; border: none; padding: 8px 16px;
  font-family: 'IBM Plex Sans', sans-serif; font-size: 14px; font-weight: 500;
  color: #6b7280; cursor: pointer; border-radius: 6px;
  transition: all 0.2s;
}
.tab-btn:hover { background: #f3f4f6; color: #121619; }
.tab-btn.active {
  background: #e7f5ee; color: #1a6b42; font-weight: 600;
}

/* Button Styles */
.primary-btn {
  padding: 8px 16px; background: #1a6b42; border: 1px solid #1a6b42; border-radius: 6px;
  color: #fff; font-family: 'IBM Plex Sans', sans-serif; font-size: 13px; font-weight: 500;
  cursor: pointer; transition: background 0.12s;
}
.primary-btn.outline { background: #fff; color: #1a6b42; }
.primary-btn.outline:hover { background: #f0faf4; }
.primary-btn:hover:not(:disabled):not(.outline) { background: #155a36; }
.primary-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 13px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; display: flex; gap: 10px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; }

/* ── KPI Grid ── */
.kpi-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; margin-bottom: 20px; }
.kpi-card { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 16px 18px; }
.kpi-label { font-size: 11.5px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: #6b7280; margin-bottom: 8px; }
.kpi-value { font-size: 24px; font-weight: 600; color: #121619; margin-bottom: 4px; }
.kpi-sub   { font-size: 12px; color: #9ca3af; }

/* ── Panels grid ── */
.panels-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 14px; margin-bottom: 14px; }
.panel { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 18px 20px; }
.full-panel { margin-bottom: 0; }
.panel-title { font-size: 13.5px; font-weight: 600; color: #121619; margin-bottom: 14px; }

/* Bar chart */
.bar-list { display: flex; flex-direction: column; gap: 10px; }
.bar-top  { display: flex; align-items: center; gap: 7px; margin-bottom: 5px; }
.dot      { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.bar-label { font-size: 12.5px; color: #4b5563; flex: 1; }
.bar-count { font-size: 13px; font-weight: 500; color: #121619; }
.bar-track { height: 5px; background: #f3f4f6; border-radius: 3px; overflow: hidden; }
.bar-fill  { height: 100%; border-radius: 3px; }

/* Stat list */
.stat-list { display: flex; flex-direction: column; gap: 8px; }
.stat-row  { display: flex; align-items: center; justify-content: space-between; padding: 9px 10px; border: 1px solid #f3f4f6; border-radius: 6px; }
.stat-left { display: flex; align-items: center; gap: 8px; }
.stat-label { font-size: 13px; color: #4b5563; }
.stat-val  { font-size: 15px; font-weight: 600; color: #121619; }

/* Metric list */
.metric-list { display: flex; flex-direction: column; }
.metric-row  { display: flex; justify-content: space-between; align-items: center; padding: 10px 0; border-bottom: 1px solid #f3f4f6; }
.metric-row:last-child { border-bottom: none; }
.metric-label { font-size: 13px; color: #6b7280; }
.metric-val   { font-size: 15px; font-weight: 600; color: #121619; }

/* Revenue table */
.rev-table { width: 100%; border-collapse: collapse; }
.rev-table th { font-size: 11.5px; font-weight: 500; text-transform: uppercase; letter-spacing: 0.05em; color: #9ca3af; text-align: left; padding: 6px 10px; border-bottom: 1px solid #f3f4f6; }
.rev-table td { padding: 11px 10px; font-size: 13.5px; color: #374151; border-bottom: 1px solid #f9fafb; }
.rev-table tr:last-child td { border-bottom: none; }
.rev-table tr:hover td { background: #f9fafb; }
.rank-cell  { font-weight: 600; color: #9ca3af; width: 32px; }
.name-cell  { font-weight: 500; color: #121619; }
.count-pill { background: #f0faf4; color: #15803d; font-size: 12px; font-weight: 500; padding: 2px 10px; border-radius: 20px; }
.rev-cell   { font-weight: 600; color: #121619; }
.empty-row  { text-align: center; color: #9ca3af; padding: 20px; }

@media (max-width: 900px) {
  .kpi-grid    { grid-template-columns: repeat(2, 1fr); }
  .panels-grid { grid-template-columns: 1fr; }
}
</style>
