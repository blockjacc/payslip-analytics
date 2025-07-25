<template>
  <div class="p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">payroll analytics</h1>
    <div class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl">employee id: {{ employeeId }}</h3>
          <h3 v-if="payrollGroupId" class="text-primary mb-2 text-xl">payroll group: {{ payrollGroupId }}</h3>
          <h3 v-if="filterDisplay" class="text-primary mb-2 text-xl">{{ filterDisplay }}</h3>
          <h4 class="text-secondary text-lg">period: {{ formatDate(periodFrom) }} - {{ formatDate(periodTo) }}</h4>
        </div>
        <div class="flex justify-end mb-4">
          <button class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500" @click="downloadCSV">download csv</button>
          <button class="ml-4 bg-secondary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-indigo-600" @click="goToDrilldown">drill down</button>
        </div>
        <div class="h-[60vh] mb-12">
          <Bar :data="chartData" :options="chartOptions" />
        </div>
        <div v-if="periods.length > 0" class="mb-8">
          <!-- Removed per-period drill down buttons -->
        </div>
        <div class="mt-8 pt-8 border-t border-white/10 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          <div v-for="(value, key) in salaryData" :key="key" class="flex justify-between items-center p-2 px-4 bg-white/5 rounded-lg" v-if="value > 0">
            <span class="text-sm text-secondary">{{ formatLabel(key) }}:</span>
            <span class="font-sans font-semibold text-white">{{ formatCurrency(value) }}</span>
          </div>
          <div class="col-span-full mt-4 p-4 bg-primary/10 border border-primary/20 rounded-lg">
            <div class="flex justify-between items-center">
              <span class="text-xl font-bold text-primary">total:</span>
              <span class="text-xl font-bold text-primary">{{ formatCurrency(totalSalary) }}</span>
            </div>
          </div>
        </div>
        <!-- Drill-Down Modal/Page -->
        <div v-if="showDrilldown && drilldownPeriodIndex !== null" class="fixed inset-0 z-50 flex items-center justify-center bg-black/60">
          <div class="bg-white rounded-lg shadow-lg w-full max-w-5xl max-h-[90vh] flex flex-col">
            <div class="flex justify-between items-center p-4 border-b border-gray-200">
              <div>
                <span class="font-bold text-lg text-primary">drill down: </span>
                <span class="text-secondary">{{ formatDate(periods[drilldownPeriodIndex].period.from) }} - {{ formatDate(periods[drilldownPeriodIndex].period.to) }}</span>
              </div>
              <button class="text-gray-500 hover:text-red-500 text-2xl font-bold" @click="closeDrilldown">&times;</button>
            </div>
            <div class="flex justify-between items-center p-4 border-b border-gray-100 bg-gray-50">
              <div>
                <button v-if="drilldownPeriodIndex > 0" @click="showDrilldownForPeriod(drilldownPeriodIndex - 1)" class="mr-2 px-3 py-1 bg-primary text-white rounded hover:bg-emerald-600">&larr; previous</button>
                <button v-if="drilldownPeriodIndex < periods.length - 1" @click="showDrilldownForPeriod(drilldownPeriodIndex + 1)" class="px-3 py-1 bg-primary text-white rounded hover:bg-emerald-600">next &rarr;</button>
              </div>
              <button @click="downloadDrilldownCSV(drilldownPeriodIndex)" class="bg-secondary text-white px-4 py-2 rounded font-semibold hover:bg-indigo-600">download csv</button>
            </div>
            <div class="overflow-auto p-4">
              <div v-if="sortedEmployeesForPeriod(drilldownPeriodIndex).length === 0" class="text-center text-gray-500 mb-4">
                no employees found for this period.
              </div>
              <div class="text-xs text-gray-400 mb-2">employee count: {{ sortedEmployeesForPeriod(drilldownPeriodIndex).length }}</div>
              <table class="min-w-full text-sm text-left" v-if="sortedEmployeesForPeriod(drilldownPeriodIndex).length > 0">
                <thead>
                  <tr class="bg-primary/10">
                    <th class="p-2">last name</th>
                    <th class="p-2">first name</th>
                    <th class="p-2">employee id</th>
                    <th v-for="field in selectedFields" :key="field" class="p-2">{{ formatLabel(field) }}</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="emp in sortedEmployeesForPeriod(drilldownPeriodIndex)" :key="emp.emp_id">
                    <td class="p-2">{{ emp.last_name }}</td>
                    <td class="p-2">{{ emp.first_name }}</td>
                    <td class="p-2">{{ emp.emp_id }}</td>
                    <td v-for="field in selectedFields" :key="field" class="p-2">{{ formatCurrency(emp[field]) }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { defineComponent } from 'vue'
import { Bar } from 'vue-chartjs'
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, LogarithmicScale } from 'chart.js'
import { getLogYAxisConfig, getYAxisStartAndFirstTick, getSimpleYAxis, getUnifiedPayslipChart } from '../utils/chartAxis'

