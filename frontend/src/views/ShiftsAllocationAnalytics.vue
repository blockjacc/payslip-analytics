<template>
  <div class="p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">shifts allocation analytics</h1>
    <div class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl">company: {{ companyName || companyId }}</h3>
          <h3 class="text-primary mb-2 text-xl">schedule type: {{ scheduleType }}</h3>
          <h4 class="text-secondary text-lg">selected shifts: {{ selectedShiftNames.join(', ') }}</h4>
        </div>
        <div class="flex justify-end mb-4">
          <button class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500" @click="downloadCSV">download csv</button>
          <button 
            class="ml-4 bg-secondary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-indigo-600"
            :disabled="!schedules.length"
            @click="goToDrilldownPicker"
          >
            drill down
          </button>
        </div>
        <div class="h-[60vh] mb-12 flex flex-col items-center justify-center">
          <Bar v-if="chartData && chartData.labels.length" :data="chartData" :options="chartOptions" />
          <div v-else class="text-white mt-6">No data to display.</div>
        </div>
        <div class="mt-8 pt-8 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div v-for="shift in schedules" :key="shift && shift.work_schedule_id" class="flex justify-between items-center p-2 px-4 bg-white/5 rounded-lg" v-if="shift && shift.employee_count > 0">
            <span class="text-sm text-secondary">{{ shift.name }}:</span>
            <span class="font-sans font-semibold text-white">{{ formatNumber(shift.employee_count) }}</span>
          </div>
          <div class="col-span-full mt-4 p-4 bg-primary/10 border border-primary/20 rounded-lg">
            <div class="flex justify-between items-center">
              <span class="text-xl font-bold text-primary">total:</span>
              <span class="text-xl font-bold text-primary">{{ formatNumber(totalEmployees) }}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';
import { getUnifiedStackedBarChart } from '../utils/chartAxis';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const shiftColors = [
  '#38bdf8', '#06b6d4', '#818cf8', '#f472b6', '#facc15', '#4ade80', '#f87171', '#eab308', '#a3e635', '#f472b6'
];

export default defineComponent({
  name: 'ShiftsAllocationAnalytics',
  components: { Bar },
  data() {
    return {
      companyId: '',
      companyName: '',
      scheduleType: '',
      shiftIds: '',
      loading: true,
      schedules: []
    }
  },
  async created() {
    this.companyId = this.$route.params.companyId;
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    this.scheduleType = this.$route.params.scheduleType;
    this.shiftIds = this.$route.params.shiftIds;
    await this.fetchShiftData();
  },
  computed: {
    selectedShiftNames() {
      return this.schedules.map(s => s.name);
    },
    chartData() {
      if (!this.schedules.length) return { labels: [], datasets: [] };
      // Use unified chart configuration for consistent behavior
      const { chartData } = getUnifiedStackedBarChart(
        this.schedules,
        'employee_count',
        'name',
        shiftColors,
        { 
          labels: ['Employees Assigned'],
          chartName: 'Shifts Allocation',
          showLegend: true,
          legendPosition: 'right',
          fontSize: 14,
          fontFamily: 'IBM Plex Mono',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1
        }
      );
      return chartData;
    },
    chartOptions() {
      if (!this.schedules.length) return {};
      // Use unified chart configuration for consistent behavior
      const { chartOptions } = getUnifiedStackedBarChart(
        this.schedules,
        'employee_count',
        'name',
        shiftColors,
        { 
          labels: ['Employees Assigned'],
          chartName: 'Shifts Allocation',
          showLegend: true,
          legendPosition: 'right',
          fontSize: 14,
          fontFamily: 'IBM Plex Mono',
          borderColor: 'rgba(255, 255, 255, 0.1)',
          borderWidth: 1
        }
      );
      
      // Add the onClick handler for drilldown navigation
      chartOptions.onClick = (e, elements, chart) => {
        if (elements.length > 0) {
          const idx = elements[0].datasetIndex;
          const shiftId = this.schedules[idx].work_schedule_id;
          this.goToDrilldown(shiftId);
        }
      };
      
      return chartOptions;
    },
    totalEmployees() {
      return this.schedules.reduce((sum, s) => sum + s.employee_count, 0);
    }
  },
  methods: {
    async fetchShiftData() {
      this.loading = true;
      try {
        const response = await fetch(`/api/shifts/schedules/${this.companyId}/${encodeURIComponent(this.scheduleType)}`);
        if (response.ok) {
          const data = await response.json();
          const selectedIds = this.shiftIds.split(',').map(id => id.trim());
          this.schedules = (data.schedules || []).filter(s => s && selectedIds.includes(String(s.work_schedule_id)));
        } else {
          this.schedules = [];
        }
      } catch (e) {
        this.schedules = [];
      } finally {
        this.loading = false;
      }
    },
    formatNumber(val) {
      return new Intl.NumberFormat('en-US').format(val);
    },
    downloadCSV() {
      let csv = 'Shift,Employees Assigned\n';
      this.schedules.forEach(s => {
        csv += `${s.name},${s.employee_count}\n`;
      });
      csv += `Total,${this.totalEmployees}\n`;
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `shifts_allocation_analytics_${this.companyId}_${this.scheduleType}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    goToDrilldownPicker() {
      if (!this.schedules.length) return;
      const shiftIds = this.schedules.map(s => s.work_schedule_id).join(',');
      this.$router.push(`