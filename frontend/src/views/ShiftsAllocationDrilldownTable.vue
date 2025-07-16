<template>
  <div class="min-h-screen w-full p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">
      shifts allocation drill down
    </h1>
    <div v-if="loading" class="text-white text-center">loading...</div>
    <div v-if="error" class="text-red-400 text-center">error: {{ error }}</div>
    <div v-if="!loading && !error && drilldownData" class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl">company: {{ companyName || companyId }}</h3>
          <h3 class="text-primary mb-2 text-xl">schedule type: {{ scheduleType }}</h3>
          <h3 class="text-primary mb-2 text-xl">shift: {{ drilldownData.shift_name }}</h3>
          <h4 class="text-secondary text-lg">employee count: {{ drilldownData.employee_count }}</h4>
        </div>
        <!-- Previous/Next Navigation -->
        <div class="flex justify-between items-center mb-6">
          <button v-if="hasPrevShift" @click="goToShiftIdx(currentShiftIdx - 1)" class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600">
            &larr; {{ getShiftName(allShiftIds[currentShiftIdx - 1]) }}
          </button>
          <div class="text-white text-xl font-bold">
            {{ getShiftName(currentShiftId) }}
          </div>
          <button v-if="hasNextShift" @click="goToShiftIdx(currentShiftIdx + 1)" class="px-4 py-2 bg-primary text-white rounded hover:bg-emerald-600">
            {{ getShiftName(allShiftIds[currentShiftIdx + 1]) }} &rarr;
          </button>
        </div>
        <div class="flex justify-end mb-4">
          <button class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500" @click="downloadCSV">download csv</button>
          <button class="ml-4 bg-white/10 text-white border border-white/20 px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-white/20" @click="goBack">back to shift picker</button>
        </div>
        <div class="overflow-auto bg-white/5 rounded-lg p-4">
          <div v-if="drilldownData.employees.length === 0" class="text-center text-gray-500 mb-4">
            no employees found for this shift.
          </div>
          <div v-else>
            <div class="text-xs text-gray-400 mb-2">employee count: {{ drilldownData.employees.length }}</div>
            <table class="min-w-full text-sm text-left">
              <thead>
                <tr class="bg-primary/10 text-white font-bold">
                  <th class="p-2">last name</th>
                  <th class="p-2">first name</th>
                  <th class="p-2">employee id</th>
                  <th class="p-2">location/office</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="emp in sortedEmployees" :key="emp.emp_id" class="text-white border-b border-white/10">
                  <td class="p-2">{{ emp.last_name }}</td>
                  <td class="p-2">{{ emp.first_name }}</td>
                  <td class="p-2">{{ emp.emp_id }}</td>
                  <td class="p-2">{{ emp.location_office }}</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div v-if="allShiftIds.length > 1" class="mt-8 pt-8 border-t border-white/10">
          <h3 class="text-white text-lg mb-4">navigate between shifts:</h3>
          <div class="flex flex-wrap gap-2">
            <button v-for="(shiftId, idx) in allShiftIds" :key="shiftId"
              @click="navigateToShift(shiftId)"
              class="px-4 py-2 text-sm rounded-md transition-colors"
              :class="shiftId === currentShiftId ? 'bg-primary text-white' : 'bg-white/10 text-white hover:bg-white/20'">
              {{ getShiftName(shiftId) }}
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ShiftsAllocationDrilldownTable',
  data() {
    return {
      loading: true,
      error: '',
      companyId: '',
      companyName: '',
      scheduleType: '',
      shiftId: '',
      drilldownData: null,
      allShiftIds: [],
      currentShiftId: null,
      shiftsMeta: []
    }
  },
  created() {
    this.companyId = this.$route.params.companyId;
    this.companyName = sessionStorage.getItem('selectedCompanyName') || '';
    this.scheduleType = this.$route.params.scheduleType;
    this.shiftId = this.$route.params.shiftId;
  },
  computed: {
    sortedEmployees() {
      if (!this.drilldownData || !this.drilldownData.employees) return [];
      return [...this.drilldownData.employees].sort((a, b) => {
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
    currentShiftIdx() {
      return this.allShiftIds.findIndex(id => String(id) === String(this.currentShiftId));
    },
    hasPrevShift() {
      return this.currentShiftIdx > 0;
    },
    hasNextShift() {
      return this.currentShiftIdx < this.allShiftIds.length - 1;
    }
  },
  methods: {
    async fetchDrilldownData() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetch(`/api/shifts/allocation-drilldown/${this.companyId}/${encodeURIComponent(this.scheduleType)}/${this.shiftId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        const data = await response.json();
        if (data.error) throw new Error(data.error);
        this.drilldownData = data;
        this.currentShiftId = this.shiftId;
      } catch (err) {
        this.error = err.message || 'Failed to fetch drilldown data';
        this.drilldownData = null;
      } finally {
        this.loading = false;
      }
    },
    async loadAllShiftIds() {
      this.allShiftIds = this.shiftIds.split(',').map(id => id.trim());
      // Optionally, fetch shift names for navigation
      try {
        const response = await fetch(`/api/shifts/schedules/${this.companyId}/${encodeURIComponent(this.scheduleType)}`);
        if (response.ok) {
          const data = await response.json();
          this.shiftsMeta = (data.schedules || []).filter(s => this.allShiftIds.includes(String(s.work_schedule_id)));
        }
      } catch (err) {
        this.shiftsMeta = [];
      }
    },
    getShiftName(shiftId) {
      const meta = this.shiftsMeta.find(s => String(s.work_schedule_id) === String(shiftId));
      return meta ? meta.name : `Shift ${shiftId}`;
    },
    navigateToShift(shiftId) {
      if (shiftId === this.currentShiftId) return;
      this.$router.push(`/shifts-allocation-drilldown/${this.companyId}/${this.scheduleType}/${this.shiftIds}/${shiftId}`);
    },
    downloadCSV() {
      if (!this.drilldownData || !this.drilldownData.employees) return;
      let csv = 'Last Name,First Name,Employee ID,Location/Office\n';
      this.sortedEmployees.forEach(emp => {
        csv += `${emp.last_name},${emp.first_name},${emp.emp_id},${emp.location_office}\n`;
      });
      const blob = new Blob([csv], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `shifts_allocation_drilldown_${this.companyId}_${this.scheduleType}_${this.shiftId}.csv`;
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    },
    goBack() {
      this.$router.push(`/shifts-allocation-drilldown/${this.companyId}/${this.scheduleType}/${this.shiftIds}`);
    },
    goToShiftIdx(idx) {
      if (idx < 0 || idx >= this.allShiftIds.length) return;
      this.navigateToShift(this.allShiftIds[idx]);
    }
  },
  async mounted() {
    await this.loadAllShiftIds();
    await this.fetchDrilldownData();
  },
  watch: {
    '$route.params.shiftId': {
      handler() {
        this.fetchDrilldownData();
      },
      immediate: true
    }
  }
}
</script> 