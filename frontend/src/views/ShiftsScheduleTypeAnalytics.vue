<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-[#0f2027] via-[#2c5364] to-[#232526] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shifts schedule type analytics</h1>
    <div class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <div class="flex justify-end mb-4">
          <button
            class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500"
            @click="downloadCSV"
          >
            download csv
          </button>
        </div>
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl font-serif" style="font-weight: 500;">company id: {{ companyId }}</h3>
        </div>
        <h2 class="text-xl font-bold text-primary mb-8 text-left">schedule types (active)</h2>
        <div v-if="loading" class="text-center text-gray-300 py-8">Loading...</div>
        <div v-else-if="error" class="text-center text-red-400 py-8">{{ error }}</div>
        <div v-else>
          <div v-if="chartData.labels.length">
            <div class="flex flex-col md:flex-row items-start gap-8">
              <div class="flex-1 min-w-0 h-[400px] flex items-center justify-center">
                <Bar :data="chartData" :options="chartOptions" />
              </div>
              <div class="flex flex-col items-start gap-3 mt-6 md:mt-0 min-w-[220px]">
                <div v-for="(color, idx) in chartColors" :key="scheduleTypes[idx]?.work_type_name" class="flex items-center gap-2 mb-1">
                  <span :style="{ backgroundColor: color, width: '28px', height: '12px', display: 'inline-block', borderRadius: '2px', border: 'none', marginRight: '10px' }"></span>
                  <span class="text-base text-white font-sans" style="font-weight: 400; letter-spacing:0.2px;">{{ scheduleTypes[idx]?.work_type_name }}</span>
                </div>
              </div>
            </div>
          </div>
          <div v-if="chartData.labels.length === 0" class="text-center text-gray-300 py-8">No active schedule types found.</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend } from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend)

export default {
  name: 'ShiftsScheduleTypeAnalytics',
  components: { Bar },
  data() {
    return {
      companyId: '',
      loading: false,
      error: null,
      scheduleTypes: []
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
      return {
        labels: [''],
        datasets: this.scheduleTypes.map((s, idx) => ({
          label: s.work_type_name,
          data: [s.count],
          backgroundColor: this.chartColors[idx],
          borderColor: '#222c44',
          borderWidth: 2,
          order: idx
        }))
      };
    },
    chartOptions() {
      return {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            enabled: true,
            mode: 'index',
            intersect: false,
            backgroundColor: 'rgba(30, 41, 59, 0.95)',
            titleColor: '#fff',
            titleFont: {
              family: 'Open Sans',
              size: 16,
              weight: 'bold'
            },
            bodyColor: '#fff',
            bodyFont: {
              family: 'Open Sans',
              size: 15
            },
            padding: 12,
            callbacks: {
              label: ctx => `${ctx.dataset.label}: ${ctx.parsed.y}`
            }
          },
          title: { display: false }
        },
        layout: { padding: { left: 0, right: 0, top: 0, bottom: 0 } },
        scales: {
          x: {
            stacked: true,
            grid: { color: 'rgba(255,255,255,0.08)' },
            ticks: { color: '#fff', font: { family: 'Open Sans', size: 16, weight: 'bold' } }
          },
          y: {
            type: 'logarithmic',
            stacked: true,
            min: 1,
            grid: { color: 'rgba(255,255,255,0.12)' },
            ticks: {
              color: '#fff',
              font: { family: 'Open Sans', size: 16, weight: 'bold' },
              callback: function(value) { return Number(value).toLocaleString(); }
            }
          }
        }
      };
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
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