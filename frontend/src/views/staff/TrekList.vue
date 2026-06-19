<template>
  <div>
    <SharedTrekList role="STAFF" />
  </div>
</template>

<script>
import SharedTrekList from '@/components/shared/SharedTrekList.vue';
export default { 
  name: 'TrekList',
  components: { SharedTrekList } 
}
</script>
