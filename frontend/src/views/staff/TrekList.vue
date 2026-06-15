<template>
  <div>
    <div class="section-header">
      <h2 class="section-title">My Assigned Treks</h2>
      <div class="header-right">
        <SearchBar v-model="query" placeholder="Search my treks…" />
      </div>
    </div>

    <div class="filter-tabs">
      <button
        v-for="f in filters"
        :key="f.value"
        class="filter-tab"
        :class="{ active: statusFilter === f.value }"
        @click="statusFilter = f.value"
      >
        {{ f.label }}
        <span class="filter-count">{{ countByStatus(f.value) }}</span>
      </button>
    </div>

    <p v-if="loading" class="state-msg">Loading your assigned treks…</p>
    <div v-else-if="error" class="state-error">
      {{ error }}
      <button @click="load" class="retry-link">Retry</button>
    </div>
    <p v-else-if="filtered.length === 0" class="state-msg">You have no treks assigned to you right now.</p>

    <div v-else>
      <div
        v-for="trek in filtered"
        :key="trek.trek_id"
        class="trek-block"
        :class="{ expanded: expandedId === trek.trek_id }"
      >
        <div class="list-card">
          <div class="card-body">
            <div class="card-name">{{ trek.trek_name }}</div>
            <div class="card-meta">
              <span>📍 {{ trek.location }}</span>
              <span class="sep">·</span>
              <span>{{ trek.duration }} days</span>
              <span class="sep">·</span>
              <span style="font-weight: 600; color: #1a6b42;">🎟️ {{ trek.available_slots }} slots</span>
              <span class="sep">·</span>
              <span>{{ formatDate(trek.start_date) }} → {{ formatDate(trek.end_date) }}</span>
            </div>
          </div>

          <div class="card-actions">
            <StatusBadge :status="trek.difficulty" type="difficulty" />
            <StatusBadge :status="trek.status" type="trek" />

            <select
              class="action-select" 
              :value="trek.status" 
              @change="updateStatus(trek, $event.target.value)"
            >
              <option value="OPEN">Open</option>
              <option value="CLOSED">Close</option>
              <option value="COMPLETE">Complete</option>
            </select>

            <button class="action-btn btn-outline" @click="askUpdateSlots(trek)">
               Edit Slots
            </button>

            <button
              class="action-btn btn-bookings"
              :class="{ active: expandedId === trek.trek_id }"
              @click="togglePanel(trek.trek_id)"
            >
              📅 {{ expandedId === trek.trek_id ? 'Hide Bookings' : 'View Bookings' }}
              <span v-if="bookingCounts[trek.trek_id] !== undefined" class="booking-count-chip">
                {{ bookingCounts[trek.trek_id] }}
              </span>
            </button>
          </div>
        </div>

        <BookingModal 
          v-if="expandedId === trek.trek_id" 
          :trek="trek"
          role="STAFF" 
          @loaded="count => updateBookingCount(trek.trek_id, count)" 
        />

      </div>
    </div>
  </div>
</template>

<script>
import SearchBar     from '@/components/shared/SearchBar.vue'
import StatusBadge   from '@/components/shared/StatusBadge.vue'
import BookingModal  from '@/components/shared/BookingModal.vue'

export default {
  name: 'StaffTrekList',
  components: { SearchBar, StatusBadge, BookingModal },

  data() {
    return {
      treks: [],
      loading: false,
      error: null,
      query: '',
      statusFilter: 'ALL',
      
      filters: [
        { value: 'ALL',      label: 'All My Treks' },
        { value: 'OPEN',     label: 'Open' },
        { value: 'CLOSED',   label: 'Closed' },
        { value: 'COMPLETE', label: 'Completed' },
      ],

      expandedId: null,
      bookingCounts: {},    
    }
  },

  computed: {
    filtered() {
      let list = Array.isArray(this.treks) ? this.treks.slice() : []

      if (this.statusFilter !== 'ALL') list = list.filter(t => t.status === this.statusFilter)
      const q = this.query.toLowerCase()

      if (q) list = list.filter(t =>
        t.trek_name?.toLowerCase().includes(q) ||
        t.location?.toLowerCase().includes(q)
      )
      return list
    }
  },

  methods: {
    token() { return localStorage.getItem('tma_token') },
    
    userId() { return localStorage.getItem('user_id') }, 

    headers() { 
      const t = this.token();
      if (!t) {
        this.$router.push('/')
        return {};
      }
      return {
        Authorization: `Bearer ${t}`, 
        'Content-Type': 'application/json'
      }
     },

    formatDate(d) {
      if (!d) return '—'
      return new Date(d).toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' })
    },

    countByStatus(status) {
      const list = Array.isArray(this.treks) ? this.treks : []
      return status === 'ALL' ? list.length : list.filter(t => t.status === status).length
    },

    togglePanel(trekId) {
      if (this.expandedId === trekId) {
        this.expandedId = null
      } else {
        this.expandedId = trekId
      }
    },

    updateBookingCount(trekId, count) {
      this.bookingCounts[trekId] = count
    },

    async load() {
      this.loading = true; 
      this.error = null;

      const uid = this.userId();
      if (!uid) {
          this.error = "User session invalid. Please log in again.";
          this.loading = false;
          return;
      }

      try {
        const res = await fetch(`/staff/assigned-trek-list/${uid}`, { headers: this.headers() })

        if (res.status === 401) { this.$router.push('/'); return }
        if (!res.ok) throw new Error(`Server error ${res.status}`)

        const payload = await res.json()
        this.treks = Array.isArray(payload) ? payload : (payload.data || [])

      } catch (e) { 
        this.error = e.message 
      } finally { 
        this.loading = false 
      }
    },

    async updateStatus(trek, status) {
      try {
        const res = await fetch(`/staff/trek/${trek.trek_id}/${status}`, { 
            method: 'PUT', 
            headers: this.headers() 
        })
        if (!res.ok) throw new Error('Status update failed')
        trek.status = status
      } catch (e) { 
          alert(e.message) 
      }
    },

    async askUpdateSlots(trek) {
        const currentSlots = trek.available_slots;
        const input = prompt(`Update available slots for ${trek.trek_name}:`, currentSlots);
        
        if (input === null || input === "") return;
        
        const newSlots = parseInt(input, 10);
        if (isNaN(newSlots) || newSlots < 0) {
            alert("Please enter a valid number of slots.");
            return;
        }

        try {
            const res = await fetch(`/staff/trek/${trek.trek_id}/slots/${newSlots}`, {
                method: 'PUT',
                headers: this.headers()
            })
            
            trek.available_slots = newSlots;
        } catch (e) {
            alert(e.message)
        }
    }
  },

  mounted() { this.load() }
}
</script>

