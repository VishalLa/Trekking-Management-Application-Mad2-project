<template>
  <div>
    <SharedTrekList role="TREKKER" />
  </div>
</template>

<script>
import SharedTrekList from '@/components/shared/SharedTrekList.vue';
export default { 
  name: 'TrekList',
  components: { SharedTrekList }
}
</script>
