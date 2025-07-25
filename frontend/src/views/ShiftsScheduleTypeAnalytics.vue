<template>
  <div class="p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shifts schedule type analytics</h1>
    <div class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl">company: {{ companyName || companyId }}</h3>
        </div>
        <div class="flex justify-end mb-4">
          <button
            class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500"
            @click="downloadCSV"
          >
            download csv
          </button>
        </div>
        <div v-if="loading" class="text-center text-gray-300 py-8">Loading...</div>
        <div v-else-if="error" class="text-center text-red-400 py-8">{{ error }}</div>
        <div v-else>
          <div v-if="chartData.labels.length" class="h-[60vh] mb-12 flex flex-col items-center justify-center">
            <Bar :data="chartData" :options="chartOptions" />
          </div>
          <div v-else class="text-center text-gray-300 py-8">No active schedule types found.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { getLogYAxisConfig, getYAxisStartAndFirstTick, getSimpleYAxis, getUnifiedStackedBarChart } from '../utils/chartAxis';
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend)

export default {
  name: 'ShiftsScheduleTypeAnalytics',
  components: { Bar },
  data() {
    return {
      companyId: '',
      companyName: '',
      scheduleType: '',
      chartData: null,
      chartOptions: null,
      loading: false,
      error: '',
      periods: [],
      analyticsPrefetchData: null
    }
  },
  computed: {
    chartColors() {
      const palette = [
        '#4a90e2', '#e74c3c', '#f1c40f', '#24c2ab', '#9b59b6', '#2ecc71', '#e67e22', '#8e44ad', '#b1bacd', '#c0392b'
      ];
      return this.scheduleTypes.map((_, idx) => palette[idx % palette.length]);
    },
    chartData() {
      if (!this.scheduleTypes.length) return { labels: [], datasets: [] };
      // Use unified chart configuration with per-period stacking
      const { chartData } = getUnifiedStackedBarChart(
        this.scheduleTypes,
        'count',
        'work_type_name',
        this.chartColors,
        { 
          chartName: 'Shifts Schedule Types',
          showLegend: true,
          legendPosition: 'right',
          fontSize: 14,
          fontFamily: 'Open Sans',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          perPeriodStacking: true
        }
      );
      return chartData;
    },
    chartOptions() {
      if (!this.scheduleTypes.length) return {};
      // Use unified chart configuration with per-period stacking
      const { chartOptions } = getUnifiedStackedBarChart(
        this.scheduleTypes,
        'count',
        'work_type_name',
        this.chartColors,
        { 
          chartName: 'Shifts Schedule Types',
          showLegend: true,
          legendPosition: 'right',
          fontSize: 14,
          fontFamily: 'Open Sans',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1,
          perPeriodStacking: true
        }
      );
      return chartOptions;
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    if (!this.companyId) {
      this.$router.push('/');
      return;
    }
    this.fetchScheduleTypes();
  },
  methods: {
    async fetchScheduleTypes() {
      this.loading = true;
      this.error = null;
      try {
        const res = await fetch(`/api/shifts/schedule-type-counts/${this.companyId}`);
        const data = await res.json();
        if (!res.ok || data.error) throw new Error(data.error || 'Failed to fetch schedule types');
        this.scheduleTypes = data.schedule_types || [];
      } catch (err) {
        this.error = err.message || 'Failed to fetch schedule types';
        this.scheduleTypes = [];
      } finally {
        this.loading = false;
      }
    },
    downloadCSV() {
      let csv = 'Schedule Type,Count\n';
      this.scheduleTypes.forEach(type => {
        csv += `${type.work_type_name},${type.count}\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `shifts_schedule_types_${this.companyId}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }
  }
}
</script> 