<style scoped>
.section-header { display: flex; align-items: center; justify-content: space-between; margin-bottom: 14px; }
.section-title  { font-size: 16px; font-weight: 600; color: #121619; }
.header-right   { display: flex; align-items: center; gap: 10px; }

.filter-tabs { display: flex; gap: 6px; margin-bottom: 16px; flex-wrap: wrap; }
.filter-tab { display: flex; align-items: center; gap: 6px; padding: 6px 12px; border: 1px solid #dde1e7; border-radius: 20px; background: #fff; font-family: 'IBM Plex Sans', sans-serif; font-size: 12.5px; color: #6b7280; cursor: pointer; transition: all 0.12s; }
.filter-tab:hover  { border-color: #1a6b42; color: #1a6b42; }
.filter-tab.active { background: #1a6b42; border-color: #1a6b42; color: #fff; }
.filter-count      { background: rgba(255,255,255,0.25); padding: 0 6px; border-radius: 10px; font-size: 11px; }
.filter-tab:not(.active) .filter-count { background: #f3f4f6; color: #9ca3af; }

.state-msg   { padding: 32px; text-align: center; color: #9ca3af; font-size: 13px; }
.state-error { padding: 12px 16px; background: #fef2f2; border: 1px solid #fca5a5; border-radius: 6px; color: #b91c1c; font-size: 13px; display: flex; gap: 10px; margin-bottom: 16px; }
.retry-link  { background: none; border: none; color: #b91c1c; font-size: 13px; cursor: pointer; text-decoration: underline; }

.trek-block { margin-bottom: 10px; border-radius: 8px; overflow: hidden; border: 1px solid #dde1e7; transition: border-color 0.12s; }
.trek-block:hover      { border-color: #b6c6d6; }
.trek-block.expanded   { border-color: #1a6b42; }

.list-card { display: flex; align-items: center; justify-content: space-between; gap: 16px; background: #fff; padding: 14px 16px; }
.card-body  { flex: 1; min-width: 0; }
.card-name  { font-size: 14px; font-weight: 500; color: #121619; margin-bottom: 4px; }
.card-meta  { font-size: 12px; color: #6b7280; display: flex; flex-wrap: wrap; gap: 4px; }
.sep        { color: #d1d5db; }

.card-actions { display: flex; align-items: center; gap: 8px; flex-shrink: 0; flex-wrap: wrap; justify-content: flex-end; }

.action-btn { display: inline-flex; align-items: center; gap: 5px; padding: 5px 12px; border-radius: 5px; font-family: 'IBM Plex Sans', sans-serif; font-size: 12px; font-weight: 500; cursor: pointer; white-space: nowrap; transition: all 0.12s; }
.btn-outline        { background: #fff; border: 1px solid #dde1e7; color: #374151; }
.btn-outline:hover  { background: #f4f5f7; }

.btn-bookings { background: #fff; border: 1px solid #dde1e7; color: #374151; }
.btn-bookings:hover { background: #f0faf4; border-color: #1a6b42; color: #1a6b42; }
.btn-bookings.active { background: #f0faf4; border-color: #1a6b42; color: #1a6b42; font-weight: 600; }
.booking-count-chip { background: #1a6b42; color: #fff; font-size: 10px; font-weight: 600; padding: 1px 6px; border-radius: 20px; min-width: 18px; text-align: center; }
.btn-bookings:not(.active) .booking-count-chip { background: #e5e7eb; color: #4b5563; }

.action-select { 
  padding: 6px 30px 6px 12px; 
  font-size: 13px; 
  font-weight: 600; 
  color: #374151; 
  background-color: #ffffff;
  border: 1px solid #dde1e7;
  border-radius: 6px;
  cursor: pointer;
  outline: none;
  transition: all 0.2s ease;
  appearance: none; 
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' fill='none' viewBox='0 0 24 24' stroke='%236b7280'%3E%3Cpath stroke-linecap='round' stroke-linejoin='round' stroke-width='2' d='M19 9l-7 7-7-7'%3E%3C/path%3E%3C/svg%3E");
  background-repeat: no-repeat;
  background-position: right 8px center;
  background-size: 14px;
}
.action-select:hover { background-color: #f9fafb; border-color: #d1d5db; }
.action-select:focus { border-color: #1a6b42; box-shadow: 0 0 0 2px rgba(26, 107, 66, 0.1); }

@media (max-width: 900px) {
  .list-card    { flex-direction: column; align-items: flex-start; }
  .card-actions { width: 100%; }
}
</style>
