<template>
  <span class="badge" :style="badgeStyle">{{ status }}</span>
</template>

<script>
const COLOR_MAPS = {
  user: {
    ACTIVE:    { bg: '#f0fdf4', color: '#15803d' },
    SUSPENDED: { bg: '#fef2f2', color: '#b91c1c' },
  },
  trek: {
    PENDING:  { bg: '#fffbeb', color: '#b45309' },
    APPROVED: { bg: '#eff6ff', color: '#1d4ed8' },
    OPEN:     { bg: '#f0fdf4', color: '#15803d' },
    CLOSED:   { bg: '#fef2f2', color: '#b91c1c' },
    COMPLETE: { bg: '#f9fafb', color: '#6b7280' },
  },
  booking: {
    BOOKED:    { bg: '#f0fdf4', color: '#15803d' },
    CANCELLED: { bg: '#fef2f2', color: '#b91c1c' },
    COMPLETED: { bg: '#eff6ff', color: '#1d4ed8' },
  },
  difficulty: {
    EASY:   { bg: '#f0fdf4', color: '#15803d' },
    MEDIUM: { bg: '#fffbeb', color: '#b45309' },
    HARD:   { bg: '#fef2f2', color: '#b91c1c' },
  }
}

export default {
  name: 'StatusBadge',
  props: {
    status: { type: String, default: '' },
    type:   { type: String, default: 'user' }
  },
  computed: {
    badgeStyle() {
      const map = COLOR_MAPS[this.type] || {}
      const colors = map[this.status] || { bg: '#f3f4f6', color: '#6b7280' }
      return {
        background: colors.bg,
        color:      colors.color,
      }
    }
  }
}
</script>

<style scoped>
.badge {
  display: inline-block;
  font-family: 'IBM Plex Sans', sans-serif;
  font-size: 11px;
  font-weight: 500;
  padding: 3px 9px;
  border-radius: 4px;
  white-space: nowrap;
  letter-spacing: 0.02em;
}
</style>