ChartJS.register(CategoryScale, LinearScale, LogarithmicScale, BarElement, Title, Tooltip, Legend)

export default defineComponent({
  name: 'Analytics',
  components: { Bar },
  data() {
    return {
      loading: true,
      error: null,
      analyticsPrefetchData: null,
      selectedFields: [],
      fieldDisplayNames: {},
      showDrilldown: false,
      drilldownPeriodIndex: null,
      drilldownEmployees: [],
      baseYAxisMax: 40000,
      // Color mapping from payslip_field_colors.txt
      fieldColors: {
        // Amounts
        basic_pay: '#4a90e2',
        regular_pay: '#24c2ab',
        night_diff: '#f1c40f',
        overtime_pay: '#e74c3c',
        sunday_holiday: '#9b59b6',
        allowances: '#2ecc71',
        nt_allowances: '#e67e22',
        hazard_pay: '#8e44ad',
        cola: '#b1bacd',
        service_charge_taxable: '#c0392b',
        service_charge_non_taxable: '#f39c12',
        bonuses: '#1abc9c',
        other_compensation: '#3498db',
        gross_pay: '#e67e22',
        net_amount: '#16a085',
        de_minimis: '#e84393',
        leave_conversion_taxable: '#fdcb6e',
        leave_conversion_non_taxable: '#00b894',
        paid_leave_amount: '#636e72',
        retroactive_total_amount: '#fd79a8',
        absences: '#00cec9',
        employee_boost_amount: '#6c5ce7',
        tardiness_pay: '#d35400',
        undertime_pay: '#00b894',
        advance_amount: '#fdcb6e',
        // Hours
        regular_days: '#00b894',
        days_absent: '#fdcb6e',
        ot_no_hours: '#e17055',
        retroactive_total_hours: '#00b894',
        employee_total_hours_service_charge_val: '#00cec9',
        // Taxes & Deductions
        pp_sss: '#636e72',
        pp_philhealth: '#00b894',
        pp_pagibig: '#fdcb6e',
        pp_withholding_tax: '#e17055',
        pp_other_deductions: '#e84393',
        voluntary_contributions: '#6c5ce7'
      }
    }
  },
  computed: {
    companyId() {
      return this.$route.params.companyId
    },
    employeeId() {
      return this.$route.params.employeeId
    },
    periodFrom() {
      return this.$route.params.periodFrom
    },
    periodTo() {
      return this.$route.params.periodTo
    },
    payrollGroupId() {
      return this.$route.query.payroll_group_id || sessionStorage.getItem('selectedPayrollGroup') || '';
    },
    filterDisplay() {
      // Use filters object from backend response if available
      if (this.analyticsPrefetchData && this.analyticsPrefetchData.filters) {
        const filters = this.analyticsPrefetchData.filters;
        // Map backend keys to user-friendly labels
        const labelMap = {
          location_name: 'location',
          department_name: 'department',
          rank_name: 'rank',
          employment_type_name: 'employment type',
          position_name: 'position',
          cost_center_code: 'cost center',
          project_name: 'project'
        };
        return Object.entries(filters)
          .filter(([_, v]) => v)
          .map(([k, v]) => `${labelMap[k] || k}: ${v}`)
          .join(' | ');
      }
      // fallback to old logic if needed
      return '';
    },
    periods() {
      return this.analyticsPrefetchData && this.analyticsPrefetchData.periods ? this.analyticsPrefetchData.periods : [];
    },
    summaryTotal() {
      // Support both legacy (total) and new (summary) keys, and fallback to top-level fields
      if (this.analyticsPrefetchData) {
        if (this.analyticsPrefetchData.summary) {
          return this.analyticsPrefetchData.summary;
        }
        if (this.analyticsPrefetchData.total) {
          return this.analyticsPrefetchData.total;
        }
        // Fallback: if top-level fields match selectedFields, use them
        const keys = Object.keys(this.analyticsPrefetchData);
        const fieldKeys = this.selectedFields.filter(f => keys.includes(f));
        if (fieldKeys.length > 0) {
          const result = {};
          fieldKeys.forEach(f => { result[f] = this.analyticsPrefetchData[f]; });
          return result;
        }
      }
      return {};
    },
    chartData() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      // Unified logic: treat aggregate as a single-period 'separate' case
      let periods = [];
      if (aggregationType === 'separate' && this.periods.length) {
        periods = this.periods.map(period => ({
          label: `${this.formatDate(period.period.from)} - ${this.formatDate(period.period.to)}`,
          summary: period.summary
        }));
      } else if (Object.keys(this.summaryTotal).length > 0) {
        // Aggregate or single: treat as one period
        periods = [{
          label: 'Total',
          summary: this.summaryTotal
        }];
      }
      if (periods.length) {
        // Use unified chart configuration with per-period stacking
        const { chartData } = getUnifiedPayslipChart(
          this.selectedFields,
          periods,
          this.formatLabel,
          this.fieldColors,
          { aggregationType, perPeriodStacking: true }
        );
        return chartData;
      } else {
        return { labels: [], datasets: [] };
      }
    },
    salaryData() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      if (aggregationType === 'separate' && this.periods.length) {
        const sums = {};
        this.selectedFields.forEach(field => { sums[field] = 0; });
        this.periods.forEach(period => {
          this.selectedFields.forEach(field => {
            sums[field] += period.summary ? period.summary[field] || 0 : 0;
          });
        });
        return sums;
      } else if (Object.keys(this.summaryTotal).length > 0) {
        const result = {};
        this.selectedFields.forEach(field => {
          result[field] = this.summaryTotal[field] || 0;
        });
        return result;
      } else {
        return {};
      }
    },
    totalSalary() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      if (aggregationType === 'separate' && this.periods.length) {
        return this.selectedFields.reduce((sum, field) => {
          return sum + this.periods.reduce((pSum, period) => pSum + (period.summary ? period.summary[field] || 0 : 0), 0);
        }, 0);
      } else if (Object.keys(this.summaryTotal).length > 0) {
        return this.selectedFields.reduce((sum, field) => sum + (this.summaryTotal[field] || 0), 0);
      } else {
        return 0;
      }
    },
    chartOptions() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      // Unified logic: treat aggregate as a single-period 'separate' case
      let periods = [];
      if (aggregationType === 'separate' && this.periods.length) {
        periods = this.periods.map(period => ({
          label: `${this.formatDate(period.period.from)} - ${this.formatDate(period.period.to)}`,
          summary: period.summary
        }));
      } else if (Object.keys(this.summaryTotal).length > 0) {
        // Aggregate or single: treat as one period
        periods = [{
          label: 'Total',
          summary: this.summaryTotal
        }];
      }
      if (periods.length) {
        // Use unified chart configuration with per-period stacking
        const { chartOptions } = getUnifiedPayslipChart(
          this.selectedFields,
          periods,
          this.formatLabel,
          this.fieldColors,
          { aggregationType, perPeriodStacking: true }
        );
        return chartOptions;
      } else {
        return {};
      }
    }
  },
  methods: {
    async fetchFieldDisplayNames() {
      try {
        const response = await fetch('/api/payslip-fields');
        const data = await response.json();
        
        // Combine all field display names
        this.fieldDisplayNames = {
          ...data.amount_fields,
          ...data.hour_fields,
          ...data.tax_fields
        };
      } catch (err) {
        console.error('Failed to fetch field display names:', err);
      }
    },
    formatLabel(key) {
      // If we have a display name from the backend, use it
      if (this.fieldDisplayNames[key]) {
        return this.fieldDisplayNames[key];
      }
      
      // Otherwise fall back to the hardcoded labels
      const labels = {
        basic: 'Basic Pay',
        nsd: 'Night Differential',
        ot: 'Overtime',
        holiday: 'Holiday Pay',
        paid_leave: 'Paid Leave',
        allowances: 'Allowances',
        deminimis: 'De Minimis',
        bonuses: 'Bonuses',
        other_comp: 'Other Compensation',
        hazard_pay: 'Hazard Pay',
        retro: 'Retro Pay',
        adj: 'Adjustments'
      };
      return labels[key] || key;
    },
    formatDate(dateStr) {
      return new Date(dateStr).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
      })
    },
    formatCurrency(value) {
      return new Intl.NumberFormat('en-US').format(value)
    },
    async fetchAnalyticsPrefetch() {
      this.loading = true;
      this.error = null;
      try {
        const selectedFields = this.selectedFields.length > 0 
          ? this.selectedFields 
          : ['basic_pay', 'regular_pay', 'gross_pay', 'net_amount'];
        const fieldsParam = encodeURIComponent(JSON.stringify(selectedFields));
        let url = `/api/analytics-prefetch/${this.companyId}/${this.periodFrom}/${this.periodTo}/${this.$route.params.aggregationType || 'single'}?fields=${fieldsParam}`;
        if (this.payrollGroupId) {
          url += `&payroll_group_id=${this.payrollGroupId}`;
        }
        if (this.$route.query.department_id) {
          url += `&department_id=${this.$route.query.department_id}`;
        }
        if (this.$route.query.rank_id) {
          url += `&rank_id=${this.$route.query.rank_id}`;
        }
        if (this.$route.query.employment_type_id) {
          url += `&employment_type_id=${this.$route.query.employment_type_id}`;
        }
        if (this.$route.query.position_id) {
          url += `&position_id=${this.$route.query.position_id}`;
        }
        if (this.$route.query.cost_center_id) {
          url += `&cost_center_id=${this.$route.query.cost_center_id}`;
        }
        if (this.$route.query.project_id) {
          url += `&project_id=${this.$route.query.project_id}`;
        }
        if (this.$route.query.location_id) {
          url += `&location_id=${this.$route.query.location_id}`;
        }
        const response = await fetch(url);
        const data = await response.json();
        // Debug log: print the raw backend response
        console.log('[DEBUG] Raw analyticsPrefetchData:', data);
        if (!response.ok) {
          throw new Error(data.error || 'Failed to fetch analytics data');
        }
        if (data.error) {
          throw new Error(data.error);
        }
        this.analyticsPrefetchData = data;
      } catch (err) {
        this.error = err.message;
        this.analyticsPrefetchData = null;
      } finally {
        this.loading = false;
      }
    },
    async showDrilldownForPeriod(idx) {
      this.drilldownPeriodIndex = idx;
      this.showDrilldown = true;
      this.drilldownEmployees = [];
      // Fetch drilldown data for this period
      const period = this.periods[idx];
      if (!period || !period.period) return;
      try {
        const fieldsParam = encodeURIComponent(JSON.stringify(this.selectedFields));
        let url = `/api/analytics-prefetch/${this.companyId}/${period.period.from}/${period.period.to}/separate?fields=${fieldsParam}`;
        if (this.payrollGroupId) {
          url += `&payroll_group_id=${this.payrollGroupId}`;
        }
        if (this.$route.query.department_id) {
          url += `&department_id=${this.$route.query.department_id}`;
        }
        if (this.$route.query.rank_id) {
          url += `&rank_id=${this.$route.query.rank_id}`;
        }
        if (this.$route.query.employment_type_id) {
          url += `&employment_type_id=${this.$route.query.employment_type_id}`;
        }
        if (this.$route.query.position_id) {
          url += `&position_id=${this.$route.query.position_id}`;
        }
        if (this.$route.query.cost_center_id) {
          url += `&cost_center_id=${this.$route.query.cost_center_id}`;
        }
        if (this.$route.query.project_id) {
          url += `&project_id=${this.$route.query.project_id}`;
        }
        if (this.$route.query.location_id) {
          url += `&location_id=${this.$route.query.location_id}`;
        }
        url += `&drilldown=true`;
        const response = await fetch(url);
        const data = await response.json();
        if (data && data.periods && data.periods.length > 0 && data.periods[0].employees) {
          this.drilldownEmployees = data.periods[0].employees;
        } else {
          this.drilldownEmployees = [];
        }
      } catch (err) {
        this.drilldownEmployees = [];
      }
    },
    closeDrilldown() {
      this.showDrilldown = false;
      this.drilldownPeriodIndex = null;
      this.drilldownEmployees = [];
    },
    downloadCSV() {
      const aggregationType = this.$route.params.aggregationType || 'single';
      let csv = '';
      if (aggregationType === 'separate' && this.periods.length) {
        csv += 'Period From,Period To';
        this.selectedFields.forEach(field => {
          csv += ',' + this.formatLabel(field);
        });
        csv += '\n';
        this.periods.forEach(period => {
          csv += `${period.period.from},${period.period.to}`;
          this.selectedFields.forEach(field => {
            csv += ',' + (period.summary ? period.summary[field] : '');
          });
          csv += '\n';
        });
      } else if (Object.keys(this.summaryTotal).length > 0) {
        csv += 'Field,Value\n';
        this.selectedFields.forEach(field => {
          csv += `${this.formatLabel(field)},${this.summaryTotal[field] !== undefined ? this.summaryTotal[field] : ''}\n`;
        });
      }
      // Download logic
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `analytics_${this.companyId}_${this.periodFrom}_${this.periodTo}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    sortedEmployeesForPeriod(idx) {
      if (!this.showDrilldown || !this.drilldownEmployees) return [];
      return [...this.drilldownEmployees].sort((a, b) => {
        const lastA = (a.last_name || '').toLowerCase();
        const lastB = (b.last_name || '').toLowerCase();
        if (lastA < lastB) return -1;
        if (lastA > lastB) return 1;
        // If last names are equal, sort by first name
        const firstA = (a.first_name || '').toLowerCase();
        const firstB = (b.first_name || '').toLowerCase();
        if (firstA < firstB) return -1;
        if (firstA > firstB) return 1;
        return 0;
      });
    },
    downloadDrilldownCSV(idx) {
      if (!this.showDrilldown || !this.drilldownEmployees) return;
      let csv = 'Last Name,First Name,Employee ID';
      this.selectedFields.forEach(field => {
        csv += ',' + this.formatLabel(field);
      });
      csv += '\n';
      this.sortedEmployeesForPeriod(idx).forEach(emp => {
        csv += `${emp.last_name},${emp.first_name},${emp.emp_id}`;
        this.selectedFields.forEach(field => {
          csv += ',' + (emp[field] !== undefined ? emp[field] : '');
        });
        csv += '\n';
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `drilldown_${this.companyId}_${this.periods[idx].period.from}_${this.periods[idx].period.to}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    goToDrilldown() {
      // Build route params and query
      const params = {
        companyId: this.companyId,
        employeeId: this.employeeId,
        periodFrom: this.periodFrom,
        periodTo: this.periodTo,
        aggregationType: this.$route.params.aggregationType || 'single'
      };
      const query = { ...this.$route.query };
      this.$router.push({ name: 'DrillDown', params, query });
    }
  },
  mounted() {
    const storedFields = sessionStorage.getItem('selectedPayslipFields');
    if (storedFields) {
      this.selectedFields = JSON.parse(storedFields);
    } else {
      this.selectedFields = ['basic_pay', 'regular_pay', 'gross_pay', 'net_amount'];
    }
    this.fetchFieldDisplayNames();
    this.fetchAnalyticsPrefetch();
  },
  watch: {
    '$route.params': {
      handler() {
        this.fetchAnalyticsPrefetch();
      },
      deep: true
    },
    '$route.query': {
      handler() {
        this.fetchAnalyticsPrefetch();
      },
      deep: true
    }
  }
})
</script> 