<template>
  <header class="topbar">
    <div class="topbar-left">
      <h1 class="topbar-title">{{ title }}</h1>
      <span class="topbar-date">{{ today }}</span>
    </div>
    <div class="topbar-right">
      <slot name="actions" />
    </div>
  </header>
</template>

<script>
export default {
  name: 'AppTopbar',
  props: {
    title: {
      type: String,
      default: 'Admin Dashboard'
    }
  },
  computed: {
    today() {
      return new Date().toLocaleDateString('en-IN', {
        weekday: 'long',
        day: 'numeric',
        month: 'long',
        year: 'numeric'
      })
    }
  }
}
</script>

<style scoped>
.topbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 14px 24px;
  background: #ffffff;
  border-bottom: 1px solid #dde1e7;
  flex-shrink: 0;
  font-family: 'IBM Plex Sans', sans-serif;
}

.topbar-left {
  display: flex;
  align-items: baseline;
  gap: 12px;
}
.topbar-title {
  font-size: 16px;
  font-weight: 600;
  color: #121619;
}
.topbar-date {
  font-size: 12px;
  color: #9ca3af;
}
.topbar-right {
  display: flex;
  align-items: center;
  gap: 10px;
}
</style>
