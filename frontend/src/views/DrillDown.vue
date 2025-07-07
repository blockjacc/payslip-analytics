<template>
  <div class="min-h-screen w-full bg-gradient-to-br from-[#0f2027] via-[#2c5364] to-[#232526] p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">
      drill down<span v-if="filterDisplay"> – {{ filterDisplay }}</span>
    </h1>
    <div v-if="loading" class="text-white">loading...</div>
    <div v-if="error" class="text-red-400">error: {{ error }}</div>
    <div v-if="!loading && !error">
      <div v-if="periods.length > 1 && selectedPeriodIdx === null" class="mb-8">
        <h2 class="text-white text-2xl mb-4">select a period</h2>
        <div class="flex flex-col gap-3">
          <button v-for="(period, idx) in sortedPeriods" :key="idx" @click="selectPeriod(idx)" class="bg-white/10 hover:bg-primary/30 text-white rounded-lg p-4 text-lg font-semibold transition-colors text-left">
            {{ formatDate(period.period.from) }} - {{ formatDate(period.period.to) }}
            <span class="block text-xs mt-2 text-gray-300">{{ period.employees.length }} employees</span>
          </button>
        </div>
      </div>
      <div v-else-if="selectedPeriodIdx !== null || periods.length === 1">
        <div class="flex justify-between items-center mb-6">
          <button v-if="hasPrevPeriod" @click="goToPeriod(selectedPeriodIdx - 1)" class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600">
            &larr; {{ formatDate(prevPeriod.period.from) }} - {{ formatDate(prevPeriod.period.to) }}
          </button>
          <div class="text-white text-xl font-bold">
            {{ formatDate(currentPeriod.period.from) }} - {{ formatDate(currentPeriod.period.to) }}
          </div>
          <button v-if="hasNextPeriod" @click="goToPeriod(selectedPeriodIdx + 1)" class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600">
            {{ formatDate(nextPeriod.period.from) }} - {{ formatDate(nextPeriod.period.to) }} &rarr;
          </button>
        </div>
        <div class="mb-4 flex justify-end">
          <button @click="downloadDrilldownCSV" class="bg-secondary text-white px-4 py-2 rounded font-semibold hover:bg-indigo-600">download csv</button>
        </div>
        <div class="overflow-auto bg-white/5 rounded-lg p-4">
          <div class="text-xs text-gray-400 mb-2">employee count: {{ currentPeriod.employees.length }}</div>
          <table class="min-w-full text-sm text-left">
            <thead>
              <tr class="bg-primary/10 text-white font-bold">
                <th class="p-2">last name</th>
                <th class="p-2">first name</th>
                <th class="p-2">employee id</th>
                <th v-for="field in selectedFields" :key="field" class="p-2">{{ formatLabel(field) }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="emp in sortedEmployees" :key="emp.emp_id" class="text-white">
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
</template>

<script>
export default {
  name: 'DrillDown',
  data() {
    return {
      loading: true,
      error: '',
      result: null,
      selectedPeriodIdx: null,
      selectedFields: [],
      fieldDisplayNames: {}
    }
  },
  computed: {
    locationId() {
      return this.$route.query.location_id || '';
    },
    isAggregate() {
      return this.$route.params.aggregationType === 'aggregate';
    },
    periods() {
      if (this.result && this.result.periods) return this.result.periods;
      if (this.isAggregate && this.result && this.result.employees) {
        return [{
          period: {
            from: this.$route.params.periodFrom,
            to: this.$route.params.periodTo
          },
          employees: this.result.employees
        }];
      }
      return [];
    },
    sortedPeriods() {
      // Sort periods chronologically by from date
      return [...this.periods].sort((a, b) => new Date(a.period.from) - new Date(b.period.from));
    },
    currentPeriod() {
      if (this.isAggregate) {
        return this.periods[0];
      }
      if (this.selectedPeriodIdx !== null && this.periods.length > 0) {
        return this.periods[this.selectedPeriodIdx];
      }
      return null;
    },
    sortedEmployees() {
      if (!this.currentPeriod || !this.currentPeriod.employees) return [];
      // For aggregate, group by emp_id and sum all fields
      if (this.isAggregate) {
        const empMap = {};
        this.currentPeriod.employees.forEach(emp => {
          if (!empMap[emp.emp_id]) {
            empMap[emp.emp_id] = { ...emp };
          } else {
            // Sum all numeric fields
            this.selectedFields.forEach(field => {
              empMap[emp.emp_id][field] = (empMap[emp.emp_id][field] || 0) + (emp[field] || 0);
            });
          }
        });
        // Sort by last name, then first name
        return Object.values(empMap).sort((a, b) => {
          const lastA = (a.last_name || '').toLowerCase();
          const lastB = (b.last_name || '').toLowerCase();
          if (lastA < lastB) return -1;
          if (lastA > lastB) return 1;
          const firstA = (a.first_name || '').toLowerCase();
          const firstB = (b.first_name || '').toLowerCase();
          if (firstA < firstB) return -1;
          if (firstA > firstB) return 1;
          return 0;
        });
      }
      // For separate, just sort as before
      return [...this.currentPeriod.employees].sort((a, b) => {
        const lastA = (a.last_name || '').toLowerCase();
        const lastB = (b.last_name || '').toLowerCase();
        if (lastA < lastB) return -1;
        if (lastA > lastB) return 1;
        const firstA = (a.first_name || '').toLowerCase();
        const firstB = (b.first_name || '').toLowerCase();
        if (firstA < firstB) return -1;
        if (firstA > firstB) return 1;
        return 0;
      });
    },
    hasPrevPeriod() {
      return this.selectedPeriodIdx !== null && this.selectedPeriodIdx > 0;
    },
    hasNextPeriod() {
      return this.selectedPeriodIdx !== null && this.selectedPeriodIdx < this.sortedPeriods.length - 1;
    },
    prevPeriod() {
      if (this.hasPrevPeriod) return this.sortedPeriods[this.selectedPeriodIdx - 1];
      return null;
    },
    nextPeriod() {
      if (this.hasNextPeriod) return this.sortedPeriods[this.selectedPeriodIdx + 1];
      return null;
    },
    filterDisplay() {
      if (this.result && this.result.filters) {
        const filters = this.result.filters;
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
      return '';
    }
  },
  methods: {
    selectPeriod(idx) {
      this.selectedPeriodIdx = idx;
    },
    goToPeriod(idx) {
      this.selectedPeriodIdx = idx;
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
    async fetchFieldDisplayNames() {
      try {
        const response = await fetch('/api/payslip-fields');
        const data = await response.json();
        this.fieldDisplayNames = {
          ...data.amount_fields,
          ...data.hour_fields,
          ...data.tax_fields
        };
      } catch (err) {
        // ignore
      }
    },
    formatLabel(key) {
      if (this.fieldDisplayNames[key]) {
        return this.fieldDisplayNames[key];
      }
      return key;
    },
    downloadDrilldownCSV() {
      if (!this.currentPeriod || !this.currentPeriod.employees) return;
      let csv = 'Last Name,First Name,Employee ID';
      this.selectedFields.forEach(field => {
        csv += ',' + this.formatLabel(field);
      });
      csv += '\n';
      this.sortedEmployees.forEach(emp => {
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
      a.download = `drilldown_${this.$route.params.companyId}_${this.currentPeriod.period.from}_${this.currentPeriod.period.to}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    }
  },
  async mounted() {
    this.loading = true;
    this.error = '';
    try {
      const fields = sessionStorage.getItem('selectedPayslipFields') || '["basic_pay","regular_pay","gross_pay","net_amount"]';
      this.selectedFields = JSON.parse(fields);
      await this.fetchFieldDisplayNames();
      const fieldsParam = encodeURIComponent(fields);
      let url = `/api/analytics-prefetch/${this.$route.params.companyId}/${this.$route.params.periodFrom}/${this.$route.params.periodTo}/${this.$route.params.aggregationType}?fields=${fieldsParam}`;
      Object.entries(this.$route.query).forEach(([key, value]) => {
        url += `&${key}=${value}`;
      });
      url += '&drilldown=true';
      const response = await fetch(url);
      if (!response.ok) throw new Error(await response.text());
      this.result = await response.json();
      // For aggregate, go straight to table; for separate, select first period if only one
      if (this.isAggregate) {
        this.selectedPeriodIdx = 0;
      } else if (this.periods.length === 1) {
        this.selectedPeriodIdx = 0;
      }
    } catch (err) {
      this.error = err.message || err;
    } finally {
      this.loading = false;
    }
  }
}
</script> 