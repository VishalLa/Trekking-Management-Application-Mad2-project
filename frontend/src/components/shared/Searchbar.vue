<template>
  <div class="search-box">
    <svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">
      <circle cx="6.5" cy="6.5" r="5" stroke="#9ca3af" stroke-width="1.4"/>
      <path d="M10.5 10.5L14 14" stroke="#9ca3af" stroke-width="1.4" stroke-linecap="round"/>
    </svg>
    <input
      :value="modelValue"
      type="text"
      :placeholder="placeholder"
      class="search-input"
      @input="$emit('update:modelValue', $event.target.value)"
    />
  </div>
</template>

<script>
export default {
  name: 'SearchBar',
  props: {
    modelValue: { type: String, default: '' },
    placeholder: { type: String, default: 'Search…' }
  },
  emits: ['update:modelValue']
}
</script>

<style scoped>
.search-box {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 7px 12px;
  border: 1px solid #dde1e7;
  border-radius: 6px;
  background: #fff;
  font-family: 'IBM Plex Sans', sans-serif;
}
.search-input {
  border: none;
  outline: none;
  font-family: inherit;
  font-size: 13px;
  color: #374151;
  width: 200px;
  background: transparent;
}
.search-input::placeholder { color: #9ca3af; }
</style>
