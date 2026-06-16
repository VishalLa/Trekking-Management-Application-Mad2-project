<template>
  <div class="report-dashboard">
    <div class="section-header">
      <h2 class="section-title">Historical Analytics</h2>
    </div>

    <p v-if="loading" class="state-msg">Crunching historical data…</p>
    <div v-else-if="error" class="state-error">{{ error }}</div>

    <div v-else class="dashboard-grid">
      
      <div class="chart-card wide">
        <h3>Monthly Revenue Tracking (₹)</h3>
        <canvas ref="revenueChart"></canvas>
      </div>

      <div class="chart-card">
        <h3>Booking Volume</h3>
        <canvas ref="bookingChart"></canvas>
      </div>

      <div class="chart-card">
        <h3>Historical Status</h3>
        <canvas ref="statusChart"></canvas>
      </div>

      <div class="chart-card wide">
        <h3>All-Time Trek Performance</h3>
        <table class="data-table">
          <thead>
            <tr>
              <th>Trek Name</th>
              <th class="td-right">Total Bookings</th>
              <th class="td-right">Total Revenue (₹)</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="trek in reportData.trek_performance" :key="trek.trek_name">
              <td>{{ trek.trek_name }}</td>
              <td class="td-right">{{ trek.total_bookings }}</td>
              <td class="td-right success">₹ {{ formatPrice(trek.total_revenue) }}</td>
            </tr>
          </tbody>
        </table>
      </div>

    </div>
  </div>
</template>

<script>
import { Chart, registerables } from 'chart.js'
Chart.register(...registerables)

export default {
  name: 'ArchivedHistoricalReport',
  
  data() {
    return {
      loading: true,
      error: null,
      reportData: null,
      charts: []
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

    formatPrice(price) {
      return Number(price).toLocaleString('en-IN')
    },

    async loadData() {
      try {
        const res = await fetch('/admin/reports/historical', { headers: this.headers() })
        if (!res.ok) throw new Error("Failed to load report data")
        
        this.reportData = await res.json()
        this.loading = false;
        this.$nextTick(() => {
          setTimeout(() => {
            this.renderCharts()
          }, 50)
        })

      } catch (e) {
        this.error = e.message
        this.loading = false;
      }
    },

    renderCharts() {
      this.charts.forEach(chart => chart.destroy())
      this.charts = []

      if (!this.$refs.revenueChart || !this.$refs.bookingChart || !this.$refs.statusChart) {
          console.warn("Canvas elements still not found in the DOM.");
          return;
      }

      // 1. Revenue Line Chart
      this.charts.push(new Chart(this.$refs.revenueChart, {
        type: 'line',
        data: {
          labels: this.reportData.labels,
          datasets: [{
            label: 'Revenue (₹)',
            data: this.reportData.revenue_data,
            borderColor: '#1a6b42',
            backgroundColor: 'rgba(26, 107, 66, 0.1)',
            fill: true,
            tension: 0.3
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      }));

      // 2. Bookings Bar Chart
      this.charts.push(new Chart(this.$refs.bookingChart, {
        type: 'bar',
        data: {
          labels: this.reportData.labels,
          datasets: [{
            label: 'Total Tickets Booked',
            data: this.reportData.booking_data,
            backgroundColor: '#3b82f6',
            borderRadius: 4
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      }));

      // 3. Status Doughnut Chart
      this.charts.push(new Chart(this.$refs.statusChart, {
        type: 'doughnut',
        data: {
          labels: this.reportData.status_labels,
          datasets: [{
            data: this.reportData.status_data,
            backgroundColor: ['#10b981', '#f59e0b', '#ef4444', '#6b7280']
          }]
        },
        options: { responsive: true, maintainAspectRatio: false }
      }));
    }
  },

  mounted() {
    this.loadData()
  },

  beforeUnmount() {
    this.charts.forEach(chart => chart.destroy())
  }
}
</script>

<style scoped>
.report-dashboard { padding-bottom: 40px; }
.section-header { margin-bottom: 20px; }
.section-title  { font-size: 18px; font-weight: 600; color: #121619; }

.dashboard-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

.chart-card.wide { grid-column: 1 / -1; }

.chart-card { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02) }

.chart-card h3 { font-size: 14px; font-weight: 600; color: #374151; margin: 0 0 16px 0; border-bottom: 1px solid #f3f4f6; padding-bottom: 10px; }

.chart-card { background: #fff; border: 1px solid #dde1e7; border-radius: 8px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.02); position: relative; }

.chart-card canvas {  height: 300px !important; width: 100% !important; }

.data-table { width: 100%; border-collapse: collapse; font-size: 13px; }
.data-table th { text-align: left; padding: 10px; color: #6b7280; border-bottom: 2px solid #dde1e7; }
.data-table td { padding: 10px; border-bottom: 1px solid #f3f4f6; color: #121619; }
.td-right { text-align: right !important; }
.success { color: #15803d; font-weight: 600; }

.state-msg { padding: 40px; text-align: center; color: #6b7280; }
.state-error { padding: 16px; background: #fef2f2; color: #b91c1c; border-radius: 6px; }

@media (max-width: 900px) {
  .dashboard-grid { grid-template-columns: 1fr; }
}
</style>
