<template>
  <div class="min-h-screen w-full p-8">
    <h1 class="font-serif text-white mb-8 text-4xl text-center">
      shifts allocation drill down
    </h1>
    
    <div v-if="loading" class="text-white text-center">loading...</div>
    <div v-if="error" class="text-red-400 text-center">error: {{ error }}</div>
    
    <div v-if="!loading && !error && drilldownData" class="flex justify-center">
      <div class="bg-white/10 rounded-xl p-8 w-full max-w-6xl">
        <!-- Header Information -->
        <div class="text-center mb-8">
          <h3 class="text-primary mb-2 text-2xl">company id: {{ companyId }}</h3>
          <h3 class="text-primary mb-2 text-xl">schedule type: {{ scheduleType }}</h3>
          <h3 class="text-primary mb-2 text-xl">shift: {{ drilldownData.shift_name }}</h3>
          <h4 class="text-secondary text-lg">employee count: {{ drilldownData.employee_count }}</h4>
        </div>

        <!-- Action Buttons -->
        <div class="flex justify-end mb-4">
          <button 
            class="bg-primary text-white border-none px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-emerald-500" 
            @click="downloadCSV"
          >
            download csv
          </button>
          <button 
            class="ml-4 bg-white/10 text-white border border-white/20 px-6 py-2 rounded-md text-base font-semibold cursor-pointer transition-colors hover:bg-white/20" 
            @click="goBack"
          >
            back to analytics
          </button>
        </div>

        <!-- Employee Table -->
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

        <!-- Navigation between shifts (if multiple shifts were selected) -->
        <div v-if="allShiftIds && allShiftIds.length > 1" class="mt-8 pt-8 border-t border-white/10">
          <h3 class="text-white text-lg mb-4">navigate between shifts:</h3>
          <div class="flex flex-wrap gap-2">
            <button 
              v-for="shiftId in allShiftIds" 
              :key="shiftId"
              @click="navigateToShift(shiftId)"
              class="px-4 py-2 text-sm rounded-md transition-colors"
              :class="shiftId === currentShiftId 
                ? 'bg-primary text-white' 
                : 'bg-white/10 text-white hover:bg-white/20'"
            >
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
  name: 'ShiftsAllocationDrilldown',
  data() {
    return {
      loading: true,
      error: '',
      drilldownData: null,
      allShiftIds: [],
      currentShiftId: null
    }
  },
  computed: {
    companyId() {
      return this.$route.params.companyId;
    },
    scheduleType() {
      return this.$route.params.scheduleType;
    },
    shiftId() {
      return this.$route.params.shiftId;
    },
    sortedEmployees() {
      if (!this.drilldownData || !this.drilldownData.employees) return [];
      return [...this.drilldownData.employees].sort((a, b) => {
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
    }
  },
  methods: {
    async fetchDrilldownData() {
      this.loading = true;
      this.error = '';
      try {
        const response = await fetch(`/api/shifts/allocation-drilldown/${this.companyId}/${encodeURIComponent(this.scheduleType)}/${this.shiftId}`);
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }
        const data = await response.json();
        if (data.error) {
          throw new Error(data.error);
        }
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
      // Try to get all shift IDs from the analytics page context
      // This will be used for navigation between shifts if multiple were selected
      try {
        const response = await fetch(`/api/shifts/schedules/${this.companyId}/${encodeURIComponent(this.scheduleType)}`);
        if (response.ok) {
          const data = await response.json();
          this.allShiftIds = data.schedules.map(s => s.work_schedule_id);
        }
      } catch (err) {
        // If we can't load all shifts, just use the current one
        this.allShiftIds = [this.shiftId];
      }
    },
    getShiftName(shiftId) {
      // This would need to be enhanced if we want to show shift names in navigation
      // For now, just show the ID
      return `Shift ${shiftId}`;
    },
    navigateToShift(shiftId) {
      if (shiftId === this.currentShiftId) return;
      this.$router.push(`/shifts-allocation-drilldown/${this.companyId}/${this.scheduleType}/${shiftId}`);
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
      // Go back to the analytics page with the same parameters
      this.$router.push(`/shifts-allocation-analytics/${this.companyId}/${this.scheduleType}/${this.allShiftIds.join(',')}`);
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