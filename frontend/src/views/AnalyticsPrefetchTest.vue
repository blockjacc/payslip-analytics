<template>
  <div class="p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">analytics prefetch test</h1>
    <div class="mb-4">
      <button @click="fetchSummary" class="bg-primary text-white px-4 py-2 rounded mr-2">fetch summary</button>
      <button @click="fetchDrilldown" class="bg-secondary text-white px-4 py-2 rounded">fetch drill-down</button>
    </div>
    <div v-if="loading" class="text-white">loading...</div>
    <div v-if="error" class="text-red-400">error: {{ error }}</div>
    <pre v-if="result" class="bg-gray-900 text-green-200 p-4 rounded overflow-x-auto max-h-[60vh]">{{ prettyResult }}</pre>
  </div>
</template>

<script>
export default {
  name: 'AnalyticsPrefetchTest',
  data() {
    return {
      loading: false,
      error: '',
      result: null
    }
  },
  computed: {
    prettyResult() {
      return JSON.stringify(this.result, null, 2);
    }
  },
  methods: {
    async fetchSummary() {
      this.loading = true;
      this.error = '';
      this.result = null;
      try {
        const fields = encodeURIComponent('["overtime_pay","night_diff","basic_pay","sunday_holiday"]');
        const url = `/api/analytics-prefetch/206/2025-03-03/2025-05-17/separate?fields=${fields}&location_id=126`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(await response.text());
        this.result = await response.json();
      } catch (err) {
        this.error = err.message || err;
      } finally {
        this.loading = false;
      }
    },
    async fetchDrilldown() {
      this.loading = true;
      this.error = '';
      this.result = null;
      try {
        const fields = encodeURIComponent('["overtime_pay","night_diff","basic_pay","sunday_holiday"]');
        const url = `/api/analytics-prefetch/206/2025-03-03/2025-05-17/separate?fields=${fields}&location_id=126&drilldown=true`;
        const response = await fetch(url);
        if (!response.ok) throw new Error(await response.text());
        this.result = await response.json();
      } catch (err) {
        this.error = err.message || err;
      } finally {
        this.loading = false;
      }
    }
  }
}
</script>

<style scoped>
.bg-primary { background: #10b981; }
.bg-secondary { background: #6366f1; }
</style> 